from PyQt4 import QtOpenGL

from OpenGL import GL as gl

class QGLDrawer(QtOpenGL.QGLWidget):
    def __init__(self, parent, graph):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.graph = graph

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
        self.graph.draw()
