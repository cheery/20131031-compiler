class Null(object):
    def __init__(self):
        pass

    def call(self, args):
        raise Exception("null is not callable")

    def to_string(self):
        return 'null'

    def __repr__(self):
        return 'const(null)'
