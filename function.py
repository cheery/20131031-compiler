class Variable(object):
    def __init__(self, function, name):
        self.function = function
        self.name = name

    def __repr__(self):
        return self.name

class Constant(object):
    def __init__(self, function, value):
        self.function = function
        self.value = value

    def __repr__(self):
        return "const(%r)" % self.value

class Function(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.namespace = dict()
        self.constants = set()
        self.blocks = []

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
