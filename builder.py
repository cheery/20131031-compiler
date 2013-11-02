from instructions import ret

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
    def __init__(self, function, generators, block=None):
        self.function = function
        self.current = self.new_block() if block is None else block
        self.generators = generators
        self.flag = None

    def new_function(self, argv, generator, body):
        function = self.function.function(argv)
        self.generators.append((function, generator, body))
        return function

    def new_block(self):
        return Block(self.function)

    def append(self, instruction):
        self.current.append(instruction)
        return instruction

    def spawn(self, block):
        return self.__class__(self.function, self.generators, block)

    def attach(self, block):
        self.current = block

def build(function, generator, body):
    builder = Builder(function, [])
    for stmt in body:
        generator(builder, stmt)
    builder.append(ret(builder.function.constant(None)))

    for function, generator, body in builder.generators:
        build(function, generator, body)
    return builder.function
