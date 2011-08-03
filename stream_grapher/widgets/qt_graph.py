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

from PyQt4 import QtOpenGL, QtGui, QtCore

from OpenGL import GL as gl

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

    def updateGL(self):
        self.gldrawer.updateGL()
