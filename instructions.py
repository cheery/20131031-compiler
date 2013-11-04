from structures import Instruction, Variable

#def inc_getc(arg):
#    if isinstance(arg, Variable):
#        arg.getc += 1
#
#def inc_getc_list(args):
#    for arg in args:
#        inc_getc(arg)

def ret(argument):
#    inc_getc(argument)
    return Instruction(True, False, 'ret', argument)

def branch(target):
    return Instruction(True, False, 'branch', target)

def cbranch(cond, then, else_):
    assert cond is not None
#    inc_getc(cond)
    return Instruction(True, False, 'cbranch', cond, then, else_)

def call(callee, args):
#    inc_getc(callee)
#    inc_getc_list(args)
    return Instruction(False, True, 'call', callee, *args)

def let(dst, src):
#    dst.letc += 1
#    inc_getc(src)
    return Instruction(False, False, 'let', dst, src)
