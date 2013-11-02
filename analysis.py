from function import Variable

def dominance_frontiers(function):
    def peel(obj, depth):
        for _ in range(depth, obj.idom_depth):
            obj = obj.idom
        return obj
    for block in function:
        block.prec = []
        block.succ = block_jump_targets(block)
        block.idom = None
        block.idom_depth = 0
        block.frontiers = set()
    for block in function:
        for target in block.succ:
            target.prec.append(block)
    assert len(function[0].prec) == 0
    breath = [function[0]]
    while len(breath) > 0:
        block = breath.pop(0)
        for target in block.succ:
            idom = target
            if target.idom is None:
                idom = block
                breath.append(target)
            else:
                depth = min(target.idom_depth, block.idom_depth)
                idom = peel(target, depth)
                cdom = peel(block, depth)
                while idom is not cdom:
                    idom = idom.idom
                    cdom = cdom.idom
            if target is not idom:
                target.idom = idom
                target.idom_depth = idom.idom_depth + 1
    for block in function:
        if len(block.prec) >= 2:
            for runner in block.prec:
                while runner != block.idom:
                    runner.frontiers.add(block)
                    runner = runner.idom

def variable_flow(function):
    for block in function:
        provides = set()
        needs = set()
        for which, var in local_reversed_variable_flow(block):
            if which == 'get':
                needs.add(var)
            if which == 'let':
                provides.add(var)
                needs.discard(var)
        block.provides = provides
        block.needs    = needs
        block.sustains = needs.copy()
    done = False
    while not done:
        done = True
        for block in function:
            k = len(block.sustains)
            for target in block_jump_targets(block):
                block.sustains.update(target.sustains - block.provides)
            if k < len(block.sustains):
                done = False

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

def block_jump_targets(block):
    instruction = block[-1]
    if instruction.name == 'branch':
        return (instruction[0],)
    elif instruction.name == 'cbranch':
        return (instruction[1], instruction[2])
    elif instruction.name == 'ret':
        return ()
    else:
        raise Exception("unknown terminator: %s" % instruction.repr())
