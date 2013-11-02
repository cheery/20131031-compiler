class Variable(object):
    def __init__(self, function, name):
        self.function = function
        self.name = name
        self.letc = 0
        self.getc = 0
        self.upscope = False

    def __repr__(self):
        return "%s@%r" % (self.name, self.function)

class Constant(object):
    def __init__(self, function, value):
        self.function = function
        self.value = value

    def __repr__(self):
        return "const(%r)" % self.value

class Namespace(object):
    def __init__(self, namespace=None):
        self.namespace = dict() if namespace is None else namespace

    def lookup(self, name):
        return self.namespace[name]
        
    def define(self, name, value):
        self.namespace[name] = value

class Function(object):
    _next_uid = 0
    def __init__(self, argv, parent=None):
        self.argv = argv
        self.parent = parent
        self.namespace = dict()
        self.constants = set()
        self.functions = []
        self.blocks = []
        self.uid = Function._next_uid
        Function._next_uid += 1

    def append(self, block):
        self.blocks.append(block)

    def __iter__(self):
        return iter(self.blocks)

    def lookup(self, name):
        if name in self.namespace:
            return self.namespace[name]
        elif self.parent is not None:
            return self.parent.lookup(name)

    def bind(self, name):
        if name in self.namespace:
            return self.namespace[name]
        else:
            var = self.namespace[name] = Variable(self, name)
            return var
        
    def constant(self, value):
        for const in self.constants:
            if const.value == value:
                return const
        const = Constant(self, value)
        self.constants.add(const)
        return const

    def function(self, argv):
        function = Function(argv, self)
        self.functions.append(function)
        return function

    def repr(self):
        listing = '\n'.join(block.repr() for block in self)
        sub_listings = '\n'.join("f%i %r:\n" % (function.uid, function.argv) + function.repr() for function in self.functions)
        listing += '\n'+ sub_listings.replace('\n', '\n    ')
        return listing

    def __repr__(self):
        return "f%i" % (self.uid)
