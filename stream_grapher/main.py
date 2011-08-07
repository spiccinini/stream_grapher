# -*- coding: UTF-8 -*-

# Copyright (C) 2011  Santiago Piccinini
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

import os
import imp
import numpy as np
from PyQt4 import QtCore, QtGui, uic

from stream_grapher.connection import PatchBay

DRAW_FPS = 60

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self, config_filename):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        uifile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'qtui/main.ui')
        uic.loadUi(uifile, self)

        config = imp.load_source('config', config_filename)
        self.config = config

        for widget in self.config.widgets:
            self.central_layout.addWidget(widget)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(1000/float(DRAW_FPS))

    def on_actionPlay_toggled(self, checked):
        if checked:
            self.update_timer.start()
            for backend in self.config.backends:
                backend.start()
        else:
            self.update_timer.stop()
            for backend in self.config.backends:
                backend.stop()

    def update(self):
        for backend in self.config.backends:
            samples = backend.get_remaining_samples()
            for connection in PatchBay.connections:
                if connection.src is backend:
                    samples = np.asarray(samples)
                    if samples.size != 0:
                        out_samples = samples[connection.src_port-1]
                    else:
                        out_samples = samples
                    if connection.out_port:
                        connection.out.graph.add_samples(out_samples, connection.out_port-1)
                    else:
                        connection.out.graph.add_samples(out_samples)

        for widget in self.config.widgets:
            widget.updateGL()
