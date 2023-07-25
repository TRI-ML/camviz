# Copyright 2023 Toyota Research Institute.  All rights reserved.

import OpenGL.GL as gl
import OpenGL.GLUT as glut
import numpy as np
from OpenGL.GL import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glMatrixMode, glEnable, glDisable, glLoadIdentity, glMultMatrixf, glBlendFunc
from OpenGL.GLU import gluPerspective, gluLookAt, gluOrtho2D
from camviz.objects.pose import Pose
from camviz.screen.screen import Screen


class Screen3Dworld(Screen):
    """
    3D screen for virtual world display

    Parameters
    ----------
    luwh : tuple
        Left/up/width/height values
    wh : width/height
        Virtual camera image dimensions
    K : np.array [3,3]
        Virtual camera intrinsics
    nf : tuple
        Near/far display parameters
    background : str
        Background color ['bla', 'whi']
    pose : tuple
        Virtual camera pose
    ref : str
        Coordinate reference system ['cam', 'lidar']
    """
    def __init__(self, luwh, wh=None, K=None, nf=(0.01, 10000.0),
                 enable_blending=False, background='bla', pose=None, ref='cam'):
        super().__init__(luwh, '3D_WORLD')
        self.wh, self.K, self.nf = wh, K, nf
        self.viewer = self.origin = self.P = None
        self.enable_blending = enable_blending
        self.background = background
        self.ref = ref
        # Start and prepare screen
        self.start()
        self.prepare()
        # Rotate if using a lidar frame of reference
        if ref == 'lidar':
            self.viewer.rotateY(-90).rotateZ(90)
            self.saveViewer()
        # Set viewer pose if provided
        if pose is not None:
            self.viewer.setPose(pose)
            self.saveViewer()

    def start(self):
        """Start viewer"""
        self.viewer = Pose()
        self.origin = Pose()
        if self.wh is not None and self.K is not None:
            self.calibrate()

    def prepare(self):
        """Prepare screen for display"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.enable_blending:
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        else:
            glEnable(GL_DEPTH_TEST)

        # If calibration matrix is provided, use it
        if self.P is not None:
            glMultMatrixf(self.P)
        # Otherwise, use a default perspective
        else:
            gluPerspective(45, self.luwh[2] / self.luwh[3],
                           self.nf[0], self.nf[1])

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Determine look vector
        T = self.viewer.T
        gluLookAt(
            T[0, 3],
            T[1, 3],
            T[2, 3],
            T[0, 3] + T[0, 2],
            T[1, 3] + T[1, 2],
            T[2, 3] + T[2, 2],
            - T[0, 1],
            - T[1, 1],
            - T[2, 1],
        )

    def calibrate(self):
        """Calibrate screen for display"""
        # Convert intrinsics to numpy if needed
        if isinstance(self.K, list):
            self.K = np.array(self.K)

        # Create transformation matrix
        self.P = np.zeros(16)

        self.P[0] = 2 * self.K[0, 0] / self.wh[0]
        self.P[5] = 2 * self.K[1, 1] / self.wh[1]

        self.P[8] = 2.0 * (self.K[0, 2] / self.wh[0]) - 1.0
        self.P[9] = 2.0 * (self.K[1, 2] / self.wh[1]) - 1.0

        self.P[10] = - 1.0 * (self.nf[1] + self.nf[0]) / (self.nf[1] - self.nf[0])
        self.P[14] = - 2.0 * (self.nf[1] * self.nf[0]) / (self.nf[1] - self.nf[0])
        self.P[11] = - 1.0

        self.P = np.reshape(self.P, (4, 4))

    def text(self, text, wh):

        # font = glut.GLUT_BITMAP_HELVETICA_18
        font = glut.GLUT_BITMAP_TIMES_ROMAN_24

        width, height = wh
        line_height = 36

        if height > 0:
            height = height * line_height + 20
        elif height < 0:
            height = self.luwh[3] + (height * line_height) - 20

        width = width + 10

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gluOrtho2D(0, self.luwh[2], self.luwh[3], 0)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glColor3f(1, 1, 1)

        gl.glRasterPos2i(width, height + line_height)

        for ch in text:
            if ch == '\n':
                height = height + line_height
                gl.glRasterPos2i(width, height + line_height)
            else:
                glut.glutBitmapCharacter(font, ord(ch))

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
