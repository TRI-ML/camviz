
import pygame
from pygame.locals import *
from PIL import Image, ImageOps
import time

from camviz.draw_input import DrawInput
from camviz.draw_texture import DrawTexture
from camviz.draw_buffer import DrawBuffer

from camviz.screen2Dimage import Screen2Dimage
from camviz.screen3Dworld import Screen3Dworld

from camviz.opengl_shapes import *
from camviz.utils import *


class Draw(DrawInput, DrawTexture, DrawBuffer):

    def __init__(self, wh, rc=None, title=None):
        """
        Draw constructor
        :param wh: width and height of window
        :param rc: number of row and columns (multiplying wh)
        """
        super(Draw, self).__init__()

        pygame.display.init()
        if title is not None:
            pygame.display.set_caption(title)

        self.wh = self.curr_color = self.curr_size = self.curr_width = None
        self.screens, self.textures, self.buffers = {}, {}, {}
        self.idx_screen = None

        self.setSize(wh, rc)
        self.color('whi').size(1).width(1)

    def setSize(self, wh, rc=None):
        if rc is not None:
            wh = (wh[0] * rc[1], wh[1] * rc[0])
        self.wh = wh
        pygame.display.set_mode(self.wh, DOUBLEBUF|OPENGL)

    def __getitem__(self, name):
        return self.screen(name)

    def scr(self, name): return self.screens[name]
    def tex(self, name): return self.textures[name]
    def buf(self, name): return self.buffers[name]

    def object(self, obj, *args, **kwargs):
        obj.display(self, *args, **kwargs)

    def to_image(self):
        x, y, w, h = 0, 0, self.wh[0], self.wh[1]
        data = glReadPixels(x, y, w, h, GL_BGR, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGB", (w, h), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return np.asarray(image)

    def currScreen(self):
        """
        Return current screen
        :return: current screen
        """
        return self.screens[self.idx_screen]

    def addScreen(self, luwh):
        """
        Add a new screen to the Draw instance
        :param luwh: left/up/width/height values
        :return: updated luwh values
        """
        l, u, w, h = luwh
        w, h = w - l, h - u

        if isinstance(l, float): l = int(l * self.wh[0])
        if isinstance(u, float): u = int(u * self.wh[1])
        if isinstance(w, float): w = int(w * self.wh[0])
        if isinstance(h, float): h = int(h * self.wh[1])

        self.idx_screen = len(self.screens)
        return l, u, w, h

    def screen(self, name):
        """
        Set a screen to be used for drawing
        :param name: name of the screen
        :return:
        """
        self.idx_screen = name

        d = self.wh[1]
        l, u, w, h = self.currScreen().luwh
        u = d - (h + u)

        glViewport(l, u, w, h)
        glScissor(l, u, w, h)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        self.currScreen().prepare()
        return self

    def add2Dimage(self, name, luwh, res=None):
        if is_tup(name):
            name = labelrc(name)
        if is_lst(name):
            for i in range(len(name)):
                luwhi = list(luwh)
                d = (luwh[3] - luwh[1]) / len(name)
                luwhi[1] = luwh[1] + i * d
                luwhi[3] = luwhi[1] + d
                for j in range(len(name[i])):
                    d = (luwh[2] - luwh[0]) / len(name[i])
                    luwhi[0] = luwh[0] + j * d
                    luwhi[2] = luwhi[0] + d
                    self.add2Dimage(name[i][j], luwhi, res)
        else:
            self.screens[name] = Screen2Dimage(self.addScreen(luwh), res)

    def add3Dworld(self, name, luwh, wh=None, K=None, nf=None, pose=None, ref='cam'):
        if is_tup(name):
            name = labelrc(name)
        if is_lst(name):
            for i in range(len(name)):
                luwhi = list(luwh)
                d = (luwh[3] - luwh[1]) / len(name)
                luwhi[1] = luwh[1] + i * d
                luwhi[3] = luwhi[1] + d
                for j in range(len(name[i])):
                    d = (luwh[2] - luwh[0]) / len(name[i])
                    luwhi[0] = luwh[0] + j * d
                    luwhi[2] = luwhi[0] + d
                    self.add3Dworld(name[i][j], luwhi, wh, K, nf, ref)
        else:
            self.screens[name] = Screen3Dworld(self.addScreen(luwh), wh, K, nf, ref)
        if ref == 'lid':
            self.screens[name].viewer.rotateY(-90).rotateZ(90)
        if pose is not None:
            self.screens[name].viewer.setPose(pose)

    @staticmethod
    def clear():
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    def populate(self, dict, fit=False):
        for key, val in dict.items():
            if is_tup(val): self.screen(key).image(val[0], data=val[1], fit=fit)
            else: self.screen(key).image(key, data=val, fit=fit)

    def size(self, n):
        self.curr_size = 1
        setPointSize(n)
        return self

    def width(self, n):
        self.curr_width = n
        setLineWidth(n)
        return self

    def color(self, clr):
        self.curr_color = clr
        setColor(clr)
        return self

    def setCSW(self, csw):
        self.color(csw[0]).size(csw[1]).width(csw[2])

    def getCSW(self):
        return self.curr_color, self.curr_size, self.curr_width

    def halt(self, n):
        time.sleep(n/1000)

    def save(self, fname):
        width, height = self.wh
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGBA", (width, height), data)
        image = ImageOps.flip(image)  # in my case image is flipped top-bottom for some reason
        image.save(fname, 'PNG')
