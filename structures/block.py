import itertools

class Block(object):
    uid_generator = itertools.count(1)

    def __init__(self, function):
        self.function = function
        self.instructions = []
        self.uid = Block.uid_generator.next()
        function.append(self)

    def __getitem__(self, index):
        return self.instructions[index]

    def __iter__(self):
        return iter(self.instructions)

    def __len__(self):
        return len(self.instructions)

    def __reversed__(self):
        return reversed(self.instructions)

    def append(self, instruction):
        self.instructions.append(instruction)

    def __repr__(self):
        return "b%i" % self.uid

    def repr(self):
        text = "%r:\n" % self
        text += '\n'.join(instr.repr() for instr in self)
        return text.replace('\n', '\n    ')
