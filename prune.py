import analysis
from builder import Builder
from instructions import branch, cbranch, call, let, ret, member
from structures import Namespace, Instruction, Function, Variable, Block, Phi

def prune_argument(arg, env, mapping):
    if isinstance(arg, Function):
        if arg in mapping:
            return mapping[arg]
        res = mapping[arg] = mapping[arg.parent].function(arg.argv)
        def prune_function():
            analysis.variable_flow(arg)
            analysis.dominance_frontiers(arg)
            sub_mapping = mapping.copy()
            sub_mapping['cont'] = []
            prune_block(arg[0], sub_mapping)
            for fn in sub_mapping['cont']:
                fn()
        mapping['cont'].append(prune_function)
        return res
    elif isinstance(arg, Variable):
        if arg.name in env:
            res = env[arg.name]
        elif arg in mapping:
            res = mapping[arg]
        else:
            function = mapping[arg.function]
            res = mapping[arg] = function.bind(arg.name)
        return res
    elif isinstance(arg, Instruction):
        return mapping[arg]
    else:
        return arg


def prune_phi(src, dst):
    for phi in dst.phis:
        phi.bind(src, src.env[phi.label])

def prune_block(source, mapping):
    if source in mapping:
        return mapping[source]
    block = mapping[source] = Block(mapping[source.function])
    block.env = env = {}
    block.phis = []
    if source.idom is not None:
        env.update(mapping[source.idom].env)
        for var in source.phi:
            phi = Phi(var.name)
            block.env[var.name] = phi
            block.append(phi)
            block.phis.append(phi)
    for instruction in source:
        name = instruction.name
        if name == 'let':
            lhs, rhs = instruction
            if lhs.upscope:
                block.append(let(
                    prune_argument(lhs, env, mapping),
                    prune_argument(rhs, env, mapping),
                ))
            else:
                #lhs = prune_argument(lhs, env, mapping)
                rhs = prune_argument(rhs, env, mapping)
                env[lhs.name] = rhs
        elif name == 'cbranch':
            cond, then, end = instruction
            cond = prune_argument(cond, env, mapping)
            then = prune_block(then, mapping)
            end  = prune_block(end, mapping)
            block.append(cbranch(cond, then, end))
            prune_phi(block, then)
            prune_phi(block, end)
        elif name == 'call':
            args = [prune_argument(arg, env, mapping) for arg in instruction]
            res = call(args[0], args[1:])
            block.append(res)
            mapping[instruction] = res
        elif name == 'member':
            arg, name = instruction
            res = member(prune_argument(arg, env, mapping), name)
            block.append(res)
            mapping[instruction] = res
        elif name == 'branch':
            then = prune_block(instruction[0], mapping)
            block.append(branch(then))
            prune_phi(block, then)
        elif name == 'ret':
            arg = prune_argument(instruction[0], env, mapping)
            block.append(ret(arg))
        else:
            raise Exception("cannot reinterpret %s" % name)
    return block

def prune(function):
    out = Function(function.argv)
    mapping = {function: out}
    mapping['cont'] = []
    prune_block(function[0], mapping)
    for fn in mapping['cont']:
        fn()
    return out
