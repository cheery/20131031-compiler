from frame import Frame

class Closure(object):
    def __init__(self, interpret, function, pframe):
        self.interpret = interpret
        self.function = function
        self.pframe = pframe

    def call(self, args):
        assert len(args) == len(self.function.argvars)
        frame = Frame(self.pframe, self.function)
        for var, arg in zip(self.function.argvars, args):
            frame.variables[var.index] = arg
        return self.interpret(frame)
