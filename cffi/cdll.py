import ctypes
import objects
from clang.cindex import *
import my_ctypes

Config.set_library_file('/usr/lib/llvm-3.3/lib/libclang.so.1')

celltypes = {
    TypeKind.VOID:   my_ctypes.c_void,
    TypeKind.INT:    my_ctypes.c_int,
    TypeKind.UINT:   my_ctypes.c_uint,
    TypeKind.LONG:   my_ctypes.c_long,
    TypeKind.ULONG:  my_ctypes.c_ulong,
    TypeKind.CHAR_S: my_ctypes.c_char,
    TypeKind.UCHAR:  my_ctypes.c_ubyte,
    TypeKind.USHORT: my_ctypes.c_ushort,
    TypeKind.SHORT:  my_ctypes.c_short,
    TypeKind.FLOAT:  my_ctypes.c_float,
    TypeKind.DOUBLE: my_ctypes.c_double,
}

def search(node, name, parent=None):
    if node.spelling and node.spelling == name:
        return node, parent
    if node.displayname and node.displayname == name:
        return node, parent
    for child in node.get_children():
        res = search(child, name, node)
        if res is not None:
            return res

def read_macro_constant(node):
    extent = node.extent
    start, end = extent.start, extent.end
    with open(start.file.name) as fd:
        a = start.offset + len(node.displayname)
        b = end.offset
        data = fd.read()[a:b].strip()
        if data.isdigit():
            return objects.Integer(int(data))
        if data.startswith('0x'):
            return objects.Integer(int(data, 16))
        if data.startswith('"') and data.endswith('"'):
            return objects.String(data[1:-1])
        raise Exception("no interpretation found for %r" % data)

def read_enum_constant(node, parent):
    const = objects.Integer(0)
    for item in parent.get_children():
        for info in item.get_children():
            assert info.kind == CursorKind.INTEGER_LITERAL
            const = read_macro_constant(info)
        if node.spelling == item.spelling:
            return const
        const.value += 1
    raise Exception("odd or invalid input for this function")

args = ['-D_Noreturn=__attribute__ ((__noreturn__))']
class Header(object):
    def __init__(self, path):
        self.path = path
        self.index = Index.create()
        self.translation_unit = self.index.parse(path, args, options=0x5)
        self.recordtype_cache = {}

    def convert_type(self, t):
        t = t.get_canonical()
        if t.kind in celltypes:
            return celltypes[t.kind]
        if t.kind == TypeKind.POINTER:
            return my_ctypes.Pointer(self.convert_type(t.get_pointee()))
        if t.kind == TypeKind.ENUM:
            return self.convert_type(t.get_declaration().enum_type)
        if t.kind == TypeKind.RECORD:
            rec = t.get_declaration()
            name = rec.spelling
            if name in self.recordtype_cache:
                return self.recordtype_cache[name]
            cls = {
                CursorKind.UNION_DECL: my_ctypes.Union,
                CursorKind.STRUCT_DECL: my_ctypes.Record,
            }[rec.kind]
            fields = []
            for child in rec.get_children():
                fields.append((child.spelling, self.convert_type(child.type)))
            self.recordtype_cache[name] = res = cls(fields, name)
            return res
        if t.kind == TypeKind.FUNCTIONPROTO:
            argtypes = [self.convert_type(arg) for arg in t.argument_types()]
            restype = self.convert_type(t.get_result())
            return my_ctypes.CFuncType(restype, argtypes)
        raise Exception("unknown type %r" % t.kind)

    def search(self, lib, name):
        tc = self.translation_unit.cursor
        res = search(tc, name)
        if res is not None:
            node, parent = res
            if node.kind == CursorKind.ENUM_CONSTANT_DECL:
                return read_enum_constant(node, parent)
            elif node.kind == CursorKind.MACRO_DEFINITION:
                return read_macro_constant(node)
            elif node.kind == CursorKind.FUNCTION_DECL:
                proto = self.convert_type(node.type.get_canonical())
                cfunc = getattr(lib, name)
                cfunc.restype = proto.restype.ctype
                cfunc.argtypes = [arg.ctype for arg in proto.argtypes]
                return my_ctypes.CFunc(cfunc, proto)
            else:
                raise Exception("unimplemented %r" % node.kind)

class CDLL(object):
    def __init__(self, path, headers):
        self.path = path
        self.headers = [Header(header) for header in headers]
        self.lib = ctypes.CDLL(path)
        self.cache = {}

    def search(self, name):
        for header in self.headers:
            res = header.search(self.lib, name)
            if res is not None:
                return res
        raise Exception("cffi name %r not found" % name)

    def getattr(self, name):
        if name in self.cache:
            res = self.cache[name]
        else:
            res = self.cache[name] = self.search(name)
        return res
