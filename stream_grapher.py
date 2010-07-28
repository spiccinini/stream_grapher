#!/usr/bin/env python
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

''' A "real-time" stream grapher.
'''
from stream_widgets import StreamWidget, MultipleStreamWidget, FFTWidget, BrowsableStreamWidget
import pyglet


SIZE = (1024, 700)
N_SAMPLES = 350

config = pyglet.gl.Config(double_buffer=True, buffer_size=24)
window = pyglet.window.Window(SIZE[0], SIZE[1], config=config)


window.set_vsync(False)
fps_display = pyglet.clock.ClockDisplay()

class Connection(object):
    def __init__(self, src, src_port, out, out_port):
        self.src = src
        self.src_port = src_port
        self.out = out
        self.out_port = out_port

class PatchBay(object):
    connections = []
    @classmethod
    def connect(cls, src, src_port, out, out_port):
        cls.connections.append(Connection(src, src_port, out, out_port))

backends = []
widgets = []

# Configuration
from backends.maths import Math as Cubic
from backends.sthocastic import Brownian
sample_generator  = Cubic(ports=1, sample_rate=300)

backends.append(sample_generator)

stream_widget = StreamWidget(N_SAMPLES, size=(400,400), position=(100, 100), color=(255,0,0))
fft_widget = FFTWidget(1024, 1024, sample_rate=300, size=(400,400), position=(550, 100))
b_stream_widget = BrowsableStreamWidget(N_SAMPLES, size=(400,400), position=(100, 100), color=(255,0,0))
widgets.extend([fft_widget,stream_widget])

PatchBay.connect(src=sample_generator, src_port=1, out=stream_widget, out_port=1)
PatchBay.connect(src=sample_generator, src_port=1, out=fft_widget, out_port=1)
PatchBay.connect(src=sample_generator, src_port=1, out=b_stream_widget, out_port=1)


for widget in widgets:
    try:
        window.push_handlers(widget.gui_frame)
    except AttributeError: # Does not have GUI
        pass

@window.event
def on_draw():
    window.clear()
    for widget in widgets:
        widget.draw()
    fps_display.draw()

def update(dt):
    for backend in backends:
        samples = backend.get_remaining_samples()
        for connection in PatchBay.connections:
            if connection.src is backend:
                try:
                    out_samples = [sample[connection.src_port] for sample in samples]
                except (TypeError, IndexError):
                    out_samples = samples
                # Todo output_ports
                connection.out.graph.add_samples(out_samples)

pyglet.clock.schedule(update)

pyglet.app.run()
