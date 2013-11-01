class Instruction(object):
    _next_uid = 1
    def __init__(self, term, name, *args):
        self.term = term
        self.name = name
        self.args = args
        self.uid = Instruction._next_uid
        Instruction._next_uid += 1

    def __iter__(self):
        return iter(self.args)

    def repr(self):
        text = "i%i = %s " % (self.uid, self.name)
        text += ' '.join(repr(arg) for arg in self)
        return text

    def __repr__(self):
        return "i%i" % (self.uid)

def branch(target):
    return Instruction(True, 'branch', target)

def cbranch(cond, then, else_):
    assert cond is not None
    return Instruction(True, 'cbranch', cond, then, else_)

def call(callee, args):
    return Instruction(False, 'call', callee, args)

def let(dst, src):
    return Instruction(False, 'let', dst, src)
