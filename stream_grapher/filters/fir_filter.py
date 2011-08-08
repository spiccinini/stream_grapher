#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import math
import operator
import numpy
import scipy.signal

class FIRFilter(object):
    def __init__(self, b, a=None):
        self.b = b
        if a is None:
            a = numpy.array([1], dtype="float64")
        self.a = a
        max_len = max(len(self.a), len(self.b))
        self.z0 = numpy.zeros(max_len-1)

    def do_filter(self, data):
        filtered_data, self.z0 = scipy.signal.lfilter(self.b, self.a, data, zi=self.z0)
        return filtered_data

class HighPass(FIRFilter):

    def __init__(self, numtaps, cutoff, sample_rate):
      nyq = sample_rate/2.
      b = scipy.signal.firwin(numtaps, cutoff, width=None, window='hamming',
                              pass_zero=False, nyq=nyq)
      FIRFilter.__init__(self, b)
