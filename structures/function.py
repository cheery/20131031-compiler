import itertools
from variable import Variable

class Function(object):
    uid_generator = itertools.count(1)

    def __init__(self, argv, parent=None):
        self.argv = argv
        self.parent = parent
        self.namespace = dict()
        self.functions = []
        self.blocks = []
        self.uid = Function.uid_generator.next()
        self.variables = []

    def __getitem__(self, index):
        return self.blocks[index]

    def __iter__(self):
        return iter(self.blocks)

    def __len__(self):
        return len(self.blocks)

    def append(self, block):
        self.blocks.append(block)


    def lookup(self, name):
        if name in self.namespace:
            return self.namespace[name]
        elif self.parent is not None:
            res = self.parent.lookup(name)
            if isinstance(res, Variable):
                res.upscope = True
            return res

    def bind(self, name):
        if name in self.namespace:
            return self.namespace[name]
        else:
            var = self.namespace[name] = Variable(self, name)
            return var
        

    def function(self, argv):
        function = Function(argv, self)
        self.functions.append(function)
        return function


    def __repr__(self):
        return "f%i" % (self.uid)

    def repr(self):
        listing = "%r %r:\n" % (self, self.argv)
        listing += '\n'.join(block.repr() for block in self.blocks + self.functions)
        return listing.replace('\n', '\n    ')
