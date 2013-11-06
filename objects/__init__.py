from closure import Closure
from frame import Frame
from float import Float
from integer import Integer
from string import String
from boolean import Boolean
from null import Null
from native import Native

null = Null()
true  = Boolean(True)
false = Boolean(False)

def is_true(obj):
    if (obj is false) or (obj is null):
        return False
    else:
        return True
