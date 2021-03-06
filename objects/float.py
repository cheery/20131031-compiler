class Float(object):
    def __init__(self, value):
        assert isinstance(value, float)
        self.value = value

    def call(self, args):
        raise Exception("float is not callable")

    def to_string(self):
        return str(self.value)

    def __repr__(self):
        return 'const(%r)' % self.value

    def as_ctypes_argument(self):
        return self.value
