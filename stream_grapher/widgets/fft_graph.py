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
import scipy.signal
from OpenGL import GL as gl

from stream_grapher.circular_buffers import CircularBuffer
from graph import Graph, DrawableLineStrip
from grid import Grid

class FFTGraph(Graph):
    def __init__(self, fft_size, fft_window_size, sample_rate, size, position, color=(255,0,0), window_type="boxcar"):
        Graph.__init__(self, size, position, color)

        self._fft_size = fft_size
        self._fft_window_size = fft_window_size
        self.samples = CircularBuffer(self._fft_window_size, 0.) # For saving incoming samples before compute FFT
        self.x_axis_len = (fft_size/2+1)  # For rfft only! This function does not compute the negative frequency terms,
                                          # and the length of the transformed axis of the output is therefore n/2+1
        self.beans = 1 #beans
        self.ffted_data = [0] * self.x_axis_len
        self.window_type = window_type
        self.window = scipy.signal.get_window(self.window_type, self._fft_window_size)
        self._color = color
        self._amplification = 1
        self.log = False
        self.sample_rate = sample_rate
        self.h_scale = 1.0
        self.h_position = 0.0 # 0.0 to the left, 1.0 to the right

        self.grid = Grid(h_lines=4, v_lines=4, size=size, position=position)

        vertexs = self._vertex_list_from_ffted_data(self.do_fft(self.samples))
        self.line_strip = DrawableLineStrip(vertexs.astype("f"))

    def do_fft(self, samples):
        rfft = np.fft.rfft(self.samples*self.window, self._fft_size)
        ffted_data = np.abs(rfft) * self._amplification / min(self._fft_size, self._fft_window_size)
        if self.log:
            ffted_data = np.log10(ffted_data)
        return ffted_data

    def _vertex_list_from_ffted_data(self, ffted_data):
        x_axis = np.arange(self.x_axis_len) * self.h_scale * self.width / float(self.x_axis_len)
        vertex_list = np.column_stack((x_axis, ffted_data))
        return vertex_list

    def regenerate_graph(self):
        "Update graph from self.samples doing fft."
        ffted_data = self.do_fft(self.samples)
        vertices = self._vertex_list_from_ffted_data(ffted_data)
        self.line_strip.vertices_x[:] = vertices[:,0]
        self.line_strip.vertices_y[:] = vertices[:,1]

    def set_fft_size(self, fft_size):
        self._fft_size = fft_size
        self.x_axis_len = (fft_size/2+1)
        self.samples = CircularBuffer(self._fft_window_size, 0.)
        self._vertex_list.resize(self.x_axis_len)
        self.regenerate_graph()

    def set_fft_window_size(self, fft_window_size):
        self._fft_window_size = fft_window_size
        self.window = scipy.signal.get_window(self.window_type, self._fft_window_size)
        self.samples = CircularBuffer(self._fft_window_size, 0.)
        self.regenerate_graph()

    def set_window_type(self, window_type):
        self.window = scipy.signal.get_window(self.window_type, self._fft_window_size)
        self.regenerate_graph()

    def get_amplification(self):
        return self._amplification

    def set_amplification(self, amplification):
        self._amplification = amplification
        self.regenerate_graph()

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.freq_per_h_division = self.sample_rate/2 * float(self.grid.h_sep) / float(self.width) * self.h_scale
        #self.freq_per_h_division_label.text = str(self.freq_per_h_division)+ "Hz/div"

    def draw(self):
        self.grid.draw()
        gl.glPushMatrix()
        gl.glColor3ub(*self._color)
        gl.glTranslatef(self.position[0], self.position[1], 0)
        #pyglet.gl.glScissor(self.position[0], self.position[1], self.width, self.heigth+1)
        #pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)
        self.line_strip.draw()
        #pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)
        gl.glPopMatrix()
        #self.freq_per_h_division_label.draw()

    def add_samples(self, samples):
        """
        Add a list of samples to the graph. If acumulated samples are equal or grater than fft_window_size
        the FFT is calculated, the graph updated and acumulated data cleaned.
        """
        need_to_do_FFT = False
        if len(samples) + self.samples._index >= self._fft_window_size:
            need_to_do_FFT = True
        self.samples.put(samples)
        if need_to_do_FFT:
            self.regenerate_graph()

    amplification = property(get_amplification, set_amplification)
    fft_size = property(lambda self: self._fft_size, set_fft_size)
    fft_window_size = property(lambda self: self._fft_window_size, set_fft_window_size)
