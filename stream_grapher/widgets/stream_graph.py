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

from stream_grapher.circular_buffers import CircularBuffer
from graph import Graph, DrawableLineStrip
from grid import Grid
from controls import ColorControl, FloatControl, IntControl

class StreamGraph(Graph):
    controls = [
        ColorControl("color"),
        FloatControl("v_position", "v_pos", "vertical position"),
        FloatControl("values_per_v_division", "/div", "values per vertical division"),
        FloatControl("samples_per_h_division", "samples/div", "samples per division"),
    ]

    def __init__(self, n_samples, size, position, color=(255,255,255)):
        Graph.__init__(self, size, position, color)
        self._n_samples = n_samples

        self.samples = CircularBuffer(n_samples, 0.) #[0]*n_samples#
        self.actual_sample_index = 0
        self._color = self.color
        self._amplification = 1
        self._v_position = 0.5 # 0 bottom, 1 top
        vertexs = self._vertex_list_from_samples(self.samples)
        self.line_strip = DrawableLineStrip(vertexs.astype("f"))

        self.grid = Grid(h_lines=3, v_lines=3, size=size, position=position)

        self._samples_per_h_division = int(self._n_samples / float(self.grid.h_lines))
        #self.samples_per_h_division_label = pyglet.text.Label(str(self.samples_per_h_division)+ "/div",
        #                  font_size=12, x=size[0]/2.0 + position[0], y=position[1]- 10, anchor_x='center', anchor_y='center')

        self._values_per_v_division = int(self.grid.v_sep / float(self._amplification))
        #self.values_per_v_division_label = pyglet.text.Label(str(self.values_per_v_division)+"/div",
        #                  font_size=12, x=position[0]-40, y=position[1]+self.heigth/2.0, anchor_x='center', anchor_y='center')


    def draw(self):
        "Draw the graph"
        self.grid.draw()
        gl.glPushMatrix()
        gl.glColor3ub(*self._color)
        gl.glTranslatef(self.position[0], self.position[1]+(self.heigth * self.v_position), 0)
        self.line_strip.draw()
        gl.glPopMatrix()

    def add_samples(self, data):
        "Add a list of samples to the graph"
        self.samples.put(data)
        data = np.array(data) * self.amplification

        if data.size >= self._n_samples:
            self.line_strip.vertices_y[0:] = data[-self._n_samples:]
            return
        til_the_end = self._n_samples - self.actual_sample_index
        cp_til_the_end = min(til_the_end, data.size)
        self.line_strip.vertices_y[self.actual_sample_index:self.actual_sample_index+cp_til_the_end] = data[:cp_til_the_end]
        copied = cp_til_the_end
        if copied == data.size:
            self.actual_sample_index += copied
            if self.actual_sample_index == self._n_samples:
                self.actual_sample_index = 0
        else:
            cp_from_the_begining = data.size -copied
            self.line_strip.vertices_y[:cp_from_the_begining] = data[copied:]
            self.actual_sample_index = cp_from_the_begining

    def set_n_samples(self, n_samples):
        "Set a new value of n_samples"
        if n_samples <=0:
            raise AttributeError("n_samples must be > 0")
        self._n_samples = n_samples
        new_samples = CircularBuffer(n_samples, 0.)
        to_copy = min(self.samples.size, n_samples)
        new_samples[:to_copy] = self.samples[:to_copy]
        self.samples = new_samples
        self.line_strip.resize(n_samples)
        self._regenerate_vertex_list()
        self.set_color(self._color)
        self.actual_sample_index = min(self.actual_sample_index, n_samples-1)
        self._samples_per_h_division = int(self._n_samples / float(self.grid.h_lines))
        #self.samples_per_h_division_label.text  = str(self.samples_per_h_division)+"/div"

    def set_amplification(self, amplification):
        self._amplification = amplification
        self._regenerate_vertex_list()
        self._values_per_v_division = int(self.grid.v_sep / float(self._amplification))
        #self.values_per_v_division_label.text = str(self.values_per_v_division)+"/div"

    def set_samples_per_h_division(self, samples_per_div):
        self.set_n_samples(int(samples_per_div * self.grid.h_lines))

    def set_values_per_v_division(self, values_per_div):
        self.set_amplification(self.grid.v_sep / float(values_per_div))

    def set_color(self, color):
        self._color = color

    def set_v_position(self, v_position):
        self._v_position = v_position
        self._regenerate_vertex_list()

    def _regenerate_vertex_list(self):
        "Regenerates the internal vertex list from self.samples data"
        self._vertex_list_from_samples_all(self.samples)

    def _vertex_list_from_samples_all(self, samples):
        "Replace current _vertex_list from samples. Samples must be n_samples length."
        self.line_strip.vertices_x[:] = (np.arange(self._n_samples) * self.width / float(self._n_samples))
        self.line_strip.vertices_y[:] = np.array(samples) * self.amplification

    def _vertex_list_from_samples(self, samples):
        x_axis = (np.arange(self.actual_sample_index, len(samples)+self.actual_sample_index) * self.width / float(self._n_samples))
        y_axis = np.array(samples) * self.amplification
        vertex_list = np.column_stack((x_axis, y_axis))
        return vertex_list

    n_samples = property(lambda self: self._n_samples, set_n_samples)
    amplification = property(lambda self: self._amplification, set_amplification)
    samples_per_h_division = property(lambda self:self._samples_per_h_division, set_samples_per_h_division)
    values_per_v_division = property(lambda self: self._values_per_v_division, set_values_per_v_division)
    v_position = property(lambda self:self._v_position, set_v_position)
    color = property(lambda self:self._color, set_color)

