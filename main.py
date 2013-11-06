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

def lt(a, b):
    ordinal = (objects.Float, objects.Integer)
    if isinstance(a, ordinal) and isinstance(b, ordinal):
        return objects.true if a.value < b.value else objects.false
    raise Exception("not an ordinal %r, %r" % (a, b))

def gt(a, b):
    ordinal = (objects.Float, objects.Integer)
    if isinstance(a, ordinal) and isinstance(b, ordinal):
        return objects.true if a.value > b.value else objects.false
    raise Exception("not an ordinal %r, %r" % (a, b))

def ffi_library(src, *headers):
    print 'importing C library'
    print 'lib', src
    print 'headers', headers

ffi = objects.Module('ffi', {
    'library': objects.Native('library', ffi_library),
})

system_modules = {ffi.name:ffi}
def import_module(name):
    assert isinstance(name, objects.String)
    if name.value in system_modules:
        print "imported module", name.value
        return system_modules[name.value]
    else:
        raise Exception("complete import not implemented")
    
#class Native(object):
#    def __init__(self, name):
#        self.name = name
#
#    def __repr__(self):
#        return '<native %s>' % self.name

global_module = Namespace({
    'println': objects.Native('println', println),
    'sub': objects.Native('sub', sub),
    'lt': objects.Native('lt', lt),
    'gt': objects.Native('gt', gt),
    'import': objects.Native('import', import_module),
})

program = parser.parse_file('input')
print program.repr()
dump = builder.build(program, global_module)

#print dump.repr()
#print

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
