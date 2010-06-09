# -*- coding: UTF-8 -*-

# Copyright (C) 2009, 2010  Santiago Piccinini
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

import itertools
import pyglet.graphics
import numpy

def from_iterable(iterables):
    # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
    for it in iterables:
        for element in it:
            yield element

def flatten(listOfLists):
    return list(itertools.chain(from_iterable(listOfLists)))

class Grid(object):
    def __init__(self, size, position, color=(100,255,100), h_sep=100, v_sep=100):
        self.size = size
        self.position = position
        self.color = color
        self.h_sep = h_sep
        self.v_sep = v_sep

        v_center = position[1] + self.size[1]/2
        auxs = range(0, size[1]/2+1, v_sep) + range(0,-size[1]/2-1,-v_sep)[1:]
        num_h_lines = len(auxs)
        h_vertexs = flatten([(position[0], y + v_center, position[0]+size[0], y + v_center) for y in auxs])

        num_v_lines = size[0]/ h_sep + 1
        v_vertexs = flatten([(position[0]+x*h_sep, position[1], position[0]+x*h_sep, position[1]+size[1]) for x in range(num_v_lines)])

        h_colors = flatten([self.color for x in range(num_h_lines*2)])
        v_colors = flatten([self.color for x in range(num_v_lines*2)])
        self.h_vertex_list = pyglet.graphics.vertex_list(num_h_lines*2, ('v2f\static', h_vertexs), ("c3B\static", h_colors))
        self.v_vertex_list = pyglet.graphics.vertex_list(num_v_lines*2 , ('v2f\static', v_vertexs), ("c3B\static", v_colors))

    def draw(self):
        self.h_vertex_list.draw(pyglet.gl.GL_LINES)
        self.v_vertex_list.draw(pyglet.gl.GL_LINES)

class StreamGraph(object):
    def __init__(self, n_samples, size, position, color=(255,255,255), amplification=1):
        self.n_samples = n_samples
        self.samples = [0] * n_samples
        self.actual_sample_index = 0
        self.width = size[0]
        self.heigth = size[1]
        self.position = position
        self._color = color
        self._amplification = amplification
        self.v_position = 0.5 # 0 bottom, 1 top

        vertexs = self._vertex_list_from_samples(self.samples)
        colors = flatten([self._color for x in range(n_samples)])
        self._vertex_list = pyglet.graphics.vertex_list(n_samples, ('v2f\stream', vertexs), ("c3B\static", colors))

        self.grid = Grid(size, position, h_sep=100, v_sep=100)

        self.samples_per_h_division = int(self.n_samples * float(self.grid.h_sep) / float(self.width))
        self.samples_per_h_division_label = pyglet.text.Label(str(self.samples_per_h_division)+ "/div",
                          font_size=12, x=size[0]/2.0 + position[0], y=position[1]- 10, anchor_x='center', anchor_y='center')

        self.values_per_v_division = int(self.grid.v_sep / float(self._amplification))
        self.values_per_v_division_label = pyglet.text.Label(str(self.values_per_v_division)+"/div",
                          font_size=12, x=position[0]-40, y=position[1]+self.heigth/2.0, anchor_x='center', anchor_y='center')


    def draw(self, samples):
        "Add a list of samples to the graph and then draw it"
        self.add_samples(samples)
        self.grid.draw()
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
        self.samples_per_h_division_label.draw()
        self.values_per_v_division_label.draw()

    def redraw(self):
        "Draw the graph"
        self.grid.draw()
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
        self.samples_per_h_division_label.draw()
        self.values_per_v_division_label.draw()

    def add_samples(self, samples):
        "Add a list of samples to the graph"
        for sample in samples:
            index = self.actual_sample_index
            self.samples[index] = sample
            self._vertex_list.vertices[index*2:index*2+2] = self._vertex_from_sample(sample, index)
            self.actual_sample_index +=1
            if self.actual_sample_index >= self.n_samples:
                    self.actual_sample_index = 0

    def set_n_samples(self, n_samples):
        "Set a new value of n_samples"
        if n_samples <=0:
            raise AttributeError("n_samples must be > 0")
        self.n_samples = n_samples
        new_samples = [0]*n_samples
        for i in range(n_samples):
            try:
                new_samples[i] = self.samples[i]
            except IndexError:
                break
        self.samples = new_samples
        self._vertex_list.resize(n_samples)
        self._regenerate_vertex_list()
        self.set_color(self.color)
        self.actual_sample_index = min(self.actual_sample_index, n_samples-1)

        self.samples_per_h_division = int(self.n_samples * float(self.grid.h_sep) / float(self.width))
        self.samples_per_h_division_label.text  = str(self.samples_per_h_division)+"/div"
        
    def set_samples_per_h_division(self, samples_per_div):
        self.set_n_samples(int(samples_per_div * self.width / self.grid.h_sep))
        

    def set_amplification(self, amplification):
        self._amplification = amplification
        self._regenerate_vertex_list()
        self.values_per_v_division = int(self.grid.v_sep / float(self._amplification))
        self.values_per_v_division_label.text = str(self.values_per_v_division)+"/div"

    def set_values_per_v_division(self, values_per_div):
        self.set_amplification(self.grid.v_sep / float(values_per_div))
        

    def get_amplification(self):
        return self._amplification

    def set_color(self, color):
        self._color = color
        colors = tuple(flatten([color for x in range(self.n_samples)]))
        self._vertex_list.colors = colors

    def get_color(self):
        return self._color

    def set_v_position(self, v_position):
        self.v_position = v_position
        self._regenerate_vertex_list()
        

    def _regenerate_vertex_list(self):
        "Regenerates the internal vertex list from self.samples data"
        self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)

    def _vertex_list_from_samples(self, samples):
        vertex_list = []
        for index, sample in enumerate(self.samples):
            vertex_list.extend(self._vertex_from_sample(sample, index))
        return vertex_list

    def _vertex_from_sample(self, sample, index):
        x = self.position[0] + index * self.width / float(self.n_samples)
        y = self.position[1] + (self.heigth * self.v_position) + self.samples[index] * self.amplification
        return  x, y

    amplification = property(get_amplification, set_amplification)
    color = property(get_color, set_color)

class MultipleStreamGraph(object):
    def __init__(self, n_graphs, stream_graph_config):

        self.stream_graphs = [StreamGraph(*stream_graph_config) for i in range(n_graphs)]
        class FakeGrid(object):
            def __init__(self):
                self.h_sep = 100
                self.v_sep = 100
            def draw(self): pass

        for graph in self.stream_graphs:
            graph.grid = FakeGrid()

    def draw(self, samples_array):
        "Add a list of samples to the graph and then draw it"
        for i, samples in enumerate(samples_array):
            self.stream_graphs[i].draw(samples)

    def redraw(self):
        "Draw the graph"
        for graph in self.stream_graphs:
            graph.redraw()

    def add_samples(self, samples_array):
        "Add a list of samples to each graph"
        for i,graph in enumerate(self.stream_graphs):
            graph.add_samples(samples_array[i])

    def __getitem__(self, key):
        return self.stream_graphs[key]

class FFTGraph(object):
    def __init__(self, fft_size, fft_window_size, size, position, color=(255,255,255), amplification=1, sample_rate=1.0):
        self.fft_size = fft_size
        self.fft_window_size = fft_window_size
        self.samples = [0] * fft_window_size # For saving incoming samples before compute FFT
        self.actual_sample_index = 0
        self.x_axis_len = (fft_size/2+1)  # For rfft only! This function does not compute the negative frequency terms, and the length of the transformed axis of the output is therefore n/2+1
        self.ffted_data = [0] * self.x_axis_len
        self.width = size[0]
        self.heigth = size[1]
        self.position = position
        self._color = color
        self._amplification = amplification
        self.sample_rate = sample_rate
        self.h_scale = h_scale
        self.h_position = 0.0 # 0.0 to the left, 1.0 to the right
        
        self.grid = Grid(size, position, h_sep=100, v_sep=100)

        vertexs = self._vertex_list_from_samples(self.samples)
        colors = flatten([self._color for x in range(self.x_axis_len)])
        self._vertex_list = pyglet.graphics.vertex_list(self.x_axis_len, ('v2f\stream', vertexs), ("c3B\static", colors))
        
        self.freq_per_h_division = self.sample_rate/2 * float(self.grid.h_sep) / float(self.width) * self.h_scale
        self.freq_per_h_division_label = pyglet.text.Label(str(self.freq_per_h_division)+ "Hz/div",
                          font_size=12, x=size[0]/2.0 + position[0], y=position[1]- 10, anchor_x='center', anchor_y='center')

        #self.values_per_v_division = int(self.grid.v_sep / float(self._amplification))
        #self.values_per_v_division_label = pyglet.text.Label(str(self.values_per_v_division)+"/div",
        #                  font_size=12, x=position[0]-40, y=position[1]+self.heigth/2.0, anchor_x='center', anchor_y='center')

    def _vertex_list_from_samples(self, samples):
        rfft = numpy.fft.rfft(self.samples, self.fft_size)
        norm_abs_rfft = numpy.abs(rfft) * self._amplification
        self.ffted_data = norm_abs_rfft
        x_axis = self.position[0] + (numpy.arange(self.x_axis_len) * self.h_scale * self.width / float(self.x_axis_len))
        vertex_list = numpy.column_stack((x_axis, self.ffted_data+self.position[1])).flatten()
        return vertex_list

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.x_axis_len = (fft_size/2+1)
        self.ffted_data = [0] * self.x_axis_len
        self.samples = [0] * self.fft_window_size
        self._vertex_list.resize(self.x_axis_len)
        self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)
        self._vertex_list.colors = flatten([self._color for x in range(self.x_axis_len)])
        
    def set_fft_window_size(self, fft_window_size):
        self.fft_window_size = fft_window_size
        self.samples = [0] * fft_window_size
        self.actual_sample_index = 0
        self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)

    def set_amplification(self, amplification):
        self._amplification = amplification

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.freq_per_h_division = self.sample_rate/2 * float(self.grid.h_sep) / float(self.width) * self.h_scale
        self.freq_per_h_division_label.text = str(self.freq_per_h_division)+ "Hz/div"
        

    def redraw(self):
        "Draw the graph"
        self.grid.draw()
        pyglet.gl.glScissor(self.position[0], self.position[1], self.width, self.heigth+1) 
        pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST) 
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
        pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)
        self.freq_per_h_division_label.draw()

    def add_samples(self, samples):
        """
        Add a list of samples to the graph. If acumulated samples are equal or grater than fft_window_size
        the FFT is calculated, the graph updated and acumulated data cleaned.
        """
        #import pdb;pdb.set_trace()
        if len(samples) + self.actual_sample_index < self.fft_window_size:
            index = self.actual_sample_index
            self.samples[index:index+len(samples)] = samples
            self.actual_sample_index += len(samples)
        else: # need to compute FFT
            if len(samples) >= self.fft_window_size:
                # only need last fft_window_size samples
                self.samples = samples[-self.fft_window_size:]
                self.actual_sample_index = 0
                self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)
            else:
                for sample in samples:
                    index = self.actual_sample_index
                    self.samples[index] = sample
                    self.actual_sample_index +=1
                    if self.actual_sample_index >= self.fft_window_size:
                        self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)
                        self.actual_sample_index = 0


class StreamWidget(object):
    def __init__(self, n_samples, size, position):
        self.graph = StreamGraph(n_samples, size, position, (255,0,90))
        self.size = size

    def draw(self, samples):
       self.graph.draw(samples)

    def redraw(self):
       self.graph.redraw()

    def set_n_samples(self, n_samples):
        "Resize samples per widget"
        self.graph.set_n_samples(n_samples)


class MultipleStreamWidget(object):
    def __init__(self, n_graphs, n_samples, size, position):
        self.graph = MultipleStreamGraph(n_graphs, (n_samples, size, position, (255,0,90)))
        self.size = size

    def draw(self, samples):
       self.graph.draw(samples_array)

    def redraw(self):
       self.graph.redraw()

    def set_n_samples(self, n_samples):
        "Resize samples per widget"
        self.graph.set_n_samples(n_samples)


class FFTWidget(object):
    def __init__(self, fft_size, fft_window_size, size, position):
        self.graph = FFTGraph(fft_size, fft_window_size, size, position, (255,0,90))
        self.size = size

    def draw(self, samples):
        raise NotImplementedError

    def redraw(self):
       self.graph.redraw()

    def set_n_samples(self, n_samples):
        raise NotImplementedError
