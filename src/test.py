import math
import pygame
import sympy as sp
import numpy as np
from lw_math.variable import Variable

# ------------------------------------------------------------
# Small Sketchpad Constraint Solver
#
# You can:
#   - draw points
#   - draw edges
#   - make selected edges equal to each other
#   - make selected angles equal to each other
#   - move points
#   - solve constraints with a general Jacobian solver
#
# No special-case shape solver.
# No "edge equals fixed number" constraint.
# Equal edges are constrained equal to each other.
# Size/energy constraints are only used to prevent collapse.
# ------------------------------------------------------------

WIDTH, HEIGHT = 1300, 850
FPS = 60

POINT_RADIUS = 7
POINT_HIT_RADIUS = 13
EDGE_HIT_RADIUS = 10

ALPHA = 0.12
DAMPING_LAMBDA = 1e-2
MAX_DELTA_PER_ITERATION = 45.0
ANGLE_WEIGHT = 200.0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sketchpad: General Jacobian Constraint Solver")
clock = pygame.time.Clock()

font = pygame.font.SysFont("monospace", 16)
small_font = pygame.font.SysFont("monospace", 14)
big_font = pygame.font.SysFont("monospace", 23)

# ------------------------------------------------------------
# Core symbolic classes.
# ------------------------------------------------------------


class Expression:
    def __init__(self, value):
        if isinstance(value, Variable):
            self.sympy_expr = value.get_symbol()
            self.variable_map = {value.get_symbol(): value}

        elif isinstance(value, Expression):
            self.sympy_expr = value.sympy_expr
            self.variable_map = dict(value.variable_map)

        elif isinstance(value, (int, float, complex)):
            self.sympy_expr = sp.sympify(value)
            self.variable_map = {}

        elif isinstance(value, sp.Basic):
            self.sympy_expr = value
            self.variable_map = {}

        else:
            raise TypeError(f"Cannot create Expression from {type(value).__name__}")

    def _wrap_other(self, other):
        return other if isinstance(other, Expression) else Expression(other)

    def __add__(self, other):
        other = self._wrap_other(other)
        result = Expression(self.sympy_expr + other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = self._wrap_other(other)
        result = Expression(self.sympy_expr - other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __rsub__(self, other):
        return Expression(other) - self

    def __mul__(self, other):
        other = self._wrap_other(other)
        result = Expression(self.sympy_expr * other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        other = self._wrap_other(other)
        result = Expression(self.sympy_expr / other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __pow__(self, other):
        other = self._wrap_other(other)
        result = Expression(self.sympy_expr**other.sympy_expr)
        result.variable_map = self.variable_map | other.variable_map
        return result

    def __neg__(self):
        result = Expression(-self.sympy_expr)
        result.variable_map = dict(self.variable_map)
        return result


class Point:
    def __init__(self, x, y):
        self.x = Variable(x)
        self.y = Variable(y)

    def get_x_variable(self):
        return self.x

    def get_y_variable(self):
        return self.y

    def xy(self):
        return [self.x.get_value(), self.y.get_value()]

    def set_xy(self, x, y):
        self.x.set_value(x)
        self.y.set_value(y)

    def variables(self):
        return [self.x, self.y]


# ------------------------------------------------------------
# Geometry helpers.
# ------------------------------------------------------------


def expr_x(point):
    return Expression(point.get_x_variable())


def expr_y(point):
    return Expression(point.get_y_variable())


def squared_distance_expr(points, edge):
    a_index, b_index = edge
    a = points[a_index]
    b = points[b_index]

    ax = expr_x(a)
    ay = expr_y(a)
    bx = expr_x(b)
    by = expr_y(b)

    return (ax - bx) ** 2 + (ay - by) ** 2


def squared_distance_between_points_expr(points, a_index, b_index):
    a = points[a_index]
    b = points[b_index]

    ax = expr_x(a)
    ay = expr_y(a)
    bx = expr_x(b)
    by = expr_y(b)

    return (ax - bx) ** 2 + (ay - by) ** 2


def current_edge_square(points, edge):
    a_index, b_index = edge
    ax, ay = points[a_index].xy()
    bx, by = points[b_index].xy()

    dx = ax - bx
    dy = ay - by

    return dx * dx + dy * dy


def current_distance(points, edge):
    return math.sqrt(current_edge_square(points, edge))


def angle_cos_expr(points, angle):
    """
    angle = (a, b, c)
    The angle is ABC.
    b is the center.
    """
    a_index, b_index, c_index = angle

    a = points[a_index]
    b = points[b_index]
    c = points[c_index]

    ax = expr_x(a)
    ay = expr_y(a)

    bx = expr_x(b)
    by = expr_y(b)

    cx = expr_x(c)
    cy = expr_y(c)

    ux = ax - bx
    uy = ay - by

    vx = cx - bx
    vy = cy - by

    dot = ux * vx + uy * vy
    u2 = ux * ux + uy * uy
    v2 = vx * vx + vy * vy

    # Small symbolic epsilon avoids division by zero if user makes a tiny edge.
    eps = Expression(1e-9)

    return dot / Expression(
        sp.sqrt((u2.sympy_expr + eps.sympy_expr) * (v2.sympy_expr + eps.sympy_expr))
    )


def current_angle_degrees(points, angle):
    a_index, b_index, c_index = angle

    ax, ay = points[a_index].xy()
    bx, by = points[b_index].xy()
    cx, cy = points[c_index].xy()

    ux = ax - bx
    uy = ay - by

    vx = cx - bx
    vy = cy - by

    dot = ux * vx + uy * vy
    lu = math.hypot(ux, uy)
    lv = math.hypot(vx, vy)

    if lu < 1e-9 or lv < 1e-9:
        return 0.0

    cos_value = max(-1.0, min(1.0, dot / (lu * lv)))
    return math.degrees(math.acos(cos_value))


def distance_point_to_segment(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay

    apx = px - ax
    apy = py - ay

    ab2 = abx * abx + aby * aby

    if ab2 <= 1e-9:
        return math.hypot(px - ax, py - ay)

    t = (apx * abx + apy * aby) / ab2
    t = max(0.0, min(1.0, t))

    closest_x = ax + t * abx
    closest_y = ay + t * aby

    return math.hypot(px - closest_x, py - closest_y)


def nearest_point(points, mouse_pos):
    mx, my = mouse_pos

    best_index = None
    best_dist = POINT_HIT_RADIUS

    for i, point in enumerate(points):
        x, y = point.xy()
        d = math.hypot(mx - x, my - y)

        if d <= best_dist:
            best_dist = d
            best_index = i

    return best_index


def nearest_edge(points, edges, mouse_pos):
    mx, my = mouse_pos

    best_index = None
    best_dist = EDGE_HIT_RADIUS

    for i, edge in enumerate(edges):
        a_index, b_index = edge
        ax, ay = points[a_index].xy()
        bx, by = points[b_index].xy()

        d = distance_point_to_segment(mx, my, ax, ay, bx, by)

        if d <= best_dist:
            best_dist = d
            best_index = i

    return best_index


# ------------------------------------------------------------
# Constraint construction.
# ------------------------------------------------------------


def current_angle_arm_energy(points, angle):
    a_index, b_index, c_index = angle

    e1 = (a_index, b_index)
    e2 = (b_index, c_index)

    return current_edge_square(points, e1) + current_edge_square(points, e2)


def build_constraint_expressions(
    points,
    edges,
    equal_edge_groups,
    equal_angle_groups,
):
    constraints = []

    # --------------------------------------------------------
    # Equal edge groups.
    #
    # If group = [edge0, edge3, edge5], then:
    #
    #   edge0_sq - edge3_sq = 0
    #   edge3_sq - edge5_sq = 0
    #
    # Also preserve total group size to prevent collapse:
    #
    #   edge0_sq + edge3_sq + edge5_sq = original_total
    #
    # This does NOT say each edge equals a fixed number.
    # It only prevents the legal but useless 0=0=0 solution.
    # --------------------------------------------------------

    for group in equal_edge_groups:
        if len(group) < 2:
            continue

        edge_exprs = [
            squared_distance_expr(points, edges[edge_index]) for edge_index in group
        ]

        for i in range(len(edge_exprs) - 1):
            constraints.append(edge_exprs[i] - edge_exprs[i + 1])

        initial_total = 0.0
        total_expr = Expression(0)

        for edge_index, edge_expr in zip(group, edge_exprs):
            initial_total += current_edge_square(points, edges[edge_index])
            total_expr = total_expr + edge_expr

        constraints.append(total_expr - initial_total)

    # --------------------------------------------------------
    # Equal angle groups.
    #
    # angle = (a, b, c), where b is the center.
    #
    # Equal angle means:
    #
    #   cos(angle0) - cos(angle1) = 0
    #
    # The extra arm-energy constraint prevents angle arms from
    # collapsing to zero.
    # --------------------------------------------------------

    for group in equal_angle_groups:
        if len(group) < 2:
            continue

        angle_exprs = [angle_cos_expr(points, angle) for angle in group]

        for i in range(len(angle_exprs) - 1):
            constraints.append((angle_exprs[i] - angle_exprs[i + 1]) * ANGLE_WEIGHT)

        initial_total = 0.0
        total_expr = Expression(0)

        for angle in group:
            a_index, b_index, c_index = angle

            arm1 = squared_distance_between_points_expr(points, a_index, b_index)
            arm2 = squared_distance_between_points_expr(points, b_index, c_index)

            total_expr = total_expr + arm1 + arm2
            initial_total += current_angle_arm_energy(points, angle)

        constraints.append(total_expr - initial_total)

    return constraints


# ------------------------------------------------------------
# Compiled general Jacobian solver.
# ------------------------------------------------------------


class CompiledSketchSolver:
    def __init__(
        self,
        points,
        edges,
        equal_edge_groups,
        equal_angle_groups,
    ):
        self.points = points
        self.edges = edges
        self.equal_edge_groups = equal_edge_groups
        self.equal_angle_groups = equal_angle_groups

        self.variables = self._collect_variables(points)
        self.symbols = [v.get_symbol() for v in self.variables]

        self.constraints = build_constraint_expressions(
            points,
            edges,
            equal_edge_groups,
            equal_angle_groups,
        )

        self.has_constraints = len(self.constraints) > 0 and len(self.variables) > 0

        if not self.has_constraints:
            self.E_expr = None
            self.J_expr = None
            self.E_func = None
            self.J_func = None
            return

        self.E_expr = sp.Matrix([expr.sympy_expr for expr in self.constraints])
        self.J_expr = self.E_expr.jacobian(self.symbols)

        self.E_func = sp.lambdify(self.symbols, self.E_expr, "numpy")
        self.J_func = sp.lambdify(self.symbols, self.J_expr, "numpy")

    def _collect_variables(self, points):
        variables = []

        for point in points:
            variables.extend(point.variables())

        return variables

    def values_array(self):
        return np.array(
            [variable.get_value() for variable in self.variables],
            dtype=float,
        )

    def set_values_array(self, values):
        for variable, value in zip(self.variables, values):
            variable.set_value(float(value))

    def evaluate_E(self, values=None):
        if not self.has_constraints:
            return np.array([], dtype=float)

        if values is None:
            values = self.values_array()

        return np.array(self.E_func(*values), dtype=float).reshape(-1)

    def evaluate_J(self, values=None):
        if not self.has_constraints:
            return np.zeros((0, len(self.variables)), dtype=float)

        if values is None:
            values = self.values_array()

        return np.array(self.J_func(*values), dtype=float)

    def error_norm(self, values=None):
        E = self.evaluate_E(values)
        return float(np.linalg.norm(E))

    def compute_delta(self):
        values = self.values_array()

        E = self.evaluate_E(values)
        J = self.evaluate_J(values)

        JT = J.T

        A = JT @ J + DAMPING_LAMBDA * np.eye(len(values))
        b = -JT @ E

        try:
            delta = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            delta = np.linalg.lstsq(A, b, rcond=None)[0]

        return delta, E, J

    def iteration(self):
        if not self.has_constraints:
            return np.array([]), np.array([]), np.array([]), 0.0, False

        values = self.values_array()

        delta, E_before, J = self.compute_delta()
        before_norm = float(np.linalg.norm(E_before))

        max_abs = float(np.max(np.abs(delta))) if delta.size else 0.0

        clamp_scale = 1.0
        if max_abs > MAX_DELTA_PER_ITERATION:
            clamp_scale = MAX_DELTA_PER_ITERATION / max_abs

        chosen_scale = 0.0
        accepted = False

        for shrink in [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]:
            step_scale = clamp_scale * shrink
            candidate = values + ALPHA * step_scale * delta
            after_norm = self.error_norm(candidate)

            if after_norm <= before_norm:
                self.set_values_array(candidate)
                chosen_scale = step_scale
                accepted = True
                break

        return E_before, J, delta, chosen_scale, accepted


# ------------------------------------------------------------
# UI helpers.
# ------------------------------------------------------------


def draw_text(text, x, y, color=(230, 230, 230), fnt=font):
    surf = fnt.render(text, True, color)
    screen.blit(surf, (x, y))


class Button:
    def __init__(self, text, action, x, y, w, h):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, active=False):
        if active:
            color = (70, 110, 160)
        else:
            color = (48, 50, 58)

        pygame.draw.rect(screen, color, self.rect, border_radius=7)
        pygame.draw.rect(screen, (130, 135, 150), self.rect, 1, border_radius=7)

        label = font.render(self.text, True, (240, 240, 240))
        screen.blit(
            label,
            (
                self.rect.x + 10,
                self.rect.y + self.rect.height // 2 - label.get_height() // 2,
            ),
        )

    def contains(self, pos):
        return self.rect.collidepoint(pos)


def make_buttons():
    x = 18
    y = 15
    h = 34
    gap = 8

    specs = [
        ("POINT", "mode_point", 86),
        ("EDGE", "mode_edge", 76),
        ("MOVE", "mode_move", 76),
        ("EQ EDGE", "mode_equal_edge", 105),
        ("EQ ANGLE", "mode_equal_angle", 115),
        ("COMMIT", "commit", 92),
        ("SOLVE", "solve", 82),
        ("CLEAR SEL", "clear_selection", 112),
        ("CLEAR ALL", "clear_all", 108),
    ]

    buttons = []

    for text, action, w in specs:
        buttons.append(Button(text, action, x, y, w, h))
        x += w + gap

    return buttons


def draw_angle_marker(points, angle, color, label=None):
    a_index, b_index, c_index = angle

    ax, ay = points[a_index].xy()
    bx, by = points[b_index].xy()
    cx, cy = points[c_index].xy()

    def point_on_ray(px, py):
        dx = px - bx
        dy = py - by
        length = math.hypot(dx, dy)

        if length < 1e-9:
            return bx, by

        scale = 32.0 / length
        return bx + dx * scale, by + dy * scale

    p1 = point_on_ray(ax, ay)
    p2 = point_on_ray(cx, cy)

    pygame.draw.line(screen, color, (bx, by), p1, 3)
    pygame.draw.line(screen, color, (bx, by), p2, 3)
    pygame.draw.circle(screen, color, (int(bx), int(by)), 5)

    if label:
        draw_text(label, bx + 10, by + 10, color, small_font)


def draw_scene(
    points,
    edges,
    equal_edge_groups,
    equal_angle_groups,
    pending_edge_group,
    pending_angle_group,
    current_edge_start,
    angle_point_buffer,
    selected_point,
    mode,
):
    # Draw committed edge equality groups with different simple colors.
    group_colors = [
        (255, 190, 90),
        (180, 240, 150),
        (240, 140, 220),
        (130, 210, 255),
        (255, 120, 120),
    ]

    edge_to_group_color = {}

    for group_index, group in enumerate(equal_edge_groups):
        color = group_colors[group_index % len(group_colors)]

        for edge_index in group:
            edge_to_group_color[edge_index] = color

    # Draw edges.
    for i, edge in enumerate(edges):
        a_index, b_index = edge
        ax, ay = points[a_index].xy()
        bx, by = points[b_index].xy()

        color = edge_to_group_color.get(i, (120, 170, 230))
        width = 4 if i in edge_to_group_color else 2

        if i in pending_edge_group:
            color = (255, 255, 100)
            width = 5

        pygame.draw.line(screen, color, (ax, ay), (bx, by), width)

        mx = (ax + bx) / 2
        my = (ay + by) / 2
        draw_text(str(i), mx + 4, my + 4, color, small_font)

    # Draw committed angle groups.
    for group_index, group in enumerate(equal_angle_groups):
        color = group_colors[group_index % len(group_colors)]

        for angle_index, angle in enumerate(group):
            draw_angle_marker(
                points,
                angle,
                color,
                label=f"A{group_index}.{angle_index}",
            )

    # Draw pending angles.
    for i, angle in enumerate(pending_angle_group):
        draw_angle_marker(
            points,
            angle,
            (255, 255, 100),
            label=f"pending {i}",
        )

    # Draw temporary line when creating edge.
    if current_edge_start is not None:
        mx, my = pygame.mouse.get_pos()
        sx, sy = points[current_edge_start].xy()
        pygame.draw.line(screen, (255, 255, 100), (sx, sy), (mx, my), 2)

    # Draw points.
    for i, point in enumerate(points):
        x, y = point.xy()

        color = (235, 235, 235)

        if i == selected_point:
            color = (255, 255, 120)

        if i == current_edge_start:
            color = (255, 255, 120)

        if i in angle_point_buffer:
            color = (255, 160, 80)

        pygame.draw.circle(screen, color, (int(x), int(y)), POINT_RADIUS)
        pygame.draw.circle(screen, (20, 20, 24), (int(x), int(y)), POINT_RADIUS, 1)
        draw_text(str(i), x + 9, y - 15, color, small_font)


def draw_info(
    mode,
    points,
    edges,
    equal_edge_groups,
    equal_angle_groups,
    pending_edge_group,
    pending_angle_group,
    angle_point_buffer,
    running,
    iteration,
    last_error_norm,
    last_scale,
    accepted,
    solver,
    message,
):
    y = 64
    x = 18

    draw_text("Sketchpad Constraint Solver", x, y, (255, 255, 255), big_font)
    y += 34

    draw_text(
        f"mode: {mode}    running: {running}    iteration: {iteration}",
        x,
        y,
        (180, 220, 255),
    )
    y += 24

    constraint_count = 0
    if solver is not None and solver.has_constraints:
        constraint_count = solver.E_expr.rows

    current_error = 0.0
    if solver is not None and solver.has_constraints:
        current_error = solver.error_norm()

    draw_text(
        f"points: {len(points)}    edges: {len(edges)}    edge groups: {len(equal_edge_groups)}    angle groups: {len(equal_angle_groups)}",
        x,
        y,
        (230, 230, 230),
    )
    y += 22

    draw_text(
        f"compiled constraints: {constraint_count}    ||E||: {current_error:.3f}    last ||E||: {last_error_norm:.3f}    step: {last_scale:.4f}    accepted: {accepted}",
        x,
        y,
        (255, 220, 160),
    )
    y += 28

    draw_text(
        f"pending edge equality group: {pending_edge_group}",
        x,
        y,
        (255, 255, 120),
    )
    y += 22

    draw_text(
        f"pending angle equality group size: {len(pending_angle_group)}    angle click buffer: {angle_point_buffer}",
        x,
        y,
        (255, 190, 120),
    )
    y += 28

    draw_text(
        message,
        x,
        y,
        (170, 240, 180),
    )

    # Right-side instructions.
    x = WIDTH - 470
    y = 65

    lines = [
        "How to use:",
        "POINT: click empty space to add point",
        "EDGE: click point A, then point B",
        "MOVE: drag a point",
        "EQ EDGE: click edges, ENTER to commit",
        "EQ ANGLE: click 3 points A-B-C. B is center.",
        "          create 2+ angles, ENTER to commit",
        "SOLVE or S: run several iterations",
        "SPACE: continuous solving",
        "N: one solver iteration",
        "BACKSPACE: undo last point/edge/angle selection",
        "ESC: quit",
    ]

    for line in lines:
        draw_text(line, x, y, (220, 220, 220), small_font)
        y += 20


# ------------------------------------------------------------
# Main app.
# ------------------------------------------------------------


def main():
    Variable._counter = 0

    points = []
    edges = []

    equal_edge_groups = []
    equal_angle_groups = []

    pending_edge_group = []
    pending_angle_group = []

    current_edge_start = None
    angle_point_buffer = []

    mode = "POINT"

    selected_point = None
    dragging_point = None

    solver = None
    solver_dirty = True

    running = False
    iteration = 0
    last_error_norm = 0.0
    last_scale = 0.0
    accepted = False

    message = "Draw something, add constraints, then press SOLVE."

    buttons = make_buttons()

    def set_mode(new_mode):
        nonlocal mode
        nonlocal current_edge_start
        nonlocal angle_point_buffer
        nonlocal message

        mode = new_mode
        current_edge_start = None
        angle_point_buffer = []

        message = f"Mode changed to {mode}."

    def clear_selection():
        nonlocal pending_edge_group
        nonlocal pending_angle_group
        nonlocal current_edge_start
        nonlocal angle_point_buffer
        nonlocal message

        pending_edge_group = []
        pending_angle_group = []
        current_edge_start = None
        angle_point_buffer = []
        message = "Selection cleared."

    def commit_selection():
        nonlocal pending_edge_group
        nonlocal pending_angle_group
        nonlocal equal_edge_groups
        nonlocal equal_angle_groups
        nonlocal solver_dirty
        nonlocal message

        did_commit = False

        if len(pending_edge_group) >= 2:
            equal_edge_groups.append(list(pending_edge_group))
            pending_edge_group = []
            solver_dirty = True
            did_commit = True
            message = "Committed equal-edge group."

        if len(pending_angle_group) >= 2:
            equal_angle_groups.append(list(pending_angle_group))
            pending_angle_group = []
            solver_dirty = True
            did_commit = True
            message = "Committed equal-angle group."

        if not did_commit:
            message = "Nothing committed. Need at least 2 edges or 2 angles."

    def clear_all():
        nonlocal points
        nonlocal edges
        nonlocal equal_edge_groups
        nonlocal equal_angle_groups
        nonlocal pending_edge_group
        nonlocal pending_angle_group
        nonlocal current_edge_start
        nonlocal angle_point_buffer
        nonlocal selected_point
        nonlocal dragging_point
        nonlocal solver
        nonlocal solver_dirty
        nonlocal running
        nonlocal iteration
        nonlocal message

        Variable._counter = 0

        points = []
        edges = []
        equal_edge_groups = []
        equal_angle_groups = []
        pending_edge_group = []
        pending_angle_group = []
        current_edge_start = None
        angle_point_buffer = []
        selected_point = None
        dragging_point = None
        solver = None
        solver_dirty = True
        running = False
        iteration = 0
        message = "Cleared all."

    def compile_solver_if_needed():
        nonlocal solver
        nonlocal solver_dirty
        nonlocal message

        if not solver_dirty and solver is not None:
            return solver

        solver = CompiledSketchSolver(
            points,
            edges,
            equal_edge_groups,
            equal_angle_groups,
        )

        solver_dirty = False

        if not solver.has_constraints:
            message = "No committed constraints yet."
        else:
            message = f"Compiled solver with {solver.E_expr.rows} constraints."

        return solver

    def one_iteration():
        nonlocal solver
        nonlocal iteration
        nonlocal last_error_norm
        nonlocal last_scale
        nonlocal accepted
        nonlocal message

        solver = compile_solver_if_needed()

        if solver is None or not solver.has_constraints:
            message = "No constraints to solve."
            return

        E, J, delta, last_scale, accepted = solver.iteration()
        last_error_norm = float(np.linalg.norm(E)) if E.size else 0.0
        iteration += 1

        message = "Solver iteration done."

    def run_solve_batch():
        nonlocal running
        nonlocal message

        solver = compile_solver_if_needed()

        if solver is None or not solver.has_constraints:
            message = "No constraints to solve."
            return

        running = True
        message = "Animated solving started. Press SPACE to pause."

    alive = True

    while alive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                alive = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    alive = False

                elif event.key == pygame.K_p:
                    set_mode("POINT")

                elif event.key == pygame.K_e:
                    set_mode("EDGE")

                elif event.key == pygame.K_m:
                    set_mode("MOVE")

                elif event.key == pygame.K_l:
                    set_mode("EQ_EDGE")

                elif event.key == pygame.K_a:
                    set_mode("EQ_ANGLE")

                elif event.key == pygame.K_RETURN:
                    commit_selection()

                elif event.key == pygame.K_s:
                    run_solve_batch()

                elif event.key == pygame.K_SPACE:
                    running = not running
                    compile_solver_if_needed()

                elif event.key == pygame.K_n:
                    one_iteration()

                elif event.key == pygame.K_BACKSPACE:
                    if mode == "EQ_EDGE" and pending_edge_group:
                        pending_edge_group.pop()
                        message = "Removed last pending edge."
                    elif mode == "EQ_ANGLE" and angle_point_buffer:
                        angle_point_buffer.pop()
                        message = "Removed last angle point click."
                    elif mode == "EQ_ANGLE" and pending_angle_group:
                        pending_angle_group.pop()
                        message = "Removed last pending angle."

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                clicked_button = False

                for button in buttons:
                    if button.contains(mouse_pos):
                        clicked_button = True

                        if button.action == "mode_point":
                            set_mode("POINT")
                        elif button.action == "mode_edge":
                            set_mode("EDGE")
                        elif button.action == "mode_move":
                            set_mode("MOVE")
                        elif button.action == "mode_equal_edge":
                            set_mode("EQ_EDGE")
                        elif button.action == "mode_equal_angle":
                            set_mode("EQ_ANGLE")
                        elif button.action == "commit":
                            commit_selection()
                        elif button.action == "solve":
                            run_solve_batch()
                        elif button.action == "clear_selection":
                            clear_selection()
                        elif button.action == "clear_all":
                            clear_all()

                        break

                if clicked_button:
                    continue

                if mouse_pos[1] < 55:
                    continue

                p_index = nearest_point(points, mouse_pos)

                if mode == "POINT":
                    if p_index is None:
                        points.append(Point(mouse_pos[0], mouse_pos[1]))
                        solver_dirty = True
                        message = f"Added point {len(points) - 1}."
                    else:
                        selected_point = p_index
                        message = f"Selected point {p_index}."

                elif mode == "MOVE":
                    if p_index is not None:
                        dragging_point = p_index
                        selected_point = p_index
                        running = False
                        solver_dirty = True
                        message = f"Dragging point {p_index}."

                elif mode == "EDGE":
                    if p_index is None:
                        message = "EDGE mode: click existing points."
                    else:
                        if current_edge_start is None:
                            current_edge_start = p_index
                            selected_point = p_index
                            message = f"Edge start: point {p_index}."
                        else:
                            a = current_edge_start
                            b = p_index

                            if a == b:
                                message = "Cannot create edge from point to itself."
                            elif (a, b) in edges or (b, a) in edges:
                                message = "That edge already exists."
                            else:
                                edges.append((a, b))
                                solver_dirty = True
                                message = f"Created edge {len(edges) - 1}: {a}-{b}."

                            current_edge_start = None

                elif mode == "EQ_EDGE":
                    edge_index = nearest_edge(points, edges, mouse_pos)

                    if edge_index is None:
                        message = "EQ_EDGE mode: click a drawn edge."
                    else:
                        if edge_index in pending_edge_group:
                            pending_edge_group.remove(edge_index)
                            message = f"Removed edge {edge_index} from pending group."
                        else:
                            pending_edge_group.append(edge_index)
                            message = f"Added edge {edge_index} to pending group."

                elif mode == "EQ_ANGLE":
                    if p_index is None:
                        message = "EQ_ANGLE mode: click points A-B-C. B is center."
                    else:
                        angle_point_buffer.append(p_index)

                        if len(angle_point_buffer) == 3:
                            a, b, c = angle_point_buffer

                            if a == b or b == c or a == c:
                                message = "Angle needs 3 different points."
                            else:
                                pending_angle_group.append((a, b, c))
                                message = f"Added pending angle ({a}, {b}, {c})."

                            angle_point_buffer = []

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_point = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_point is not None:
                    x, y = event.pos
                    points[dragging_point].set_xy(x, y)
                    solver_dirty = True

        if running:
            # One solver step per frame.
            # This makes the solving visible/interactively animated.
            one_iteration()

            if solver is not None and solver.has_constraints:
                if solver.error_norm() < 0.01:
                    running = False
                    message = "Solved. Constraint error is very small."

        screen.fill((25, 26, 32))

        for button in buttons:
            active = False

            if button.action == "mode_point" and mode == "POINT":
                active = True
            elif button.action == "mode_edge" and mode == "EDGE":
                active = True
            elif button.action == "mode_move" and mode == "MOVE":
                active = True
            elif button.action == "mode_equal_edge" and mode == "EQ_EDGE":
                active = True
            elif button.action == "mode_equal_angle" and mode == "EQ_ANGLE":
                active = True

            button.draw(active)

        draw_scene(
            points,
            edges,
            equal_edge_groups,
            equal_angle_groups,
            pending_edge_group,
            pending_angle_group,
            current_edge_start,
            angle_point_buffer,
            selected_point,
            mode,
        )

        draw_info(
            mode,
            points,
            edges,
            equal_edge_groups,
            equal_angle_groups,
            pending_edge_group,
            pending_angle_group,
            angle_point_buffer,
            running,
            iteration,
            last_error_norm,
            last_scale,
            accepted,
            solver,
            message,
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
