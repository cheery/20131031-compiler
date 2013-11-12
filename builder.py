from instructions import ret, branch, cbranch, call, let, member
from structures import Block, Function, Variable
import objects

class Builder(object):
    def __init__(self, function, block, cont=None):
        self.function = function
        self.current = block
        self.cont = [] if cont is None else cont
        self.flag = None
        self.suspend = False

    def new_function(self, argv, body):
        function = self.function.function(argv)
        def cnt():
            builder = Builder(function, Block(function))
            for stmt in body:
                builder.stmt(stmt)
            builder.append(ret(objects.null))
            for fn in builder.cont:
                fn()
        self.cont.append(cnt)
        return function

    def new_block(self):
        return Block(self.function)

    def append(self, instruction):
        if not self.suspend:
            self.current.append(instruction)
            self.suspend |= instruction.term
        return instruction

    def spawn(self, block):
        return self.__class__(self.function, block, self.cont)

    def attach(self, block):
        self.current = block
        self.suspend = False

    def expr(self, expr):
        if expr.type == 'identifier':
            var = self.function.lookup(expr.string)
            assert var is not None, repr(expr.string)
            return var
        if expr.type == 'string':
            return objects.String(expr.string)
        if expr.type == 'number':
            if "." in expr.string:
                return objects.Float(float(expr.string))
            elif expr.string.startswith('0x'):
                return objects.Integer(int(expr.string, 16))
            else:
                return objects.Integer(int(expr.string))
        if expr.type == 'member':
            arg = self.expr(expr[0])
            return self.append(member(arg, expr.string))
        if expr.type == 'call':
            args = [self.expr(sub_expr) for sub_expr in expr]
            callee = args.pop(0)
            return self.append(call(callee, args))
        if expr.type == 'def':
            argv = [arg.string for arg in expr[0]]
            body = expr[1:]
            return self.new_function(argv, body)
        if expr.type == 'op':
            lhs, rhs = expr
            opname = ''
            if expr.string == '<':
                opname = 'lt'
            if expr.string == '>':
                opname = 'gt'
            if expr.string == '<=':
                opname = 'le'
            if expr.string == '>=':
                opname = 'ge'
            if expr.string == '!=':
                opname = 'ne'
            if expr.string == '==':
                opname = 'eq'
            if len(opname) > 0:
                res = call(self.function.lookup(opname), [self.expr(lhs), self.expr(rhs)])
                self.append(res)
                return res
        raise Exception("%s not built" % expr.repr())

    def stmt(self, stmt):
        if stmt.type == 'op' and stmt.string == '=':
            assert stmt[0].type == 'identifier'
            var = self.function.bind(stmt[0].string)
            self.append(let(var, self.stmt(stmt[1])))
            return var
        if stmt.type == 'op' and stmt.string == ':=':
            raise Exception("upscope assignment rules are about to change.")
            assert stmt[0].type == 'identifier'
            var = self.function.lookup(stmt[0].string)
            assert var is not None, repr(expr.string)
            self.append(let(var, self.stmt(stmt[1])))
            return var
#        if stmt.type == 'import':
#            var = self.function.bind(stmt.string)
#            m = call(self.function.lookup('import'), [objects.String(stmt.string)])
#            self.append(m)
#            self.append(let(var, m))
#            return m
        if stmt.type == 'if':
            then = self.new_block()
            end  = self.new_block()
            self.flag = self.expr(stmt[0])
            self.append(cbranch(self.flag, then, end))
            b = self.spawn(then)
            for sub_stmt in stmt[1:]:
                b.stmt(sub_stmt)
            b.append(branch(end))
            self.attach(end)
            return None
        if stmt.type == 'else':
            then = self.new_block()
            end  = self.new_block()
            self.append(cbranch(self.flag, end, then))
            b = self.spawn(then)
            for sub_stmt in stmt:
                b.stmt(sub_stmt)
            b.append(branch(end))
            self.attach(end)
            return None
        if stmt.type == 'while':
            loop = self.new_block()
            end  = self.new_block()

            cond = self.expr(stmt[0])
            self.append(cbranch(cond, loop, end))

            b = self.spawn(loop)
            for sub_stmt in stmt[1:]:
                b.stmt(sub_stmt)
            cond = b.expr(stmt[0])
            b.append(cbranch(cond, loop, end))

            self.attach(end)
            return None
        if stmt.type == 'return':
            if len(stmt) > 0:
                self.append(ret(self.expr(stmt[0])))
            else:
                self.append(ret(objects.null))
            return None
        return self.expr(stmt)

def build(body, module):
    root = Function([], parent=module)
    builder = Builder(root, Block(root))
    for stmt in body:
        builder.stmt(stmt)
    builder.append(ret(objects.null))
    for fn in builder.cont:
        fn()
    return root
