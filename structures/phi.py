from instruction import Instruction

class Phi(object):
    def __init__(self, label, routes=None):
        self.term = False
        self.use  = True
        self.name = 'phi'
        self.label = label
        self.routes = {} if routes is None else routes
        self.uid = Instruction.uid_generator.next()

    def bind(self, src, value):
        self.routes[src] = value

    def repr(self):
        text = "i%i = %s %s " % (self.uid, self.name, self.label)
        text += ' '.join(
            "%r{%r}" % (src, arg)
            for src, arg in self.routes.items())
        return text

    def __repr__(self):
        return "i%i" % (self.uid)

    def __iter__(self):
        return iter(self.routes.values())

    def __getitem__(self, src):
        return self.routes[src]
