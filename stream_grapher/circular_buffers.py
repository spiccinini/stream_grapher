#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2010  Santiago Piccinini
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Circular Buffer. Plain python and numpy implementations.
"""
import numpy as np

class CircularBufferPy(list):
    """CricularBuffer, python implementation.

    >>> circ_buff = CircularBufferPy(size=4, default=None)
    >>> circ_buff
    [None, None, None, None]
    >>> circ_buff.put([1])
    >>> circ_buff
    [1, None, None, None]
    >>> circ_buff.put([2])
    >>> circ_buff
    [1, 2, None, None]
    >>> circ_buff.put([3,4])
    >>> circ_buff
    [1, 2, 3, 4]
    >>> circ_buff.put([5])
    >>> circ_buff
    [5, 2, 3, 4]
    >>> circ_buff.put([6,7,8,9])
    >>> circ_buff # Dont care of order
    [6, 7, 8, 9]
    >>> circ_buff.put([10,11,12,13,14,15])
    >>> circ_buff # Dont care of order
    [12, 13, 14, 15]
    """
    def __init__(self, size, default=None):
        self.size = size
        self.default = default
        list.__init__(self, [default]*size)
        self._index = 0

    def put(self, elements):
        if len(elements) >= self.size:
            self.__setslice__(0, self.size, elements[-self.size:])
            return
        for elem in elements:
            self[self._index] = elem
            self._index +=1
            if self._index >= self.size:
                self._index = 0


class CircularBuffer(np.ndarray):
    """CricularBuffer, numpy implementation.

    >>> circ_buff = CircularBuffer(size=4, default=0)
    >>> circ_buff
    CircularBuffer([0, 0, 0, 0])
    >>> circ_buff.put([1])
    >>> circ_buff
    CircularBuffer([1, 0, 0, 0])
    >>> circ_buff.put([2])
    >>> circ_buff
    CircularBuffer([1, 2, 0, 0])
    >>> circ_buff.put([3,4])
    >>> circ_buff
    CircularBuffer([1, 2, 3, 4])
    >>> circ_buff.put([5])
    >>> circ_buff
    CircularBuffer([5, 2, 3, 4])
    >>> circ_buff.put([6,7,8,9])
    >>> circ_buff # Dont care of order
    CircularBuffer([6, 7, 8, 9])
    >>> circ_buff.put([10,11,12,13,14,15])
    >>> circ_buff # Dont care of order
    CircularBuffer([12, 13, 14, 15])
    """
    def __new__(subtype, size, default=0):
       obj = np.array([default]*size)
       obj = obj.view(subtype)
       obj._index = 0
       return obj

    def put(self, data):
        data_length = len(data)
        if data_length >= self.size:
            self.__setslice__(0, self.size, data[-self.size:])
            return
        til_the_end = self.size - self._index
        cp_til_the_end = min(til_the_end, data_length)
        self.__setslice__(self._index, self._index+cp_til_the_end, data[:cp_til_the_end])
        copied = cp_til_the_end
        if copied == data_length:
            self._index += copied
            if self._index == self.size:
                self._index = 0
        else:
            cp_from_the_begining = data_length -copied
            self.__setslice__(0, cp_from_the_begining, data[copied:])
            self._index = cp_from_the_begining

if __name__ == "__main__":
   import doctest
   doctest.testmod()
   import timeit
   tpython = timeit.Timer("circ_buff.put(np.arange(50))","import numpy as np;from __main__ import CircularBufferPy as CB; circ_buff = CB(size=400,default=0)")
   tnumpy = timeit.Timer("circ_buff.put(np.arange(50))","import numpy as np;from __main__ import CircularBuffer as CB; circ_buff = CB(size=400, default=0)")
   times = 10000
   print "python: %s, numpy: %s" % (tpython.timeit(times), tnumpy.timeit(times))
