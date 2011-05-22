﻿#!/usr/bin/env python
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
import sys
import pickle

import numpy
import pyglet

from connection import PatchBay

try:
    f = open("config.py", "r")
except IOError:
    print >> sys.stderr, "You must write a config.py. See the README."
    sys.exit(1)
import config

window_config = pyglet.gl.Config(**config.DISPLAY.pop("gl_config"))
window = pyglet.window.Window(config=window_config, **config.DISPLAY)
fps_display = pyglet.clock.ClockDisplay()

try:
    conf = pickle.load(open("conf.bin", "r"))
    for widget in config.widgets:
        graph = widget.graph
        if hasattr(graph, "load"):
            try:
                graph.load(conf[graph.name])
            except KeyError:
                pass
except IOError:
    pass

for widget in config.widgets:
    if hasattr(widget, "gui_frame"):
        window.push_handlers(widget.gui_frame)

@window.event
def on_draw():
    window.clear()
    pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
    pyglet.gl.glLoadIdentity()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glLineWidth(1)
    for widget in config.widgets:
        widget.draw()
    fps_display.draw()

event_loop = pyglet.app.EventLoop()
@event_loop.event
def on_exit():
    for backend in config.backends:
        backend.stop()
    event_loop.exit()

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

pyglet.clock.schedule_interval(update, 1/60.)

# Some backends (eg: pyjack) need initializaction after all machinery is running.
for backend in config.backends:
    backend.start()

event_loop.run()


conf = {}
for widget in config.widgets:
    graph = widget.graph
    if hasattr(graph, "dump"):
        d = graph.dump()
        conf[graph.name] = d

conf_file = pickle.dump(conf, open("conf.bin", "w"))