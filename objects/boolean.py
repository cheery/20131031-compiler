class Boolean(object):
    def __init__(self, value):
        self.value = value

    def call(self, args):
        raise Exception("boolean is not callable")

    def __repr__(self):
        return 'const(%s)' % (repr(self.value).lower())
