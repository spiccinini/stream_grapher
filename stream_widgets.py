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

from circular_buffers import CircularBuffer
from utils import flatten, as_numpy_array
import pyglet.graphics
import numpy
from pyglet import gl
from simplui import Frame, Theme, Dialogue, VLayout, Label, Button, \
                    TextInput, HLayout, FlowLayout, FoldingBox, Slider
import os
PATH = os.path.dirname(os.path.realpath(__file__))

class Graph(object):
    def __init__(self, size, position, color):
        self.size = size
        self.width = size[0]
        self.heigth = size[1]
        self.position = position
        self.color = color

    def draw(self):
        raise NotImplementedError


class Grid(Graph):
    def __init__(self, h_lines, v_lines, size, position, color=(100,255,100)):
        Graph.__init__(self, size, position, color)
        self.h_lines = h_lines
        self.v_lines = v_lines
        h_colors = flatten([self.color for x in range(h_lines*2)])
        v_colors = flatten([self.color for x in range(v_lines*2)])
        v_sep = size[0]/float(v_lines+1)
        h_sep = size[1]/float(h_lines+1)
        self.v_sep = v_sep
        self.h_sep = h_sep
        v_vertexs = flatten([(i*v_sep, 0, i*v_sep, size[1]) for i in range(1, v_lines+1)])
        h_vertexs = flatten([(0, i*h_sep, size[0], i*h_sep) for i in range(1, h_lines+1)])
        self.h_vertex_list = pyglet.graphics.vertex_list(h_lines*2, ('v2f\static', h_vertexs), ("c3B\static", h_colors))
        self.v_vertex_list = pyglet.graphics.vertex_list(v_lines*2 , ('v2f\static', v_vertexs), ("c3B\static", v_colors))
        border_vertexs = (
            0,0,
            self.size[0], 0,
            self.size[0], self.size[1],
            0,self.size[1],
        )
        border_colors = flatten([self.color for x in range(4)])
        self.border_vertex_list = pyglet.graphics.vertex_list(4 , ('v2f\static', border_vertexs), ("c3B\static", border_colors))

    def draw(self):
        gl.glPushMatrix()
        gl.glLineStipple(1,1)
        gl.glEnable(pyglet.gl.GL_LINE_STIPPLE)
        gl.glTranslatef(self.position[0], self.position[1], 0)
        self.h_vertex_list.draw(gl.GL_LINES)
        self.v_vertex_list.draw(gl.GL_LINES)
        gl.glDisable(gl.GL_LINE_STIPPLE)
        self.border_vertex_list.draw(gl.GL_LINE_LOOP)
        gl.glPopMatrix()


class LinesGraph(Graph):
    # TODO: All
    def __init__(self, n_vertexs, size, position, color=(255,255,255)):
        Graph.__init__(self, size, position, color)
        self.n_vertex = n_vertex
        self.vertexs = [0] * n_vertex
        self.v_position = 0.5 # 0 bottom, 1 top
        # bla bla bla


class StreamGraph(Graph):
    def __init__(self, n_samples, size, position, color=(255,255,255)):
        Graph.__init__(self, size, position, color)
        self.n_samples = n_samples

        self.samples = CircularBuffer(n_samples, 0.) #[0]*n_samples#
        self.actual_sample_index = 0
        self._color = color
        self._amplification = 1
        self.v_position = 0.5 # 0 bottom, 1 top

        vertexs = self._vertex_list_from_samples(self.samples)
        colors = flatten([self._color for x in range(n_samples)])
        self._vertex_list = pyglet.graphics.vertex_list(n_samples, ('v2f\stream', vertexs), ("c3B\static", colors))

        self.grid = Grid(h_lines=4, v_lines=4, size=size, position=position)

        self.samples_per_h_division = int(self.n_samples / float(self.grid.h_lines))
        self.samples_per_h_division_label = pyglet.text.Label(str(self.samples_per_h_division)+ "/div",
                          font_size=12, x=size[0]/2.0 + position[0], y=position[1]- 10, anchor_x='center', anchor_y='center')

        self.values_per_v_division = int(self.grid.v_sep / float(self._amplification))
        self.values_per_v_division_label = pyglet.text.Label(str(self.values_per_v_division)+"/div",
                          font_size=12, x=position[0]-40, y=position[1]+self.heigth/2.0, anchor_x='center', anchor_y='center')

        self.color = StreamGraph.color_property

    def draw(self):
        "Draw the graph"
        self.grid.draw()
        gl.glPushMatrix()
        gl.glTranslatef(self.position[0], self.position[1]+(self.heigth * self.v_position), 0)
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
        gl.glPopMatrix()
        self.samples_per_h_division_label.draw()
        self.values_per_v_division_label.draw()

    def add_samples(self, data):
        "Add a list of samples to the graph"
        self.samples.put(data)
        data = numpy.array(data) * self.amplification
        nv_y_axis = as_numpy_array(self._vertex_list.vertices)[1::2]
        if data.size >= self.n_samples:
            nv_y_axis = data[-self.n_samples:]
            return
        til_the_end = self.n_samples - self.actual_sample_index
        cp_til_the_end = min(til_the_end, data.size)
        nv_y_axis[self.actual_sample_index:self.actual_sample_index+cp_til_the_end] = data[:cp_til_the_end]
        copied = cp_til_the_end
        if copied == data.size:
            self.actual_sample_index += copied
            if self.actual_sample_index == self.n_samples:
                self.actual_sample_index = 0
        else:
            cp_from_the_begining = data.size -copied
            nv_y_axis[:cp_from_the_begining] = data[copied:]
            self.actual_sample_index = cp_from_the_begining

    def set_n_samples(self, n_samples):
        "Set a new value of n_samples"
        if n_samples <=0:
            raise AttributeError("n_samples must be > 0")
        self.n_samples = n_samples
        new_samples = CircularBuffer(n_samples, 0.)
        to_copy = min(self.samples.size, n_samples)
        new_samples[:to_copy] = self.samples[:to_copy]
        self.samples = new_samples
        self._vertex_list.resize(n_samples)
        self._regenerate_vertex_list()
        self.set_color(self._color)
        self.actual_sample_index = min(self.actual_sample_index, n_samples-1)
        self.samples_per_h_division = int(self.n_samples / float(self.grid.h_lines))
        self.samples_per_h_division_label.text  = str(self.samples_per_h_division)+"/div"

    def set_samples_per_h_division(self, samples_per_div):
        self.set_n_samples(int(samples_per_div * self.grid.h_lines))

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
        self._vertex_list_from_samples_all(self.samples)

    def _vertex_list_from_samples_all(self, samples):
        "Replace current _vertex_list from samples. Samples must be n_samples length."
        nv_x_axis = as_numpy_array(self._vertex_list.vertices)[0::2]
        nv_y_axis = as_numpy_array(self._vertex_list.vertices)[1::2]
        nv_x_axis[:] = (numpy.arange(self.n_samples) * self.width / float(self.n_samples))
        nv_y_axis[:] = numpy.array(samples) * self.amplification

    def _vertex_list_from_samples(self, samples):
        x_axis = (numpy.arange(self.actual_sample_index, len(samples)+self.actual_sample_index) * self.width / float(self.n_samples))
        y_axis = numpy.array(samples) * self.amplification
        vertex_list = numpy.column_stack((x_axis, y_axis)).flatten()
        return vertex_list

    amplification = property(get_amplification, set_amplification)
    color_property = property(get_color, set_color)


class BrowsableStreamGraph(StreamGraph):
    def __init__(self, n_samples, size, position, color=(255,255,255)):
        StreamGraph.__init__(self, n_samples,size, position, color)

        self.sample_buffer = [0] * n_samples
        self.first_sample_in_view = 0

    def draw(self):
        first = self.first_sample_in_view
        samples = self.sample_buffer[first:first+self.n_samples]
        # fill with zero to the right until n_samples
        samples.extend([0] * (self.n_samples - len(samples)))
        self._vertex_list.vertices = self._vertex_list_from_samples(samples)
        self.grid.draw()
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
        self.samples_per_h_division_label.draw()
        self.values_per_v_division_label.draw()

    def add_samples(self, samples):
        self.sample_buffer.extend(samples)

    def set_h_position(self, value):
        first_sample = int(len(self.sample_buffer)*value)
        self.first_sample_in_view = first_sample


class MultipleStreamGraph(object):
    def __init__(self, n_graphs, stream_graph_configs):
        colors = stream_graph_configs.pop("colors")
        self.stream_graphs = [StreamGraph(color=colors[i],**stream_graph_configs) for i in range(n_graphs)]

        class FakeGrid(object):
            def __init__(self):
                self.h_sep = 100
                self.v_sep = 100
            def draw(self): pass

        for graph in self.stream_graphs[:-1]: # Only need 1 real grid
            graph.grid = FakeGrid()

    def draw(self):
        for graph in self.stream_graphs:
            graph.draw()

    def add_samples(self, samples_array, n_graph=None):
        "Add a list of samples to each graph"
        samples = numpy.asarray(samples_array)
        if samples.size != 0:
            if n_graph is not None:
                self.stream_graphs[n_graph].add_samples(samples)
            else:
                samples_array = samples.transpose()
                for i, graph in enumerate(self.stream_graphs):
                    graph.add_samples(samples_array[i])

    def __getitem__(self, key):
        return self.stream_graphs[key]


class FFTGraph(Graph):
    def __init__(self, fft_size, fft_window_size, sample_rate, size, position, color=(255,0,0), beans=1):
        Graph.__init__(self, size, position, color)
        self.fft_size = fft_size
        self.fft_window_size = fft_window_size
        self.samples = CircularBuffer(self.fft_window_size, 0.) # For saving incoming samples before compute FFT
        self.x_axis_len = (fft_size/2+1)  # For rfft only! This function does not compute the negative frequency terms,
                                          # and the length of the transformed axis of the output is therefore n/2+1
        self.beans = 1 #beans
        self.ffted_data = [0] * self.x_axis_len
        self._color = color
        self._amplification = 1
        self.sample_rate = sample_rate
        self.h_scale = 1.0
        self.h_position = 0.0 # 0.0 to the left, 1.0 to the right

        self.grid = Grid(h_lines=4, v_lines=4, size=size, position=position)

        vertexs = self._vertex_list_from_samples(self.samples)
        colors = flatten([self._color for x in range(self.x_axis_len)])
        self._vertex_list = pyglet.graphics.vertex_list(self.x_axis_len, ('v2f\stream', vertexs), ("c3B\static", colors))

        self.freq_per_h_division = self.sample_rate/2 * float(self.grid.h_sep) / float(self.width) * self.h_scale
        self.freq_per_h_division_label = pyglet.text.Label(str(self.freq_per_h_division)+ "Hz/div",
                          font_size=12, x=size[0]/2.0 + position[0], y=position[1]- 10, anchor_x='center', anchor_y='center')

    def _vertex_list_from_samples(self, samples):
        rfft = numpy.fft.rfft(self.samples, self.fft_size)
        norm_abs_rfft = numpy.abs(rfft) * self._amplification
        self.ffted_data = norm_abs_rfft
        x_axis = numpy.arange(self.x_axis_len) * self.h_scale * self.width / float(self.x_axis_len)
        if self.beans > 1:
            padding = self.ffted_data.size % self.beans
            aux = self.ffted_data[:-padding]
            aux.shape = (self.ffted_data.size /self.beans, self.beans)
            self.ffted_data = numpy.repeat(numpy.mean(aux, 1), self.beans+1)[:self.ffted_data.size]

        vertex_list = numpy.column_stack((x_axis, self.ffted_data)).flatten()
        return vertex_list

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.x_axis_len = (fft_size/2+1)
        self.ffted_data = [0] * self.x_axis_len
        self.samples = CircularBuffer(self.fft_window_size, 0.)
        self._vertex_list.resize(self.x_axis_len)
        self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)
        self._vertex_list.colors = flatten([self._color for x in range(self.x_axis_len)])

    def set_fft_window_size(self, fft_window_size):
        self.fft_window_size = fft_window_size
        self.samples = CircularBuffer(self.fft_window_size, 0.)
        self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)

    def get_amplification(self):
        return self._amplification

    def set_amplification(self, amplification):
        self._amplification = amplification

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.freq_per_h_division = self.sample_rate/2 * float(self.grid.h_sep) / float(self.width) * self.h_scale
        self.freq_per_h_division_label.text = str(self.freq_per_h_division)+ "Hz/div"

    def draw(self):
        self.grid.draw()
        gl.glPushMatrix()
        gl.glTranslatef(self.position[0], self.position[1], 0)
        #pyglet.gl.glScissor(self.position[0], self.position[1], self.width, self.heigth+1)
        #pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
        #pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)
        gl.glPopMatrix()
        self.freq_per_h_division_label.draw()

    def add_samples(self, samples):
        """
        Add a list of samples to the graph. If acumulated samples are equal or grater than fft_window_size
        the FFT is calculated, the graph updated and acumulated data cleaned.
        """
        need_to_do_FFT = False
        if len(samples) + self.samples._index >= self.fft_window_size:
            need_to_do_FFT = True
        self.samples.put(samples)
        if need_to_do_FFT:
            self._vertex_list.vertices = self._vertex_list_from_samples(self.samples)
    amplification = property(get_amplification, set_amplification)

class StreamWidget(object):
    def __init__(self, n_samples, size, position, color):
        self.graph = StreamGraph(n_samples, size, position, color)
        self.size = size
        self.position = position

        self.gui_frame = Frame(Theme(os.path.join(PATH, "themes/pywidget")), w=2000, h=2000)
        config_gui = Dialogue('Control 1', x=self.position[0], y=self.size[1]+self.position[1]+200, content=
            VLayout(hpadding=0, children=[
                #Label(".                                       ."),
                FoldingBox('H settings', content=
                    HLayout(children=[
                        Label('sam/div: ', hexpand=False),
                        TextInput(text="", action = lambda x:self.graph.set_samples_per_h_division(float(x.text)))
                    ])
                ),
                FoldingBox('V settings', content=
                    VLayout(children=[
                        HLayout(children=[
                            Label('val/div', hexpand=False),
                            TextInput(text='100', action = lambda x:self.graph.set_values_per_v_division(float(x.text)))
                        ]),
                        HLayout(children=[
                            Label('position:', halign='right'),
                            Slider(w=100, min=0.0, max=1.0, value=0.5, action=lambda x:self.graph.set_v_position(x.value)),
                        ])

                    ])
                )
            ])
        )
        self.gui_frame.add(config_gui)

    def draw(self):
       self.graph.draw()
       self.gui_frame.draw()

    def set_n_samples(self, n_samples):
        "Resize samples per widget"
        self.graph.set_n_samples(n_samples)


class BrowsableStreamWidget(object):
    def __init__(self, n_samples, size, position, color):
        self.graph = BrowsableStreamGraph(n_samples, size, position, color)
        self.size = size
        self.position = position

        self.gui_frame = Frame(Theme(os.path.join(PATH, "themes/pywidget")), w=2000, h=2000) # w, h ?
        config_gui = Dialogue('Control 1', x=self.position[0], y=self.size[1]+self.position[1]+200, content=
            VLayout(hpadding=0, children=[
                #Label(".                                       ."),
                FoldingBox('H settings', content=
                    VLayout(children=[
                        HLayout(children=[
                            Label('sam/div: ', hexpand=False),
                            TextInput(text="", action = lambda x:self.graph.set_samples_per_h_division(float(x.text)))
                        ]),
                        HLayout(children=[
                            Label('position:', halign='right'),
                            Slider(w=100, min=0.0, max=1.0, value=0., action=lambda x:self.graph.set_h_position(x.value)),
                        ])
                    ])

                ),
                FoldingBox('V settings', content=
                    VLayout(children=[
                        HLayout(children=[
                            Label('val/div', hexpand=False),
                            TextInput(text='100', action = lambda x:self.graph.set_values_per_v_division(float(x.text)))
                        ]),
                        HLayout(children=[
                            Label('position:', halign='right'),
                            Slider(w=100, min=0.0, max=1.0, value=0.5, action=lambda x:self.graph.set_v_position(x.value)),
                        ])

                    ])
                )
            ])
        )
        self.gui_frame.add(config_gui)

    def draw(self):
       self.graph.draw()
       self.gui_frame.draw()

    def set_n_samples(self, n_samples):
        "Resize samples per widget"
        raise NotImplementedError


class MultipleStreamWidget(object):
    def __init__(self, n_graphs, n_samples, size, position, colors=None):
        if not colors:
            colors = [(255,0,90) for g in range(n_graphs)]
        cfg = {"n_samples":n_samples, "size":size, "position":position, "colors":colors}
        self.graph = MultipleStreamGraph(n_graphs, cfg)
        self.size = size

    def draw(self):
       self.graph.draw()

    def set_n_samples(self, n_samples):
        "Resize samples per widget"
        self.graph.set_n_samples(n_samples)


class FFTWidget(object):
    def __init__(self, fft_size, fft_window_size, sample_rate, size, position):
        self.graph = FFTGraph(fft_size, fft_window_size, sample_rate, size, position, (255,0,90))
        self.size = size
        self.position = position
        self.gui_frame = Frame(Theme(os.path.join(PATH, "themes/pywidget")), w=2000, h=2000)

        config_gui = Dialogue('Control 2', x=self.position[0], y=self.size[1]+self.position[1]+200, content=
            VLayout(hpadding=0, children=[
                Label(".                                                                        ."),
            #    FoldingBox('signal settings', content=
            #        VLayout(children=[
            #            HLayout(children=[
            #                Label('sample rate: ', hexpand=False),
            #                TextInput(text=str(sample_rate), action = lambda x:self.graph.set_sample_rate(int(x.text))),
            #                Label('Hz', hexpand=False),
            #            ]),
            #        ])
            #    ),
                FoldingBox('FFT settings', content=
                    HLayout(children=[
                        HLayout(children=[
                            Label('window size: ', hexpand=False),
                            TextInput(text=str(fft_window_size), action = lambda x:self.graph.set_fft_window_size(int(x.text)))
                        ]),
                        HLayout(children=[
                            Label('fft size: ', hexpand=False),
                            TextInput(text=str(fft_size), action = lambda x:self.graph.set_fft_size(int(x.text)))
                        ]),

                    ])
                ),
                FoldingBox('V settings', content=
                    VLayout(children=[
                        HLayout(children=[
                            Label('amplification: ', hexpand=False),
                            TextInput(text='1', action = lambda x:self.graph.set_amplification(float(x.text)))
                        ]),
                    ])
                )
            ])
        )
        self.gui_frame.add(config_gui)

    def draw(self):
       self.graph.draw()
       self.gui_frame.draw()

