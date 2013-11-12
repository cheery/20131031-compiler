import objects
import greenlet

class Greenlet(object):
    def __init__(self, greenlet, parent):
        self.greenlet = greenlet
        self.parent = parent

    def switch(self, args):
        res = self.greenlet.switch(args)
        if res is objects.null:
            return objects.null
        if len(res) == 1:
            return res[0]
        raise Exception("no multiple argument support on switch yet")

    def getattr(self, name):
        if name == 'dead':
            return (objects.true, objects.false)[self.greenlet.dead]
        if name == 'parent':
            return self.parent
        if name == 'switch':
            return objects.Native('greenlet.switch', lambda *args: self.switch(args))
        raise Exception("no such name %r in greenlet" % name)

current = Greenlet(greenlet.getcurrent(), None)

def make_greenlet(fn, parent=None):
    if parent is None:
        parent = current
    this = greenlet.greenlet(lambda args: fn.call(args), parent.greenlet)
    return Greenlet(this, parent)

def get_current_greenlet():
    return current

module = objects.Module('greenlet', {
    'greenlet':  objects.Native('greenlet', make_greenlet),
    'getcurrent':objects.Native('getcurrent', get_current_greenlet),
})
