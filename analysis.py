from structures import Variable

def dominance_frontiers(function):
    def peel(obj, depth):
        for _ in range(depth, obj.idom_depth):
            obj = obj.idom
        return obj
    for block in function:
        block.idom = None
        block.idom_depth = 0
        block.frontiers = set()
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
        block.phi = set()
        if len(block.prec) >= 2:
            for runner in block.prec:
                while runner != block.idom:
                    runner.frontiers.add(block)
                    runner = runner.idom
    def frontier_visit(frontier, var):
        if var in frontier.phi:
            return
        if var in frontier.sustains:
            frontier.phi.add(var)
            for deep_frontier in frontier.frontiers:
                frontier_visit(deep_frontier, var)
    for block in function:
        for var in block.provides:
            for frontier in block.frontiers:
                frontier_visit(frontier, var)
#    done = False
#    while not done:
#        done = True
#        for block in function:
#            phis = block.provides | block.phi
#            for frontier in block.frontiers:
#                k = len(frontier.phi)
#                frontier.phi.update(frontier.sustains & phis)
#                if k < len(frontier.phi):
#                    done = False

def variable_flow(function):
    for block in function:
        provides = set()
        needs = set()
        for instruction in reversed(block):
            args = iter(instruction)
            if instruction.name == 'let':
                var = args.next()
                provides.add(var)
                needs.discard(var)
            needs.update(arg for arg in args if isinstance(arg, Variable))
        block.provides = provides
        block.needs    = needs
        block.sustains = needs.copy()
        block.succ = block_jump_targets(block)
        block.prec = []
    for block in function:
        for target in block.succ:
            target.prec.append(block)
    done = False
    while not done:
        done = True
        for block in function:
            k = len(block.sustains)
            for target in block.succ:
                block.sustains.update(target.sustains - block.provides)
            if k < len(block.sustains):
                done = False

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
