# -*- coding: UTF-8 -*-

# Copyright (C) 2009, 2010, 2011  Santiago Piccinini
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

import numpy as np
from OpenGL import GL as gl

from stream_graph import StreamGraph

class BrowsableStreamGraph(StreamGraph):
    def __init__(self, n_samples, size, position, color=(255,255,255)):
        StreamGraph.__init__(self, n_samples,size, position, color)

        self.sample_buffer = []
        self.first_sample_in_view = 0
        self._is_first_empty_samples = True

    def draw(self):
        first = self.first_sample_in_view
        samples = self.sample_buffer[first:first+self.n_samples]

        # fill with zero to the right until n_samples
        samples.extend([0] * (self.n_samples - len(samples)))
        self.line_strip.vertices = self._vertex_list_from_samples_all(samples)

        self.grid.draw()
        gl.glPushMatrix()
        gl.glColor3ub(*self._color)
        gl.glTranslatef(self.position[0], self.position[1]+(self.heigth * self.v_position), 0)
        self.line_strip.draw()
        gl.glPopMatrix()

    def add_samples(self, samples):
        self.sample_buffer.extend(samples)

    def set_h_position(self, value):
        first_sample = int(len(self.sample_buffer)*value)
        self.first_sample_in_view = first_sample
