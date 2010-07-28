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
import pyglet
import numpy
from connection import PatchBay
try:
    import config
except ImportError:
    import config_example as config

window_config = pyglet.gl.Config(**config.DISPLAY.pop("gl_config"))
window = pyglet.window.Window(config=window_config, **config.DISPLAY)
fps_display = pyglet.clock.ClockDisplay()

for widget in config.widgets:
    try:
        window.push_handlers(widget.gui_frame)
    except AttributeError: # Does not have GUI
        pass

@window.event
def on_draw():
    window.clear()
    for widget in config.widgets:
        widget.draw()
    fps_display.draw()

def update(dt):
    for backend in config.backends:
        samples = backend.get_remaining_samples()
        for connection in PatchBay.connections:
            if connection.src is backend:
                samples = numpy.asarray(samples)
                if samples.size != 0:
                    out_samples = samples.transpose()[connection.src_port-1]
                else:
                    out_samples = samples
                if connection.out_port:
                    connection.out.graph.add_samples(out_samples, connection.out_port-1)
                else:
                    connection.out.graph.add_samples(out_samples)

pyglet.clock.schedule(update)

pyglet.app.run()
