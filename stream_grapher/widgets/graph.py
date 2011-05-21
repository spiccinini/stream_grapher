import numpy as np
import OpenGL.arrays.vbo
from OpenGL import GL as gl

def draw_lines_vbo(vbo, primitive):
    vbo.copied = False # TODO: We are copying the whole VBO every time!!
    vbo.bind()
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
    gl.glVertexPointerf(vbo)
    gl.glDrawArrays(primitive, 0, len(vbo.data))
    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    vbo.unbind()

class Graph(object):
    def __init__(self, size, position, color):
        self.size = size
        self.width = size[0]
        self.heigth = size[1]
        self.position = position
        self.color = color

    def draw(self):
        raise NotImplementedError

class DrawableLineStrip(object):
    def __init__(self, vertices):
        self.vertices = vertices
        self.vertices_x = vertices[:,0]
        self.vertices_y = vertices[:,1]
        self._vbo = OpenGL.arrays.vbo.VBO(data=vertices, usage='GL_STREAM_COPY_ARB')

    def draw(self):
        draw_lines_vbo(self._vbo, gl.GL_LINE_STRIP)

    def __repr__(self):
        return repr(self.vertices)

    def resize(self, size):
        self.vertices = np.zeros((size, 2), dtype="float32")
        self.vertices_x = self.vertices[:,0]
        self.vertices_y = self.vertices[:,1]
        self._vbo = OpenGL.arrays.vbo.VBO(data=self.vertices, usage='GL_STREAM_COPY_ARB')

