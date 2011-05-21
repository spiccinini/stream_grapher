import sys, os, math
import numpy as np
from PyQt4 import QtCore, QtGui, QtOpenGL, uic
from OpenGL import GL as gl
from OpenGL import GLU as glu

from widgets.grid import Grid
from widgets.stream_graph import StreamGraph

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # This is always the same
        uifile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'qtui/main.ui')
        uic.loadUi(uifile, self)
        self.ui = self
        widget = MyGLDrawer(self)
        self.setCentralWidget(widget)

class MyGLDrawer(QtOpenGL.QGLWidget):
    def __init__(self, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.grid = Grid(h_lines=3, v_lines=3, size=(0.9, 0.9), position=(0, 0))
        self.graph = StreamGraph(n_samples=10, size=(0.9, 0.9), position=(-0.5, -0.5), color=(255,255,255))

    def initializeGL(self):
        gl.glViewport(0, 0, 800, 600)
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_LINE_SMOOTH)

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
        #self.grid.draw()
        import random
        self.graph.add_samples([random.random()])
        self.graph.draw()

def main():
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

