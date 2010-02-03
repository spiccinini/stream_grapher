#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# notch.py Filtro Notch de segundo orden
# Copyright (C) 2009  Santiago Piccinini
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


import math
import operator

#-------------------------------------------
# Filtro Notch de segundo orden
#
# Transferencia
# Sea
#     th = 2 * pi * central_frecuency * sample_period
#      d = exp(-2 * pi * bandwidth/2.0 * sample_period)
#      a = ( 1 + d^2) / 2
#      b = ( 1 + d^2) * cos(th)
#
# entonces
#          z^2 - 2 cos (th) z + 1
# H(z) = a ----------------------
#            z^2 - b z + d^2
#
# Ecuacion en diferencias:
#  y(n) - b * y(n-1) + d^2 * y(n-2) = a * x(n)  - a*2*cos(th) * x(n-1) + a * x(n-2)
#
class Notch(object):
    """
    Implementación de filtro notch de segundo orden. Por cada muestra de entrada devuelve una muestra de salida.
    >>> notch = Notch(1/44100.0, 50, 10)
    >>> entrada = [1, 2, 3 4] # ...
    >>> salida = [notch(muestra) for muestra in entrada]
    """
    def __init__(self, sample_period, central_frecuency, bandwidth):
        self.Ts = sample_period
        self.f_c = central_frecuency
        self.BW = bandwidth
        self.th = 2 * math.pi * central_frecuency * sample_period
        self.d = math.exp(-2 * math.pi * bandwidth/2.0 * sample_period)
        self.a = ( 1 + math.pow(self.d ,2)) / 2
        self.b =  ( 1 + math.pow(self.d ,2)) * math.cos(self.th)

        self.B = [self.a , -2* math.cos(self.th)*self.a, self.a ] # Coeficientes del filtro (parte x)
        self.A = [1.0, -self.b, math.pow(self.d, 2)] # Coeficientes del filtro (parte y)
        self.A_nec = [--self.b, -math.pow(self.d, 2)]
        self.x_old = [0, 0]
        self.y_old = [0, 0]

    def __call__(self, input):
        x = [input] + self.x_old
        x_filtered = map(operator.mul, x, self.B)
        y_filtered = map(operator.mul, self.y_old, self.A_nec)
        out = reduce(operator.add, x_filtered + y_filtered)
        self.x_old = x[:-1]
        self.y_old = [out] + self.y_old[:-1]
        return out


