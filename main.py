import parser
from builder import build
from instructions import branch, cbranch, call, let, ret
from structures import Variable, Namespace, Function
import analysis
import prune
import builder
import registeralloc
import objects
import interpret
import cffi
import operator
import sys

def println(*objs):
    for obj in objs:
        if hasattr(obj, 'to_string'):
            print obj.to_string(),
        else:
            print obj,
    print
    return objects.null

def sub(a, b):
    if isinstance(a, objects.Float) or isinstance(b, objects.Float):
        return objects.Float(a.value - b.value)
    if isinstance(a, objects.Integer) and isinstance(b, objects.Integer):
        return objects.Integer(a.value - b.value)
    raise Exception("cannot subtract %r, %r" % (a, b))

def cmp_op(name, op):
    def _impl(a, b):
        ordinal = (objects.Float, objects.Integer)
        if isinstance(a, ordinal) and isinstance(b, ordinal):
            return objects.true if op(a.value, b.value) else objects.false
        raise Exception("not an ordinal %r, %r" % (a, b))
    return objects.Native(name, _impl)

system_modules = {cffi.module.name:cffi.module}
def import_module(name):
    assert isinstance(name, objects.String)
    if name.value in system_modules:
        print "imported module", name.value
        return system_modules[name.value]
    else:
        raise Exception("complete import not implemented")

global_module = Namespace({
    'println': objects.Native('println', println),
    'sub': objects.Native('sub', sub),
    'lt': cmp_op('lt', operator.lt),
    'gt': cmp_op('gt', operator.gt),
    'le': cmp_op('le', operator.le),
    'ge': cmp_op('ge', operator.ge),
    'ne': cmp_op('ne', operator.ne),
    'eq': cmp_op('eq', operator.eq),
    'false': objects.false,
    'true': objects.true,
    'null': objects.null,
    'import': objects.Native('import', import_module),
})

if len(sys.argv) < 2:
    print "requires input program as an argument"
    print "please take something from the samples directory, or do your own"
    sys.exit(1)

program = parser.parse_file(sys.argv[1])
print program.repr()
dump = builder.build(program, global_module)

print dump.repr()
print

analysis.variable_flow(dump)
analysis.dominance_frontiers(dump)
#for block in dump:
#    print 'analysis', block, '->', ', '.join(map(repr,block.succ))
#    print '  prec     ', block.prec
#    print '  idom     ', block.idom
#    print '  frontiers', block.frontiers
#    print '  phi      ', block.phi
#    print '  provide', block.provides
#    print '  need   ', block.needs
#    print '  sustain', block.sustains
#print

result = prune.prune(dump)
registeralloc.allocate(result)

print 'after pruning'
print result.repr()

print "run the program"
script = objects.Closure(interpret.run, result, None)
script.call(())
