
from OpenGL.GL import glMatrixMode, glLoadIdentity, glDisable
from OpenGL.GL import GL_PROJECTION, GL_DEPTH_TEST, GL_MODELVIEW
from OpenGL.GLU import gluOrtho2D

from camviz.screen.screen import Screen


class Screen2Dimage(Screen):

    def __init__(self, luwh, res):
        super().__init__(luwh, '2D_IMAGE')
        if res is None:
            res = (self.luwh[2], self.luwh[3])
        self.setRes(res)
        self.orig_res = list(self.res)
        self.background = 'whi'

    def setRes(self, res):
        self.res = [0, 0, res[0], res[1]]
        self.prepare()

    def prepare( self ):

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        gluOrtho2D(self.res[0], self.res[2],
                   self.res[3], self.res[1])

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

