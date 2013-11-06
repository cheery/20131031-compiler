class Integer(object):
    def __init__(self, value):
        assert isinstance(value, (int, long))
        self.value = value

    def call(self, args):
        raise Exception("integer is not callable")

    def to_string(self):
        return str(self.value)

    def __repr__(self):
        return 'const(%r)' % self.value
