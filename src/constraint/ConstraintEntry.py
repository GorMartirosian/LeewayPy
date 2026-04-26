class ConstraintEntry:
    def __init__(self, constraint, objects):
        self.constraint = constraint
        self.objects = objects
    
    def __repr__(self):
        return f"ConstraintEntry({self.constraint}, {self.objects})"

    def get_objects(self):
        return self.objects

    def get_constraint(self):
        return self.constraint