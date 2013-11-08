import ctypes
import objects

class CellType(object):
    def __init__(self, ctype):
        self.ctype = ctype

    def from_ctypes(self, value):
        if isinstance(value, (int, long)):
            return objects.Integer(value)
        if isinstance(value, float):
            return objects.Float(value)
        if value is None:
            return objects.null
        raise Exception("Unknown cell value: %r" % value)
    
class VoidType(CellType):
    def from_ctypes(self, value):
        return objects.null

class IntType(CellType):
    def from_ctypes(self, value):
        return objects.Integer(value)

class FloatType(CellType):
    def from_ctypes(self, value):
        return objects.Float(value)

c_void = VoidType(None)
c_int  = CellType(ctypes.c_int)
c_uint = CellType(ctypes.c_uint)
c_long = CellType(ctypes.c_long)
c_ulong = CellType(ctypes.c_ulong)
c_char = CellType(ctypes.c_char)
c_ubyte = CellType(ctypes.c_ubyte)
c_ushort = CellType(ctypes.c_ushort)
c_short = CellType(ctypes.c_short)
c_float = CellType(ctypes.c_float)
c_double = CellType(ctypes.c_double)

class Pointer(object):
    def __init__(self, pointee):
        self.pointee = pointee
        self.ctype = ctypes.POINTER(pointee.ctype)

class CFuncType(object):
    def __init__(self, restype, argtypes):
        self.restype = restype
        self.argtypes = argtypes

class CFunc(object):
    def __init__(self, cfunc, proto, name=None):
        self.cfunc = cfunc
        self.proto = proto
        self.name = name

    def to_string(self):
        if self.name is None:
            return "<CFunc %x>" % id(self)
        return self.name

    def call(self, args):
        res = self.cfunc(*[arg.as_ctypes_argument() for arg in args])
        return self.proto.restype.from_ctypes(res)

class Record(object):
    def __init__(self, fields, name='record'):
        self.fields = dict(fields)
        cfields = [(name, t.ctype) for name, t in fields]
        self.ctype = type(name, (ctypes.Structure,), {"_fields_":cfields})
#
#    def vm_call(self, args):
#        return FFIInstance(self.ctype(*args))

class Union(object):
    def __init__(self, fields, name='union'):
        self.fields = dict(fields)
        cfields = [(name, t.ctype) for name, t in fields]
        self.ctype = type(name, (ctypes.Union,), {"_fields_":cfields})
#
#    def vm_call(self, args):
#        return FFIInstance(self.ctype(*args))

def byref(obj):
    assert isinstance(obj, Instance)
    return ctypes.byref(obj._as_parameter_)
