class Variable(object):
    def __init__(self, function, name):
        self.function = function
        self.name = name
        self.upscope = False

    def __repr__(self):
        return "%s@%r" % (self.name, self.function)
