class String(object):
    def __init__(self, value):
        assert isinstance(value, (str, unichr))
        self.value = value

    def call(self, args):
        raise Exception("string is not callable")

    def to_string(self):
        return self.value

    def __repr__(self):
        return 'const(%r)' % self.value
