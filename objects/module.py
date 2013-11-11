class Module(object):
    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace

    def call(self, args):
        raise Exception("module is not callable (not yet)")

    def to_string(self):
        return self.name

    def __repr__(self):
        return 'module(%s)' % self.name

    def getattr(self, name):
        #print 'getattr %s.%s' % (self.name, name)
        return self.namespace[name]
