class Native(object):
    def __init__(self, name, fn):
        self.name = name
        self.fn   = fn

    def call(self, args):
        return self.fn(*args)

    def __repr__(self):
        return '<native %s>' % self.name
