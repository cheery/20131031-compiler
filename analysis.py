from function import Variable

def local_reversed_variable_flow(block):
    for instruction in block.reversed():
        if instruction.name == 'let':
            yield 'let', instruction[0]
            args = instruction[1:]
        else:
            args = instruction
        for arg in args:
            if isinstance(arg, Variable):
                yield 'get', arg
