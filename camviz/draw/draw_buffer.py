# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np
from OpenGL.GL import glEnableClientState, glDisableClientState, \
    glPolygonMode, glVertexPointer, glBindBuffer, glColorPointer, \
    glDrawArrays, glDrawElements, glBegin, glEnd, glVertex2fv, glVertex3fv, \
    GL_ARRAY_BUFFER, GL_FILL, GL_ELEMENT_ARRAY_BUFFER, \
    GL_FLOAT, GL_UNSIGNED_INT, GL_POINTS, GL_FRONT_AND_BACK, GL_COLOR_ARRAY, \
    GL_VERTEX_ARRAY, GL_LINE, GL_LINES, GL_LINE_LOOP, GL_LINE_STRIP, GL_QUADS, GL_TRIANGLES

from camviz.containers.buffer import Buffer
from camviz.opengl.opengl_shapes import drawConnects, drawMatches, drawAxis, drawEllipse
from camviz.utils.utils import grid_idx
from camviz.utils.types import is_str, is_list, is_tuple, is_int
from camviz.utils.cmaps import jet


class drawBuffer:
    """Draw subclass containing data buffer methods"""
    def __init__(self):
        pass

    def addBuffer(self, name, data, dtype, gltype, n=None):
        """
        Create a new data buffer

        Parameters
        ----------
        name : str
            Buffer name
        data : np.array [N,D] or tuple (n,d)
            Data to be added to the buffer
            If it's a tuple, create a data buffer of that size
        dtype : numpy type (e.g. np.float32)
            Numpy data type
        gltype : OpenGL type (e.g. GL_FLOAT32)
            OpenGL data type
        n : int or tuple
            Number of textures to be added
        """
        # If it's a list, create one buffer for each item
        if is_list(name):
            for i in range(len(name)):
                self.addBuffer(name[i], data[i] if is_list(data) else data, dtype, gltype)
        # Otherwise, create a single buffer
        else:
            if n is not None:
                if is_tuple(n):
                    for i in range(n[0]):
                        for j in range(n[1]):
                            self.buffers['%s%d%d' % (name, i, j)] = Buffer(data, dtype, gltype)
                elif is_int(n):
                    for i in range(n):
                        self.buffers['%s%d' % (name, i)] = Buffer(data, dtype, gltype)
            self.buffers[name] = Buffer(data, dtype, gltype)

    def addBufferf(self, name, data=0):
        """Create a buffer with float32 values (2D or 3D is determined from data)"""
        self.addBuffer(name, data, np.float32, GL_FLOAT)

    def addBufferu(self, name, data=0):
        """Create a buffer with unsigned 32 values (2D or 3D is determined from data)"""
        self.addBuffer(name, data, np.uint32, GL_UNSIGNED_INT)

    def addBuffer2f(self, name, data=0, n=None):
        """Create a 2D empty buffer with float32 values"""
        self.addBuffer(name, (data, 2), np.float32, GL_FLOAT, n)

    def addBuffer3f(self, name, data=0, n=None):
        """Create a 3D empty buffer with float32 values"""
        self.addBuffer(name, (data, 3), np.float32, GL_FLOAT, n)

    def addbufferIDX(self, name, data=0):
        """Create an index buffer for shape drawing"""
        self.addBufferu(name, grid_idx(data))

    def addBufferJET(self, name, data=0):
        """Create a JET colormap buffer from data"""
        self.addBufferf(name, jet(data))

    def addBuffer3JET(self, name, data=0):
        """Create an empty 3D colormap buffer from data"""
        self.addBuffer3f(name, data)

    def updBufferf(self, name, data):
        """Update a buffer with float32 values"""
        self.buffers[name].update(data)

    def clrBuffer(self, name):
        """Clear a buffer"""
        self.buffers[name].clear()

    def points(self, *args, **kwargs):
        """Draw points"""
        return self._drawSomething(GL_POINTS, *args, **kwargs)

    def lines( self, *args, **kwargs):
        """Draw lines"""
        return self._drawSomething(GL_LINES, *args, **kwargs)

    def strips(self, *args, **kwargs):
        """Draw strips (connecting adjacent vertices)"""
        return self._drawSomething(GL_LINE_STRIP, *args, **kwargs)

    def loop(  self, *args, **kwargs):
        """Draw loops (strips with last vertices connected)"""
        return self._drawSomething(GL_LINE_LOOP, *args, **kwargs)

    def quads( self, *args, **kwargs):
        """Draw quadratics"""
        return self._drawSomething(GL_QUADS, *args, **kwargs)

    def tris(  self, *args, **kwargs):
        """Draw triangles"""
        return self._drawSomething(GL_TRIANGLES, *args, **kwargs)

    def grid(  self, *args, **kwargs):
        """Draw a grid"""
        return self._drawSomething(GL_QUADS, *args, **kwargs)

    def matches(self, *args, **kwargs):
        """Draw matches from two sets of points"""
        drawMatches(*args, **kwargs)
        return self

    def connects(self, *args, **kwargs):
        """Draw a connection from one point to many points"""
        drawConnects(*args, **kwargs)
        return self

    def axis(self, *args, **kwargs):
        """Draw coordinate axis"""
        drawAxis(*args, **kwargs)
        return self

    def ellipse(self, *args, **kwargs):
        """Draw ellipse"""
        drawEllipse(*args, **kwargs)
        return self

    def _drawSomething(self, shape, *args, **kwargs):
        """
        Base function for shape drawing

        Parameters
        ----------
        shape : opengl shape
            OpenGL shape to draw (e.g. GL_POINTS)
        args : args
            Extra draw arguments
        kwargs : kwargs
            Extra draw arguments
        """
        # If it's a string, draw buffer
        if is_str(args[0]):
            return self._drawBuffer(shape, *args, **kwargs)
        # Otherwise, copy data and draw
        else:
            return self._drawBase(shape, *args, **kwargs)

    def _drawBuffer(self, shape, vert, color=None, idx=None, wire=None):
        """
        Draw from a buffer

        Parameters
        ----------
        shape : opengl type
            OpenGL shape to draw (e.g. GL_POINTS)
        vert : buffer
            Buffer with vertices
        color : buffer
            Buffer with colors
        idx : buffer
            Buffer with indexes
        wire : buffer
            Buffer with wire (color and width)
        """
        # If wire is avaialble
        if wire is not None:
            csw = self.getCSW()
            self.width(wire[1])
            color_wire = wire[0] if wire[0] in self.buffers else None
            if wire[0] not in self.buffers:
                self.color(wire[0])
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            self._drawBuffer(shape, vert, color=color_wire, idx=idx, wire=None)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            self.setCSW(csw)
        # If vert is available
        if vert is not None:
            vert = self.buffers[vert]
            glEnableClientState(GL_VERTEX_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, vert.id)
            glVertexPointer(vert.d, vert.gltype, 0, None)
        # If color is available
        if color is not None:
            color = self.buffers[color]
            glEnableClientState(GL_COLOR_ARRAY)
            glBindBuffer(GL_ARRAY_BUFFER, color.id)
            glColorPointer(color.d, color.gltype, 0, None)
        # If idx is available
        if idx is None:
            glDrawArrays(shape, 0, vert.n)
        else:
            idx = self.buffers[idx]
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, idx.id)
            glDrawElements(shape, idx.n, idx.gltype, None)
        # Bind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        # Unbind vertices
        if vert is not None:
            glDisableClientState(GL_VERTEX_ARRAY)
        # Unbind colors
        if color is not None:
            glDisableClientState(GL_COLOR_ARRAY)
        # Return self
        return self

    def _drawBase(self, shape, verts):
        """
        Draw a shape by copying data (very slow)

        Parameters
        ----------
        shape : opengl shape
            OpenGL shape to draw (e.g. GL_POINTS)
        verts : np.array
            Vertices to draw
        """
        # If there are no vertices, do nothing
        if len(verts) == 0:
            return self
        # Select 2D or 3D vertex draw function
        glVertex = glVertex2fv if len(verts[0]) == 2 else glVertex3fv
        # Draw vertices
        glBegin(shape)
        for vert in verts:
            glVertex(vert)
        glEnd()
        # Return self
        return self
