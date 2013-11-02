import parser
from builder import build
from instructions import branch, cbranch, call, let, closure, ret
from function import Namespace, Function

def gen_expr(builder, expr):
    if expr.type == 'identifier':
        var = builder.function.lookup(expr.string)
        assert var is not None, repr(expr.string)
        return var
    if expr.type == 'string':
        return builder.function.constant(expr.string)
    if expr.type == 'number':
        return builder.function.constant(float(expr.string))
    if expr.type == 'call':
        args = [gen_expr(builder, subexpr) for subexpr in expr]
        callee = args.pop(0)
        return builder.append(call(callee, args))
    if expr.type == 'def':
        argv = [arg.string for arg in expr[0]]
        function = builder.new_function(argv, gen_stmt, expr[1:])
        return builder.append(closure(function))
    raise Exception("%s not interpreted" % expr.repr())

def gen_stmt(builder, stmt):
    if stmt.type == 'op' and stmt.string == '=':
        assert stmt[0].type == 'identifier'
        var = builder.function.bind(stmt[0].string)
        return builder.append(let(var, gen_stmt(builder, stmt[1])))
    if stmt.type == 'op' and stmt.string == ':=':
        assert stmt[0].type == 'identifier'
        var = builder.function.lookup(stmt[0].string)
        assert var is not None, repr(expr.string)
        return builder.append(let(var, gen_stmt(builder, stmt[1])))
    if stmt.type == 'if':
        then = builder.new_block()
        end  = builder.new_block()
        cond = gen_expr(builder, stmt[0])
        builder.flag = builder.append(cbranch(cond, then, end))
        b = builder.spawn(then)
        for sub_stmt in stmt[1:]:
            gen_stmt(b, sub_stmt)
        b.append(branch(end))
        builder.attach(end)
        return None
    if stmt.type == 'else':
        then = builder.new_block()
        end  = builder.new_block()
        builder.flag = builder.append(cbranch(builder.flag, end, then))
        b = builder.spawn(then)
        for sub_stmt in stmt:
            gen_stmt(b, sub_stmt)
        b.append(branch(end))
        builder.attach(end)
        return None
    return gen_expr(builder, stmt)

class Native(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<native %s>' % self.name

global_module = Namespace({
    'pow': Native('pow'),
})
dump = Function([], parent=global_module)

program = parser.parse_file('input')
build(dump, gen_stmt, program)

print dump.repr()
