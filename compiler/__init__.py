import objects
from structures import Variable
from llvm import *
from llvm.core import *
import subprocess
import tempfile
import cffi
import ctypes

ty_char = Type.int(8)
ty_int = Type.int()
ty_void = Type.void()
ty_long = Type.int(64)

cell_types = {
    ctypes.c_ulong: Type.int(64),
    ctypes.c_long: ty_long,
    ctypes.c_int: ty_int,
    None: ty_void,
}

def convert_to_llvm_type(mytype):
    if isinstance(mytype, cffi.PointerType):
        res = convert_to_llvm_type(mytype.pointee)
        if res is ty_void:
            res = ty_char
        return Type.pointer(res)
    if isinstance(mytype, cffi.CellType):
        return cell_types[mytype.ctype]
    if isinstance(mytype, cffi.CFuncType):
        restype = convert_to_llvm_type(mytype.restype)
        argtypes = [convert_to_llvm_type(t) for t in mytype.argtypes]
        return Type.function(restype, argtypes)
    raise Exception("cannot convert %r" % mytype)

x86_gnu = dict(
    crt1 = "/usr/lib/x86_64-linux-gnu/crt1.o",
    crtn = "/usr/lib/x86_64-linux-gnu/crtn.o",
    crti = "/usr/lib/x86_64-linux-gnu/crti.o",
    ld_linux = "/lib64/ld-linux-x86-64.so.2",
)

def collect_namespace(frame, ns):
    if frame.parent is not None:
        collect_namespace(frame.parent, ns)
    for var, val in zip(frame.function.variables, frame.variables):
        ns[var] = val
    return ns

def native(main_closure):
    print "native compilation entry"
    module = Module.new('native_module')

    env = collect_namespace(main_closure.pframe, {})
    print env
    function = main_closure.function

    print "main", main_closure
    print "function:", function

    print "implicitly define entry type as ty_int, []"
    ty_func = Type.function(ty_int, [])

    f_main = module.add_function(ty_func, 'main')

    assert len(function) == 1, "only one block compiled now"

    bb = f_main.append_basic_block("entry")
    builder = Builder.new(bb)

    block = function[0]

    def read_arg(env, arg):
        if isinstance(arg, objects.Integer):
            return Constant.int(ty_int, arg.value)
        if isinstance(arg, objects.String):
            data = Constant.stringz(arg.value)
            var = module.add_global_variable(data.type, "_my_string")
            var.initializer = data
            return var.gep([Constant.int(ty_long, 0), Constant.int(ty_long, 0)])
        if isinstance(arg, cffi.CFunc):
            return arg
        if arg in env:
            return read_arg(env, env[arg])
        raise Exception("no encoding for this: %r" % arg)


    for instruction in block:
        name = instruction.name
        if name == 'ret':
            builder.ret(read_arg(env, instruction[0]))
        elif name == 'member':
            arg, key = instruction
            assert arg in env
            env[instruction] = env[arg].pre_getattr(builder, env, key)
        elif name == 'call':
            callee = read_arg(env, instruction[0])
            assert isinstance(callee, cffi.CFunc)
            assert callee.name != None
            ft = convert_to_llvm_type(callee.proto)
            fn = module.get_or_insert_function(ft, callee.name)
            args = []
            for t, arg in zip(ft.args, instruction[1:]):
                arg = read_arg(env, arg)
                if isinstance(arg, ConstantInt) and t.width > arg.type.width:
                    arg = arg.sext(t)
                args.append(arg)
            env[instruction] = builder.call(fn, args)
        else:
            raise Exception("cannot compile yet: %s" % instruction.repr())

    print "blocks:"
    print main_closure.function.repr()
    print module

    compile_file(module, 'native')

def compile_file(module, path):
    obj_file = tempfile.NamedTemporaryFile(suffix=".o")
    try:
        print "outputting to ", obj_file.name
        module.to_native_object(obj_file)
        obj_file.flush()
        print "linking %s" % path
        target = x86_gnu
        subprocess.call([
            'ld', '-o', path, '-dynamic-linker',
            target['ld_linux'],
            target['crt1'],
            target['crti'],
            '-lc', obj_file.name,
            target['crtn'],
        ])
    finally:
        obj_file.close()
        print "native compilation exit"

module = objects.Module('compile', {
    'native': objects.Native('native', native),
})
