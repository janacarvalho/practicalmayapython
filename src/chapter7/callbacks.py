#callbacks.py
from maya import OpenMaya
import pymel.core as pmc

def addNameChangedCallback(callback, pynode=None):
    """Registers a callback so that
    `callback(pynode, oldname, newname)` is called when
    `pynode`'s name changes.
    If `pynode` is None, invoke the callback for every
    name change.

    Return the callback ID. Hold onto this if you will need to
    remove the callback.
    """

def removeNameChangedCallback(callbackId):
    """Removes a callback based on its ID."""


def removeNameChangedCallback(callbackId):
    OpenMaya.MNodeMessage.removeCallback(callbackId)

def addNameChangedCallback(callback, pynode=None):
    def omcallback(mobject, oldname, _): #(1)
        newname = OpenMaya.MFnDependencyNode(mobject).name()
        changedPynode = pmc.PyNode(newname) #(2)
        # Ignore name changes for manipulators and stuff
        # that have no scene objects
        if not _isvalidnode(changedPynode): #(3)
            return
        callback(changedPynode, oldname, newname) #(4)

    if pynode is None: #(5)
        listenTo = OpenMaya.MObject()
    else:
        listenTo = pynode.__apimobject__()
    return OpenMaya.MNodeMessage.addNameChangedCallback( #(6)
        listenTo, omcallback)

def _isvalidnode(pynode): #(7)
    try:
        bool(pynode)
        return True
    except KeyError:
        return False


def patchjoint():
    """Patch rename so it doesn't return anything."""
    def joint2(*args, **kwargs):
        res = oldjoint(*args, **kwargs)
        def rename2(*args2, **kwargs2):
            oldrename(*args2, **kwargs2)
        oldrename = res.rename
        res.rename = rename2
        return res
    oldjoint = pmc.joint
    pmc.joint = joint2

def test():
    """
>>> patchjoint()

>>> def cb(n, old, new):
...     print 'CB: %r, %r, %r' % (n, old, new)
>>> jspam = pmc.joint()
>>> jeggs = pmc.joint()
>>> cbid1 = addNameChangedCallback(cb, jspam)
>>> jspam.rename('spam') #(1)
CB: nt.Joint(u'spam'), u'joint1', u'spam'
>>> jeggs.rename('eggs') #(2)
>>> cbid2 = addNameChangedCallback(cb) #(3)
>>> jeggs.rename('eggs2') #(4)
CB: nt.Joint(u'eggs2'), u'eggs', u'eggs2'
>>> jspam.rename('spam2') #(5)
CB: nt.Joint(u'spam2'), u'spam', u'spam2'
CB: nt.Joint(u'spam2'), u'spam', u'spam2'
>>> removeNameChangedCallback(cbid2) #(6)
>>> jeggs.rename('eggs3') #(7)

    """


if __name__ == "__main__":
    import doctest
    doctest.testmod()
