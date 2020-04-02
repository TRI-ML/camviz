
import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from PIL import Image

from camviz.draw_input import DrawInput
from camviz.screen2Dimage import Screen2Dimage
from camviz.texture import Texture
from camviz.buffer import Buffer
from camviz.opengl_colors import *
from camviz.opengl_shapes import *
from camviz.utils import *


class DrawTexture:

    def addTexture(self, name, data=None):
        if is_tup(name):
            name = labelrc(name)
        if is_lst(name):
            for i in range(len(name)):
                self.addTexture(name[i], data[i] if is_lst(data) else data)
        else:
            self.textures[name] = Texture(data)

    def image(self, name, data=None, verts=None, fit=False):
        if name is None:
            return
        tex = self.textures[name]
        if fit is True:
            self.currScreen().setRes(tex.wh)
        if data is not None:
            tex.update(data)
        if verts is None:
            verts = [[tex.wh[0],    0.0   ], [tex.wh[0], tex.wh[1]],
                    [    0.0   , tex.wh[1]], [   0.0   ,    0.0   ]]
        verts = numpyf(verts)

        glVertex = glVertex2fv if len(verts[0]) == 2 else glVertex3fv
        White(); tex.bind(); glBegin(GL_QUADS)
        glTexCoord2f(1.0, 1.0); glVertex(verts[0])
        glTexCoord2f(1.0, 0.0); glVertex(verts[1])
        glTexCoord2f(0.0, 0.0); glVertex(verts[2])
        glTexCoord2f(0.0, 1.0); glVertex(verts[3])
        glEnd(); tex.unbind()

        return self

