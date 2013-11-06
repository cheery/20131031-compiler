class Frame(object):
    def __init__(self, parent, function):
        self.parent = parent
        self.function = function
        self.variables = [None for var in function.variables]
