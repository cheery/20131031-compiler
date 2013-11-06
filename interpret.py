from structures import Phi, Instruction, Variable
import objects

def fetch(arg, frame, regs):
    if isinstance(arg, (Phi, Instruction)):
        return regs[arg.reg]
    if isinstance(arg, Variable):
        while frame.function != arg.function:
            frame = frame.parent
        return frame.variables[arg.index]
    return arg

def run(frame):
    block = last = frame.function[0]
    regs = [objects.null for i in range(frame.function.registers)]

    while True:
        for instruction in block:
            name = instruction.name
            if name == 'call':
                args = iter(instruction)
                callee = fetch(args.next(), frame, regs)
                regs[instruction.reg] = callee.call([fetch(arg, frame, regs) for arg in args])
            elif name == 'member':
                val = fetch(instruction[0], frame, regs)
                regs[instruction.reg] = val.getattr(instruction[1])
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
                regs[instruction.reg] = fetch(instruction[last], frame, regs)
            elif name == 'ret':
                return fetch(instruction[0], frame, regs)
            else:
                raise Exception("cannot interpret %s" % instruction.repr())
