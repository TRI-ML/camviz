# Copyright 2023 Toyota Research Institute.  All rights reserved.

from OpenGL.GL import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW
from OpenGL.GL import glMatrixMode, glLoadIdentity, glDisable
from OpenGL.GLU import gluOrtho2D

from camviz.screen.screen import Screen


class Screen2Dimage(Screen):
    """
    2D screen for image display

    Parameters
    ----------
    luwh : tuple
        Left/up/width/height values
    res : tuple
        Image resolution
    """
    def __init__(self, luwh, res):
        super().__init__(luwh, '2D_IMAGE')
        # Get resolution from dimensions if not provided
        if res is None:
            res = (self.luwh[2], self.luwh[3])
        # Initialize values
        self.setRes(res)
        self.orig_res = list(self.res)
        self.background = 'whi'

    def setRes(self, res):
        """Set new resolution"""
        self.res = [0, 0, res[0], res[1]]
        self.prepare()

    def prepare(self):
        """Prepare screen for display"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        gluOrtho2D(self.res[0], self.res[2],
                   self.res[3], self.res[1])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def printText(self, wh, string):

        import OpenGL.GL as gl
        import OpenGL.GLUT as glut

        width, height = wh
        line_height = 5

        # font = glut.GLUT_BITMAP_HELVETICA_18
        font = glut.GLUT_BITMAP_TIMES_ROMAN_24

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gluOrtho2D(self.res[0], self.res[2],
                   self.res[3], self.res[1])

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glColor3f(1, 1, 1)

        gl.glRasterPos2i(width, height + line_height)

        for ch in string:
            if ch == '\n':
                height = height + line_height
                gl.glRasterPos2i(width, height + line_height)
            else:
                glut.glutBitmapCharacter(font, ord(ch))

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
