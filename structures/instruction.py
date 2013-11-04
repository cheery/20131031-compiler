import itertools

class Instruction(object):
    uid_generator = itertools.count(1)

    def __init__(self, term, use, name, *args):
        self.term = term
        self.use  = use
        self.name = name
        self.args = args
        self.uid = Instruction.uid_generator.next()

    def __iter__(self):
        return iter(self.args)

    def __getitem__(self, index):
        return self.args[index]

    def repr(self):
        if self.use:
            text = "i%i = %s " % (self.uid, self.name)
        else:
            text = "%s " % self.name
        text += ' '.join(repr(arg) for arg in self)
        return text

    def __repr__(self):
        return "i%i" % (self.uid)
