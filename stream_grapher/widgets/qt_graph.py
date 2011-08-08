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

from PyQt4 import QtOpenGL, QtGui, QtCore, uic
from OpenGL import GL as gl

from controls_qt import control_map

class QGLDrawer(QtOpenGL.QGLWidget):
    def __init__(self, graph, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.graph = graph

    def initializeGL(self):
        gl.glViewport(0, 0, 800, 600)
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        #gl.glEnable(gl.GL_LINE_SMOOTH) # Antialiasing

    def resizeGL(self, w, h):
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glEnable(gl.GL_BLEND)
        self.graph.draw()

    def update(self):
        self.updateGL()

class QGLDrawerHScroll(QtGui.QWidget):
    def __init__(self, graph, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.graph = graph
        self.gldrawer = QGLDrawer(graph)

        self.h_scroll = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        self.h_scroll.sliderMoved.connect(lambda x: self.graph.set_h_position(x/100.))
        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(self.gldrawer)
        vlayout.addWidget(self.h_scroll)
        self.setLayout(vlayout)

    def update(self):
        self.gldrawer.updateGL()

class Widget(QtGui.QWidget):
    def __init__(self, graph, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.graph = graph
        self.gldrawer = QGLDrawer(graph)

        self.config_dialog = QtGui.QDialog()
        uifile = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../qtui/config_dialog.ui')
        uic.loadUi(uifile, self.config_dialog)

        dialog_layout = self.config_dialog.groupBox.layout()
        if hasattr(graph, "controls"):
            for control in graph.controls:
                ctrl_widget_cls = control_map[control.__class__]
                dialog_layout.addRow(QtGui.QLabel(control.name.capitalize()),
                                     ctrl_widget_cls(graph, control))

            #self.config_dialog.setLayout(QtGui.QVBoxLayout())
            #self.config_dialog.layout().addWidget(self.controls)

            self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

            configure_action = QtGui.QAction("Configure widget", self)
            configure_action.triggered.connect(lambda : self.config_dialog.show())
            self.addAction(configure_action)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.gldrawer)
        self.setLayout(layout)



    def update(self):
        self.gldrawer.updateGL()

