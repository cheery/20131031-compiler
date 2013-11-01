class Block(object):
    _next_uid = 1
    def __init__(self, function):
        self.function = function
        function.append(self)
        self.uid = Block._next_uid
        Block._next_uid += 1
        self.instructions = []

    def __iter__(self):
        return iter(self.instructions)

    def append(self, instruction):
        self.instructions.append(instruction)

    def repr(self):
        text = "b%i:\n" % self.uid
        text += '\n'.join(instr.repr() for instr in self)
        return text.replace('\n', '\n    ')

    def __repr__(self):
        return "b%i" % self.uid

class Builder(object):
    def __init__(self, function, block=None):
        self.function = function
        self.current = self.new_block() if block is None else block
        self.flag = None

    def new_block(self):
        return Block(self.function)

    def append(self, instruction):
        self.current.append(instruction)
        return instruction

    def spawn(self, block):
        return self.__class__(self.function, block)

    def attach(self, block):
        self.current = block
