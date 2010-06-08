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
from stream_widgets import StreamWidget,MultipleStreamWidget

backend = raw_input("Choose backend: 1 = Spiro,  2 = x^3, 3 = multiple x^3: ")
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

import pyglet
from pyglet.window import key
import random, math

SIZE = (1024, 768)
N_SAMPLES = 350

config = pyglet.gl.Config(double_buffer=True, buffer_size=24)
window = pyglet.window.Window(SIZE[0], SIZE[1], config=config)
#window.set_vsync(False)
fps_display = pyglet.clock.ClockDisplay()

if backend == "multiple-math":
    stream_widget1 = MultipleStreamWidget(2, N_SAMPLES, (600,600), (100, 100))
    stream_widget1.graph[1].color = (0, 0, 255)
    stream_widget1.graph[1].amplification = 0.5
    stream_widget1.graph[1].position = (100, 200)
    
    stream_widget1.graph[0].amplification = 0.5
    stream_widget1.graph[0].position = (100, -100)
else:
    stream_widget1 = StreamWidget(N_SAMPLES, (600,600), (100, 100))

@window.event
def on_draw():
    window.clear()
    stream_widget1.redraw()
    fps_display.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    pass

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.RIGHT: # Increase sample per screen in 20%
        n_samples = stream_widget1.graph.n_samples
        stream_widget1.graph.set_n_samples(int(math.ceil(n_samples + n_samples*0.2 )))
    elif symbol == key.LEFT: # Decrease sample per screen in 20%
        n_samples = stream_widget1.graph.n_samples
        new_n_samples = int(n_samples - n_samples*0.2)
        if new_n_samples > 1:
            stream_widget1.graph.set_n_samples(new_n_samples)
    elif symbol == key.UP:
        old_amplification = stream_widget1.graph.amplification
        stream_widget1.graph.set_amplification(old_amplification + old_amplification * 0.4)
    elif symbol == key.DOWN:
        old_amplification = stream_widget1.graph.amplification
        stream_widget1.graph.set_amplification(old_amplification - old_amplification * 0.4)



def update(dt):
    if backend == "math":
        stream_widget1.graph.add_samples([t**3/4.0 for t in range(-10,11)])
    elif backend == "spiro":
        samples = spiro.get_remaining_samples()
        print samples, len(samples)
        out_file.write("\n".join([str(sample) for sample in samples])+"\n")
        stream_widget1.graph.add_samples([filt_45hz_2nd(sample)/90.0 for sample in samples])
    elif backend == "multiple-math":
        stream_widget1.graph.add_samples([[t**3/4.0 for t in range(-10,11)] for i in range(3)])

pyglet.clock.schedule_interval(update, 0.05)

pyglet.app.run()
