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
from stream_widgets import StreamWidget, MultipleStreamWidget, FFTWidget
import pyglet
from pyglet.window import key
from simplui import Frame, Theme, Dialogue, VLayout, Label, Button, \
                    TextInput, HLayout, FlowLayout, FoldingBox, Slider
import random, math, os

SIZE = (1024, 768)
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
from backends.math import Math as Cubic
cubic_generator = Cubic(ports=1, sample_rate=300)
backends.append(cubic_generator)

stream_widget = StreamWidget(N_SAMPLES, size=(400,400), position=(100, 100), color=(255,0,0))
fft_widget = FFTWidget(1024, 1024, sample_rate=300, size=(400,400), position=(550, 100))
widgets.extend([stream_widget, fft_widget])

PatchBay.connect(src=cubic_generator, src_port=1, out=stream_widget, out_port=1)
PatchBay.connect(src=cubic_generator, src_port=1, out=fft_widget, out_port=1)


# create a frame to contain our gui, the full size of our window
frame = Frame(Theme(os.path.join(".", "themes/pywidget")), w=SIZE[0], h=SIZE[1])
window.push_handlers(frame)

dialogue_control_1= Dialogue('Control 1', x=100, y=700, content=
    VLayout(hpadding=0, children=[
        #Label(".                                       ."),
        FoldingBox('H settings', content=
            HLayout(children=[
                Label('sam/div: ', hexpand=False),
                TextInput(text="", action = lambda x:stream_widget1.graph.set_samples_per_h_division(float(x.text)))
            ])
        ),
        FoldingBox('V settings', content=
            VLayout(children=[
                HLayout(children=[
                    Label('val/div', hexpand=False), 
                    TextInput(text='100', action = lambda x:stream_widget1.graph.set_values_per_v_division(float(x.text)))
                ]),
                HLayout(children=[
                    Label('position:', halign='right'), 
                    Slider(w=100, min=0.0, max=1.0, value=0.5, action=lambda x:stream_widget1.graph.set_v_position(x.value)),
                ])
                
            ])
        )
    ])
)

dialogue_control_2= Dialogue('Control 2', x=550, y=700, content=
    VLayout(hpadding=0, children=[
        Label(".                                                                        ."),
        FoldingBox('signal settings', content=
            VLayout(children=[
                HLayout(children=[
                    Label('sample rate: ', hexpand=False),
                    TextInput(text="1", action = lambda x:fft_widget.graph.set_sample_rate(int(x.text))),
                    Label('Hz', hexpand=False),
                ]),
            ])
        ),
        FoldingBox('FFT settings', content=
            HLayout(children=[
                HLayout(children=[
                    Label('window size: ', hexpand=False),
                    TextInput(text="1024", action = lambda x:fft_widget.graph.set_fft_window_size(int(x.text)))
                ]),
                HLayout(children=[
                    Label('fft size: ', hexpand=False),
                    TextInput(text="1024", action = lambda x:fft_widget.graph.set_fft_size(int(x.text)))
                ]),
                
            ])
        ),
        FoldingBox('V settings', content=
            VLayout(children=[
                HLayout(children=[
                    Label('amplification: ', hexpand=False), 
                    TextInput(text='1', action = lambda x:fft_widget.graph.set_amplification(float(x.text)))
                ]),                
            ])
        )
    ])
)

frame.add(dialogue_control_1)
frame.add(dialogue_control_2)

@window.event
def on_draw():
    window.clear()
    for widget in widgets:
        widget.draw()
    frame.draw()
    fps_display.draw()

def update(dt):
    for backend in backends:
        samples = backend.get_remaining_samples()
        for connection in PatchBay.connections:
            if connection.src is backend:
                try:
                    out_samples = [sample[connection.src_port] for sample in samples]
                except TypeError:
                    out_samples = samples
                # Todo output_ports
                connection.out.graph.add_samples(out_samples)
        
pyglet.clock.schedule(update)

pyglet.app.run()
