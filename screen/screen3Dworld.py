
import numpy as np
from OpenGL.GL import glMatrixMode, glEnable, glLoadIdentity, glMultMatrixf
from OpenGL.GL import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW
from OpenGL.GLU import gluPerspective, gluLookAt

from camviz.screen.screen import Screen
from camviz.objects.pose import Pose


class Screen3Dworld(Screen):

    def __init__(self, luwh, wh=None, K=None, nf=(0.01, 100.0),
                 background='bla', pose=None, ref='cam'):
        super().__init__(luwh, '3D_WORLD')
        self.wh, self.K, self.nf = wh, K, nf
        self.viewer = self.origin = self.P = None
        self.background = background
        self.ref = ref

        self.start()
        self.prepare()

        if ref == 'lidar':
            self.viewer.rotateY(-90).rotateZ(90)
        if pose is not None:
            self.viewer.setPose(pose)
            self.saveViewer()

    def start(self):
        self.viewer = Pose()
        self.origin = Pose()
        if self.wh is not None and self.K is not None:
            self.calibrate()

    def prepare(self):

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glEnable(GL_DEPTH_TEST)

        if self.P is not None:
            glMultMatrixf(self.P)
        else:
            gluPerspective(45, self.luwh[2] / self.luwh[3],
                           self.nf[0], self.nf[1])

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

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

        if isinstance(self.K, list):
            self.K = np.array(self.K)

        self.P = np.zeros(16)

        self.P[0] = 2 * self.K[0, 0] / self.wh[0]
        self.P[5] = 2 * self.K[1, 1] / self.wh[1]

        self.P[8] = 2.0 * (self.K[0, 2] / self.wh[0]) - 1.0
        self.P[9] = 2.0 * (self.K[1, 2] / self.wh[1]) - 1.0

        self.P[10] = - 1.0 * (self.nf[1] + self.nf[0]) / (self.nf[1] - self.nf[0])
        self.P[14] = - 2.0 * (self.nf[1] * self.nf[0]) / (self.nf[1] - self.nf[0])
        self.P[11] = - 1.0

        self.P = np.reshape(self.P, (4, 4))
