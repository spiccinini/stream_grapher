#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2009 Piccinini Santiago
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import itertools
import pyglet.graphics

def flatten(listOfLists):
    return list(itertools.chain.from_iterable(listOfLists))

class StreamGraph(object):
    def __init__(self, n_samples, size, y_position, color=(255,255,255), amplification=1):
        self.n_samples = n_samples
        self.samples = [0]*n_samples
        self.actual_sample_index = 0
        self.width = size[0]
        self.heigth = size[1]
        self.y_position = y_position
        self.color = color
        self.amplification = amplification
        
        vertexs = flatten([(x*self.width/float(self.n_samples),y_position) for x in range(n_samples)]) # Fixme: Hardcoded initial vertex
        colors = flatten([self.color for x in range(n_samples)])
        self._vertex_list = pyglet.graphics.vertex_list(n_samples, ('v2f\stream', vertexs), ("c3B\static", colors))

    
    def draw(self, samples):
        "Add a list of samples to the graph and then draw it"
        self.add_samples(samples)
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)

    def redraw(self):
        "Draw the graph"
        self._vertex_list.draw(pyglet.gl.GL_LINE_STRIP)

    def add_samples(self, samples):
        "Add a list of samples to the graph"
        for sample in samples:
            index = self.actual_sample_index
            self.samples[index] = sample
            new_vertex = (index*self.width/float(self.n_samples), self.y_position + self.samples[index]*self.amplification)
            self._vertex_list.vertices[index*2:index*2+2] = new_vertex
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

    def set_amplification(self, amplification):
        self.amplification = amplification
        self._regenerate_vertex_list()

    def set_color(self, color):
        colors = tuple(flatten([color for x in range(self.n_samples)])) 
        self._vertex_list.colors = colors
 
    def _regenerate_vertex_list(self):
        "Regenerates the internal vertex list from self.samples data"
        new_vertex_list = []
        for index, sample in enumerate(self.samples):
            vertex = (index*self.width/float(self.n_samples), self.y_position + self.samples[index]*self.amplification)
            new_vertex_list.extend(vertex)
        self._vertex_list.vertices = new_vertex_list

class StreamWidget(object):
    def __init__(self, n_samples, size):
        self.graph = StreamGraph(n_samples, size, size[1]/2, (255,0,90))
        self.size = size

    def draw(self, samples):
       self.graph.draw(samples)

    def redraw(self):
       self.graph.redraw()
    
    def set_n_samples(self, n_samples):
        "Resize samples per widget"
        self.graph.set_n_samples(n_samples)
