class Namespace(object):
    def __init__(self, namespace=None):
        self.namespace = dict() if namespace is None else namespace

    def lookup(self, name):
        return self.namespace[name]
        
    def define(self, name, value):
        self.namespace[name] = value
