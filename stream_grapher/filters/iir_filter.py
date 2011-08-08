#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import math
import operator

class IIRFilter(object):
    """
     Description
    
      Filter a data sequence, x, using a digital filter. The filter is a direct
      form II transposed implementation of the standard difference equation
      (see "Algorithm").
    
    Inputs:
    
      b -- The numerator coefficient vector in a 1-D sequence.
      a -- The denominator coefficient vector in a 1-D sequence.  If a[0]
           is not 1, then both a and b are normalized by a[0].

    Algorithm:
    
      The filter function is implemented as a direct II transposed structure.
      This means that the filter implements
    
      a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
                            - a[1]*y[n-1] - ... - a[na]*y[n-na]
    
      using the following difference equations:
    
      y[m] = b[0]*x[m] + z[0,m-1]
      z[0,m] = b[1]*x[m] + z[1,m-1] - a[1]*y[m]
      ...
      z[n-3,m] = b[n-2]*x[m] + z[n-2,m-1] - a[n-2]*y[m]
      z[n-2,m] = b[n-1]*x[m] - a[n-1]*y[m]
    
      where m is the output sample number and n=max(len(a),len(b)) is the
      model order.
    
      The rational transfer function describing this filter in the
      z-transform domain is
                                  -1               -nb
                      b[0] + b[1]z  + ... + b[nb] z
              Y(z) = ---------------------------------- X(z)
                                  -1               -na
                      a[0] + a[1]z  + ... + a[na] z
    

    >>> id = IIRFilter([1],[1])
    >>> id(1)
    1
    >>> id(0)
    0
    >>> id(-25)
    -25
    >>> ac = IIRFilter([1, 1],[1])
    >>> ac(1)
    1
    >>> ac(1)
    2
    >>> ac(1)
    2
    >>> rnd = IIRFilter([1,2, 3],[1])
    >>> rnd(3.0)
    3.0
    >>> rnd(-9)
    -3.0
    >>> rnd = IIRFilter([1],[1,2,3])
    >>> rnd(3.0)
    3.0
    >>> rnd(-9.0)
    -15.0
    >>> rnd = IIRFilter([1,1,-2.0],[1,-2,9])
    >>> rnd(3.0)
    3.0
    >>> rnd(-9.0)
    0.0
    >>> rnd = IIRFilter([2],[2])
    >>> rnd(3.0)
    3.0
    >>> rnd(-9.0)
    -9.0
    
    """
    def __init__(self, b, a):
        self.b = b
        self.a = a
        if a[0] != 1 and a[0] != 0:
            self.b = [x/float(a[0]) for x in b]
            self.a = [x/float(a[0]) for x in a]
        self._a_nec = [-1*x for x in a[1:]]
        self.x_old = [0] * (len(b)-1)
        self.y_old = [0] * (len(a)-1)

    def __call__(self, data):
        x = [data] + self.x_old
        x_filtered = map(operator.mul, x, self.b)
        y_filtered = map(operator.mul, self.y_old, self._a_nec)
        out = reduce(operator.add, x_filtered + y_filtered)
        self.x_old = x[:-1]
        self.y_old = ([out] + self.y_old)[:len(self.a)-1]
        return out


if __name__ == "__main__":
    import doctest
    doctest.testmod()

