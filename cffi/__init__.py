import objects
from cdll import CDLL
import os

header_prefixes = [
    "/usr/include",
]
def find_header(name):
    for prefix in header_prefixes:
        path = os.path.join(prefix, name)
        if os.path.exists(path):
            return path
    raise Exception("header %r not found" % name)

def ffi_library(path, *headers):
    assert isinstance(path, objects.String)
    resolved_headers = []
    for header in headers:
        assert isinstance(header, objects.String)
        resolved_headers.append( find_header(header.value) )
    print 'importing C library'
    print 'lib', path
    print 'headers', resolved_headers
    return CDLL(path.value, resolved_headers)

module = objects.Module('cffi', {
    'library': objects.Native('library', ffi_library),
})
