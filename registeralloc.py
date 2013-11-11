from structures import Instruction, Phi
import analysis
import itertools

def postorder_dfs(entry):
    output = []
    visited = set()
    def visit(block):
        if block in visited:
            return
        visited.add(block)
        block.succ = analysis.block_jump_targets(block)
        for target in block.succ:
            visit(target)
        output.append(block)
    visit(entry)
    return output


class Interval(object):
    def __init__(self, instruction, start, stop):
        self.instruction = instruction
        self.start = start
        self.stop  = stop

    def extend(self, index):
        self.start = min(self.start, index)
        self.stop  = max(self.stop,  index)

    def __repr__(self):
        return "%r[%i:%i]" % (self.instruction, self.start, self.stop)

def allocate(function):
    intervals = {}
    def update(value, k):
        if value in intervals:
            intervals[value].extend(k)
        else:
            intervals[value] = Interval(value, i, i)
    index = 0
    for block in reversed(postorder_dfs(function[0])):
        block.index = index
        block.provides = set()
        block.sustains = set()
        for i, instruction in enumerate(block, index):
            if instruction.use:
                update(instruction, i)
                block.provides.add(instruction)
            for arg in instruction:
                if isinstance(arg, (Phi, Instruction)):
                    update(arg, i)
                    if not arg in block.provides:
                        update(arg, block.index)
                        block.sustains.add(arg)
        index += len(block)
    done = False
    while not done:
        done = True
        for block in function:
            k = len(block.sustains)
            for target in block.succ:
                new_sustains = target.sustains - block.provides
                block.sustains.update(new_sustains)
                for arg in new_sustains:
                    update(arg, block.index + len(block))
                    update(arg, block.index)
            if k < len(block.sustains):
                done = False

    intervals = intervals.values()
    intervals.sort(key=lambda i: i.start)
    
    active = []
    regc = itertools.count(0)
    freeregs = set()
    def expire_old_intervals(i):
        while len(active) > 0 and active[0].stop <= i:
            interval = active.pop(0)
            freeregs.add(interval.instruction.reg)
#            print '- interval', interval, 'reg = r%r' % interval.instruction.reg
    for interval in intervals:
        expire_old_intervals(interval.start)
        if len(freeregs) == 0:
            reg = regc.next()
        else:
            reg = freeregs.pop()
        interval.instruction.reg = reg
        active.append(interval)
        active.sort(key=lambda i: i.stop)
#        print '+ interval', interval, "reg = r%r" % interval.instruction.reg

    function.registers = regc.next()
    for sub_function in function.functions:
        allocate(sub_function)

#    for interval in intervals:
#        instr = interval.instruction
#        print instr, '>', 'r%i'%instr.reg
#    print "register count:", function.registers
