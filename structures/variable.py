class Variable(object):
    def __init__(self, function, name):
        self.function = function
        self.name = name
        self.upscope = False
        self.index = len(function.variables)
        function.variables.append(self)

    def __repr__(self):
        return "%s@%r" % (self.name, self.function)
