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
from backends import pyjack
import pyglet
from pyglet.window import key
from simplui import Frame, Theme, Dialogue, VLayout, Label, Button, \
                    TextInput, HLayout, FlowLayout, FoldingBox, Slider
import random, math

backend = raw_input("Choose backend: 1 = Spiro,  2 = x^3, 3 = multiple x^3, 4 = jack: ")
if backend == "1":
    from backends.spiro_com import Spiro
    com = raw_input("COM port:")
    spiro = Spiro(port=com, timeout=0.5)
    spiro.run()
    backend = "spiro"
    out_file = open("data.log", "w")
    from filters.iir_filter import IIRFilter
    filt_45hz_2nd = IIRFilter((1.0, 2.0, 1.0),(1.0, -1.6692031429, 0.7166338735))

elif backend== "2":
    backend = "math"
elif backend == "3":
    backend = "multiple-math"
elif backend == "4":
    backend = "jack"
    #jack_backend = pyjack.Jack()



SIZE = (1024, 768)
N_SAMPLES = 350

config = pyglet.gl.Config(double_buffer=True, buffer_size=24)
window = pyglet.window.Window(SIZE[0], SIZE[1], config=config)


window.set_vsync(False)
fps_display = pyglet.clock.ClockDisplay()

if backend == "multiple-math":
    stream_widget1 = MultipleStreamWidget(2, N_SAMPLES, (600,600), (100, 100))
    stream_widget1.graph[1].color = (0, 0, 255)
    stream_widget1.graph[1].amplification = 0.5
    stream_widget1.graph[1].position = (100, 200)

    stream_widget1.graph[0].amplification = 0.5
    stream_widget1.graph[0].position = (100, -100)
    fft_widget = FFTWidget(1024, 1024, sample_rate=1.0, size=(400,400), position=(550, 100))
elif backend in ["spiro", "math", "jack"]:
    stream_widget1 = StreamWidget(N_SAMPLES, size=(400,400), position=(100, 100), color=(255,0,0))
    fft_widget = FFTWidget(1024, 1024, sample_rate=1.0, size=(400,400), position=(550, 100))

# create a frame to contain our gui, the full size of our window
frame = Frame(Theme('/home/san/somecode/stream_grapher_fft/themes/pywidget'), w=SIZE[0], h=SIZE[1])
window.push_handlers(frame)

def show_position(slider):
    print slider.value
    

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
    if backend != "jack":
        pass
    stream_widget1.draw()
    frame.draw()
    fft_widget.draw()
    fps_display.draw()

def update(dt):
    if backend == "math":
        stream_widget1.graph.add_samples([1 for t in range(-10,10)])
        stream_widget1.graph.add_samples([-1 for t in range(-10,10)])
        fft_widget.graph.add_samples([1 for t in range(-10,80)])
        fft_widget.graph.add_samples([-1 for t in range(-10,80)])
    if backend == "jack":
        samples = jack_backend.get_remaining_samples()
        stream_widget1.graph.add_samples(samples)
        fft_widget.graph.add_samples(samples)
    elif backend == "spiro":
        samples = spiro.get_remaining_samples()
        print samples, len(samples)
        out_file.write("\n".join([str(sample) for sample in samples])+"\n")
        stream_widget1.graph.add_samples([filt_45hz_2nd(sample)/90.0 for sample in samples])
    elif backend == "multiple-math":
        stream_widget1.graph.add_samples([[t**3/4.0 for t in range(-10,11)] for i in range(3)])

pyglet.clock.schedule(update)

if backend == "jack":
    jack_backend = pyjack.Jack()

pyglet.app.run()
