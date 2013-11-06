from frame import Frame

class Closure(object):
    def __init__(self, interpret, function, pframe):
        self.interpret = interpret
        self.function = function
        self.pframe = pframe

    def call(self, args):
        assert len(args) == 0
        frame = Frame(self.pframe, self.function)
        return self.interpret(frame)
