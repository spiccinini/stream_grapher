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

from stream_graph import StreamGraph
from controls import ColorControl, FloatControl, IntControl


class MultipleStreamGraph(object):

    controls = [
        FloatControl("values_per_v_division", "/div", "values per vertical division"),
        FloatControl("samples_per_h_division", "samples/div", "samples per division"),
    ]

    def __init__(self, n_graphs, n_samples, size, position, colors):
        self.n_graphs = n_graphs
        self.stream_graphs = [StreamGraph(n_samples, size, position, colors[i]) for i in range(n_graphs)]

        class FakeGrid(object):
            def __init__(self):
                self.h_sep = 100
                self.v_sep = 100
                self.h_lines = 3
                self.v_lines = 3

            def draw(self): pass

        for graph in self.stream_graphs[:-1]: # Only need to draw 1 grid
            graph.grid.draw = lambda : None

        class _SequenceView(object):
            def __init__(self, getter, setter):
                self._getter = getter
                self._setter = setter

            def __getitem__(self, key):
                return self._getter(key)

            def __setitem__(self, key, value):
                return self._setter(key, value)

        sample_getter = lambda key: self._get_samples().__getitem__(key)
        sample_setter = lambda key, value: self._get_samples().__setitem__(key, value)

        self.samples = _SequenceView(sample_getter, sample_setter)

        spacing = 1 / float(n_graphs+1)
        spacings = [spacing*n for n in range(1, n_graphs+1)][::-1]
        for n, graph in enumerate(self.stream_graphs):
            graph.v_position =  spacings[n]

        self._samples_per_h_division = self.stream_graphs[0].samples_per_h_division
        self._values_per_v_division = self.stream_graphs[0].values_per_v_division

        # Build controls dinamicaly
        self.controls = self.controls[:]
        self._graphs_controls = {}

        for i, graph in enumerate(self.stream_graphs):
            port = i+1
            color_name = "port_%d_color" %  port
            v_position_name = "port_%d_v_position" % port
            color_ctrl = ColorControl(color_name,
                                      display_name="Port %d color" % port)
            v_position_ctrl = FloatControl(v_position_name,
                                           display_name="Port %d V postion" % port)
            self.controls.append(("Port %d" % port, [color_ctrl, v_position_ctrl]))

            self._graphs_controls[color_name] = (lambda : graph.color,
                                                 graph.set_color)
            self._graphs_controls[v_position_name] = (lambda :graph.v_position,
                                                      graph.set_v_position)

    def draw(self):
        for graph in self.stream_graphs:
            graph.draw()

    def add_samples(self, samples_array, n_graph=None):
        "Add a list of samples to each graph"
        samples = np.asarray(samples_array)
        if samples.size != 0:
            if n_graph is not None:
                self.stream_graphs[n_graph].add_samples(samples)
            else:
                samples_array = samples
                for i, graph in enumerate(self.stream_graphs):
                    graph.add_samples(samples_array[i])

    def __getitem__(self, key):
        return self.stream_graphs[key]

    def _get_samples(self):
        length = len(self.stream_graphs[0].samples)
        samples = np.zeros((self.n_graphs, length))
        for i, graph in enumerate(self.stream_graphs):
            samples[i] = graph.samples[:]
        return samples.transpose()

    def set_samples_per_h_division(self, value):
        self._samples_per_h_division = value
        for graph in self.stream_graphs:
            graph.samples_per_h_division = value

    def set_values_per_v_division(self, value):
        self._values_per_v_division = value
        for graph in self.stream_graphs:
            graph.values_per_v_division = value

    def __getattr__(self, attr):
        if attr in self._graphs_controls:
            return self._graphs_controls[attr][0]()
        else:
            raise AttributeError, attr

    def __setattr__(self, attr, value):
        if attr == "_graphs_controls":
            object.__setattr__(self, attr, value)
        elif attr.startswith("port_"):
            self._graphs_controls[attr][1](value)
        else:
            object.__setattr__(self, attr, value)

    samples_per_h_division = property(lambda self: self._samples_per_h_division,
                                      set_samples_per_h_division)
    values_per_v_division = property(lambda self: self._values_per_v_division,
                                      set_values_per_v_division)
