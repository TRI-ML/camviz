
import numpy as np

from OpenGL.GL import glEnableClientState, glDisableClientState, \
    glPolygonMode, glVertexPointer, glBindBuffer, glColorPointer, \
    glDrawArrays, glDrawElements, glBegin, glEnd, glVertex2fv, glVertex3fv, \
    GL_ARRAY_BUFFER, GL_FILL, GL_ELEMENT_ARRAY_BUFFER, \
    GL_FLOAT, GL_UNSIGNED_INT, GL_POINTS, GL_FRONT_AND_BACK, GL_COLOR_ARRAY, \
    GL_VERTEX_ARRAY, GL_LINE, GL_LINES, GL_LINE_LOOP, GL_LINE_STRIP, GL_QUADS, GL_TRIANGLES

from camviz.data.buffer import Buffer
from camviz.utils.types import is_lst, is_str
from camviz.utils.utils import grid_idx, cmapJET
from camviz.opengl.opengl_shapes import drawConnects, drawMatches, drawAxis, drawEllipse


class drawBuffer:

    def addBuffer(self, name, data, dtype, gltype):
        if is_lst(name):
            for i in range(len(name)):
                self.addBuffer(name[i], data[i] if is_lst(data) else data, dtype, gltype)
        else:
            self.buffers[name] = Buffer(data, dtype, gltype)

    def addBufferf(self, name, data=0):
        self.addBuffer(name, data, np.float32, GL_FLOAT)

    def addBufferu(self, name, data=0):
        self.addBuffer(name, data, np.uint32, GL_UNSIGNED_INT)

    def addBuffer2f(self, name, data=0):
        self.addBuffer(name, (data, 2), np.float32, GL_FLOAT)

    def addBuffer3f(self, name, data=0):
        self.addBuffer(name, (data, 3), np.float32, GL_FLOAT)

    def addbufferIDX(self, name, data=0):
        self.addBufferu(name, grid_idx(data))

    def addBufferJET(self, name, data=0):
        self.addBufferf(name, cmapJET(data))

    def addBuffer3JET(self, name, data=0):
        self.addBuffer3f(name, data)

    def updBufferf(self, name, data):
        self.buffers[name].update(data)

    def clrBuffer(self, name):
        self.buffers[name].clear()

    def points(self, *args, **kwargs): return self._drawSomething(GL_POINTS, *args, **kwargs)
    def lines( self, *args, **kwargs): return self._drawSomething(GL_LINES, *args, **kwargs)
    def strips(self, *args, **kwargs): return self._drawSomething(GL_LINE_STRIP, *args, **kwargs)
    def loop(  self, *args, **kwargs): return self._drawSomething(GL_LINE_LOOP, *args, **kwargs)
    def quads( self, *args, **kwargs): return self._drawSomething(GL_QUADS, *args, **kwargs)
    def tris(  self, *args, **kwargs): return self._drawSomething(GL_TRIANGLES, *args, **kwargs)
    def grid(  self, *args, **kwargs): return self._drawSomething(GL_QUADS, *args, **kwargs)

    def matches(self, *args, **kwargs):
        drawMatches(*args, **kwargs)
        return self

    def connects(self, *args, **kwargs):
        drawConnects(*args, **kwargs)
        return self

    def axis(self, *args, **kwargs):
        drawAxis(*args, **kwargs)
        return self

    def ellipse(self, *args, **kwargs):
        drawEllipse(*args, **kwargs)
        return self

    def _drawSomething(self, shape, *args, **kwargs):
        if is_str(args[0]): return self._drawBuffer(shape, *args, **kwargs)
        else: return self._drawBase(shape, *args, **kwargs)

    def _drawBuffer(self, shape, vert, color=None, idx=None, wire=None):

        if wire is not None:
            csw = self.getCSW()
            self.width(wire[1])
            color_wire = wire[0] if wire[0] in self.buffers else None
            if wire[0] not in self.buffers: self.color(wire[0])
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            self._drawBuffer(shape, vert, color=color_wire, idx=idx, wire=None)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            self.setCSW(csw)

        if vert is not None:
            vert = self.buffers[vert]
            glEnableClientState(GL_VERTEX_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, vert.id)
            glVertexPointer(vert.d, vert.gltype, 0, None)

        if color is not None:
            color = self.buffers[color]
            glEnableClientState(GL_COLOR_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, color.id)
            glColorPointer(color.d, color.gltype, 0, None)

        if idx is None:
            glDrawArrays(shape, 0, vert.n)
        else:
            idx = self.buffers[idx]
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, idx.id)
            glDrawElements(shape, idx.n, idx.gltype, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        if vert is not None: glDisableClientState(GL_VERTEX_ARRAY)
        if color is not None: glDisableClientState(GL_COLOR_ARRAY)

        return self

    def _drawBase(self, shape, verts):

        if len(verts) == 0: return self
        glVertex = glVertex2fv if len(verts[0]) == 2 else glVertex3fv

        glBegin(shape)
        for vert in verts:
            glVertex(vert)
        glEnd()

        return self
