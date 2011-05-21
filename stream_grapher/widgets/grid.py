import numpy as np
from OpenGL import GL as gl
import OpenGL.arrays.vbo

from stream_grapher.utils import flatten
from graph import Graph, draw_lines_vbo

class Grid(Graph):
    def __init__(self, h_lines, v_lines, size, position, color=(100,255,100)):
        Graph.__init__(self, size, position, color)
        self.h_lines = h_lines
        self.v_lines = v_lines
        v_sep = size[0]/float(v_lines+1)
        h_sep = size[1]/float(h_lines+1)
        self.v_sep = v_sep
        self.h_sep = h_sep
        v_vertexs = np.array(flatten([(i*v_sep, 0, i*v_sep, size[1]) for i in range(1, v_lines+1)]), dtype="float32")
        v_vertexs = v_vertexs.reshape(v_vertexs.size/2, 2)

        h_vertexs = np.array(flatten([(0, i*h_sep, size[0], i*h_sep) for i in range(1, h_lines+1)]), dtype="float32")
        h_vertexs = h_vertexs.reshape(h_vertexs.size/2, 2)
        self.h_vbo = OpenGL.arrays.vbo.VBO(data=h_vertexs, usage='GL_STREAM_COPY_ARB')
        self.v_vbo = OpenGL.arrays.vbo.VBO(data=v_vertexs, usage='GL_STREAM_COPY_ARB')

        border_vertexs = np.array([[0, 0], [self.size[0], 0], [self.size[0], self.size[1]],
                                   [0, self.size[1]]], dtype="float32")
        self.border_vbo = OpenGL.arrays.vbo.VBO(data=border_vertexs, usage='GL_STREAM_COPY_ARB')

    def draw(self):

        gl.glPushMatrix()
        gl.glColor3ub(*self.color)

        gl.glLineStipple(3, 0xAAAA)
        gl.glEnable(gl.GL_LINE_STIPPLE)
        gl.glTranslatef(self.position[0], self.position[1], 0)
        draw_lines_vbo(self.h_vbo, gl.GL_LINES)
        draw_lines_vbo(self.v_vbo, gl.GL_LINES)
        gl.glDisable(gl.GL_LINE_STIPPLE)

        draw_lines_vbo(self.border_vbo, gl.GL_LINE_LOOP)
        gl.glPopMatrix()

