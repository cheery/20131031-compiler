from structures import Phi, Instruction, Variable, Function
import objects

def fetch(arg, frame, regs):
    if isinstance(arg, (Phi, Instruction)):
        return regs[arg.reg]
    if isinstance(arg, Variable):
        while frame.function != arg.function:
            frame = frame.parent
        return frame.variables[arg.index]
    if isinstance(arg, Function):
        if arg in frame.closures:
            res = frame.closures[arg]
        else:
            res = frame.closures[arg] = objects.Closure(run, arg, frame)
        return res
    return arg

def store(var, frame, arg):
    while frame.function != var.function:
        frame = frame.parent
    frame.variables[var.index] = arg

def run(frame):
    block = last = frame.function[0]
    regs = [objects.null for i in range(frame.function.registers)]

    while True:
        for instruction in block:
            name = instruction.name
            if name == 'let':
                arg = fetch(instruction[1], frame, regs)
                store(instruction[0], frame, arg)
            elif name == 'call':
                args = iter(instruction)
                callee = fetch(args.next(), frame, regs)
#                print "r%r" % instruction.reg, instruction.repr()
#                print "callee", callee
                regs[instruction.reg] = callee.call([fetch(arg, frame, regs) for arg in args])
            elif name == 'member':
                val = fetch(instruction[0], frame, regs)
                regs[instruction.reg] = val.getattr(instruction[1])
#                print "r%r" % instruction.reg, instruction.repr()
            elif name == 'branch':
                last = block
                block = instruction[0]
                break
            elif name == 'cbranch':
                last = block
                cond = fetch(instruction[0], frame, regs)
                if objects.is_true(cond):
                    block = instruction[1]
                else:
                    block = instruction[2]
                break
            elif name == 'phi':
#                print "r%r" % instruction.reg, instruction.repr()
                regs[instruction.reg] = fetch(instruction[last], frame, regs)
            elif name == 'ret':
                return fetch(instruction[0], frame, regs)
            else:
                raise Exception("cannot interpret %s" % instruction.repr())
