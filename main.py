import parser
from builder import build
from instructions import branch, cbranch, call, let, ret
from structures import Variable, Namespace, Function
import analysis
import prune
import builder

class Native(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<native %s>' % self.name

global_module = Namespace({
    'pow': Native('pow'),
})

program = parser.parse_file('input')
dump = builder.build(program, global_module)

print dump.repr()
print

analysis.variable_flow(dump)
analysis.dominance_frontiers(dump)
for block in dump:
    print 'analysis', block, '->', ', '.join(map(repr,block.succ))
    print '  prec     ', block.prec
    print '  idom     ', block.idom
    print '  frontiers', block.frontiers
    print '  phi      ', block.phi
    print '  provide', block.provides
    print '  need   ', block.needs
    print '  sustain', block.sustains
print

result = prune.prune(dump)

print 'after pruning'
print result.repr()
