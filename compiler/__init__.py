import objects
from llvm import *
from llvm.core import *
import subprocess
import tempfile

ty_int = Type.int()
ty_void = Type.void()

def read_arg(arg):
    if isinstance(arg, objects.Integer):
        return Constant.int(ty_int, arg.value)
    raise Exception("no encoding for this: %r" % arg)

x86_gnu = dict(
    crt1 = "/usr/lib/x86_64-linux-gnu/crt1.o",
    crtn = "/usr/lib/x86_64-linux-gnu/crtn.o",
    crti = "/usr/lib/x86_64-linux-gnu/crti.o",
    ld_linux = "/lib64/ld-linux-x86-64.so.2",
)

def native(main_closure):
    print "native compilation entry"
    module = Module.new('native_module')

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

    for instruction in block:
        name = instruction.name

        if name == 'ret':
            builder.ret(read_arg(instruction[0]))
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
