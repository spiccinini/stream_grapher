import itertools
import ctypes
import numpy

ctypes.pythonapi.PyBuffer_FromReadWriteMemory.restype = ctypes.py_object

def as_numpy_array(c_array):
    # Copyright tamas <tkemen...@gmail.com>
    # http://groups.google.com/group/pyglet-users/browse_thread/thread/dfa600719ce989da
    """
    Return a view of the c array as a numpy array, with the
    underlying memory shared.
    """
    return numpy.frombuffer(
        ctypes.pythonapi.PyBuffer_FromReadWriteMemory(
                c_array, ctypes.sizeof(c_array._type_) * len(c_array)),
        dtype=c_array._type_)

def from_iterable(iterables):
    # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
    for it in iterables:
        for element in it:
            yield element

def flatten(listOfLists):
    return list(itertools.chain(from_iterable(listOfLists)))

class Persistable(object):
    persisting = tuple()
    def __init__(self, name=None):
        if name is None:
            self.name = repr(self.__class__)
        else:
            self.name = name

    def dump(self):
        d = {}
        for item in self.persisting:
            d[item] = getattr(self, item)
        return d

    def load(self, d):
        for key in d:
            setattr(self, key, d[key])
