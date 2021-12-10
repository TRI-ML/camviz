# Copyright 2021 Toyota Research Institute.  All rights reserved.

import time

import numpy as np
import pygame
from OpenGL.GL import glReadPixels, glViewport, glScissor, \
    glClear, glClearColor, glPixelStorei, \
    GL_BGR, GL_UNSIGNED_BYTE, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, \
    GL_PACK_ALIGNMENT, GL_RGBA
from PIL import Image, ImageOps
from pygame.locals import *

from camviz.draw.draw_buffer import drawBuffer
from camviz.draw.draw_input import DrawInput
from camviz.draw.draw_texture import DrawTexture
from camviz.opengl.opengl_colors import setColor
from camviz.opengl.opengl_shapes import setPointSize, setLineWidth
from camviz.screen.screen2Dimage import Screen2Dimage
from camviz.screen.screen3Dworld import Screen3Dworld
from camviz.utils.types import is_tuple, is_list
from camviz.utils.utils import labelrc


class Draw(DrawInput, DrawTexture, drawBuffer):

    def __init__(self, wh, rc=None, title=None, scale=1.0, width=1600):
        """
        Draw class for display visualization

        Parameters
        ----------
        wh : tuple (width, height)
            Window dimensions
        rc : tuple (row, column)
            Number of rows and columns (multiplying wh)
        title : str
            Window title
        scale : float
            Scale for width/height window dimensions
        """
        super().__init__()
        # Initialize pygame display
        pygame.init()
        # Initialize title
        if title is not None:
            pygame.display.set_caption(title)
        # Initialize parameters
        wh = [int(val * scale) for val in wh]
        if width is not None:
            wh[0], wh[1] = width, width * wh[1] // wh[0]
        self.wh = self.curr_color = self.curr_size = self.curr_width = None
        self.screens, self.textures, self.buffers = {}, {}, {}
        self.idx_screen = None
        # Set size and color
        self.setSize(wh, rc)
        self.color('whi').size(1).width(1)

    def setSize(self, wh, rc=None):
        """Set window size"""
        # Multiply row and column to produce correct dimensions
        if rc is not None:
            wh = (wh[0] * rc[1], wh[1] * rc[0])
        # Store dimensions
        self.wh = wh
        # Initialize display
        pygame.display.set_mode(self.wh, DOUBLEBUF|OPENGL)

    def __getitem__(self, name):
        """Get screen from name"""
        return self.screen(name)

    def scr(self, name):
        """Get screen from name"""
        return self.screens[name]

    def tex(self, name):
        """Get texture from name"""
        return self.textures[name]

    def buf(self, name):
        """Get buffer from name"""
        return self.buffers[name]

    def object(self, obj, *args, **kwargs):
        """Display object on screen"""
        obj.display(self, *args, **kwargs)

    def to_image(self):
        """Convert window into a numpy image"""
        x, y, w, h = 0, 0, self.wh[0], self.wh[1]
        data = glReadPixels(x, y, w, h, GL_BGR, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGB", (w, h), data)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return np.asarray(image)

    def currScreen(self):
        """Return current screen"""
        return self.screens[self.idx_screen]

    def addScreen(self, luwh):
        """
        Add a new screen to the draw window

        Parameters
        ----------
        luwh : tuple (left, up, width, height)
            Screen dimensions (percentage or pixels)

        Returns
        -------
        l, u, w, h : int
            Dimensions
        """
        # Parse dimensions
        l, u, w, h = luwh
        w, h = w - l, h - u
        # Convert percentages to pixels
        if isinstance(l, float):
            l = int(l * self.wh[0])
        if isinstance(u, float):
            u = int(u * self.wh[1])
        if isinstance(w, float):
            w = int(w * self.wh[0])
        if isinstance(h, float):
            h = int(h * self.wh[1])
        # Get screen index and return dimensions
        self.idx_screen = len(self.screens)
        return l, u, w, h

    def screen(self, name):
        """Set which screen will be used for drawing"""
        self.idx_screen = name
        # Get parameters
        d = self.wh[1]
        l, u, w, h = self.currScreen().luwh
        u = d - (h + u)
        # Create viewport and cropping
        glViewport(l, u, w, h)
        glScissor(l, u, w, h)
        # Set background color
        glClearColor(0.0, 0.0, 0.0, 1.0)
        # Prepare current screen
        self.currScreen().prepare()
        return self

    def add2Dimage(self, name, luwh, res=None):
        """
        Add 2D image screen

        Parameters
        ----------
        name : str
            Screen name
        luwh : tuple (left, up, width, height)
            Screen dimensions (pixels or percentage)
        res : tuple (width, height)
            Screen resolution
        """
        # If name is a tuple, create labels for rows and columns
        if is_tuple(name):
            name = labelrc(name)
        # If name is a list, create several screens
        if is_list(name):
            for i in range(len(name)):
                luwh_i = list(luwh)
                d = (luwh[3] - luwh[1]) / len(name)
                luwh_i[1] = luwh[1] + i * d
                luwh_i[3] = luwh_i[1] + d
                for j in range(len(name[i])):
                    d = (luwh[2] - luwh[0]) / len(name[i])
                    luwh_i[0] = luwh[0] + j * d
                    luwh_i[2] = luwh_i[0] + d
                    self.add2Dimage(name[i][j], luwh_i, res)
        # Else, create a single screen
        else:
            self.screens[name] = Screen2Dimage(self.addScreen(luwh), res)

    def add2DimageRow(self, name, luwh, n, res=None):
        """
        Add row with multiple 2D image screens

        Parameters
        ----------
        name : str
            Screen name
        luwh : tuple (left, up, width, height)
            Screen dimensions (pixels or percentage)
        n : int
            Number of columns in the row
        res : tuple (width, height)
            Screen resolution
        """
        for i in range(n):
            # Copy dimension vector
            luwh_i = [val for val in luwh]
            # Offset rows
            luwh_i[0] = luwh[0] + (i / n) * (luwh[2] - luwh[0])
            luwh_i[2] = luwh[0] + ((i + 1) / n) * (luwh[2] - luwh[0])
            # Create 2D image screen
            self.add2Dimage('%s%d' % (name, i), luwh_i, res)

    def add2DimageCol(self, name, luwh, n, res=None):
        """
        Add column with multiple 2D image screens

        Parameters
        ----------
        name : str
            Screen name
        luwh : tuple (left, up, width, height)
            Screen dimensions (pixels or percentage)
        n : int
            Number of rows in the column
        res : tuple (width, height)
            Screen resolution
        """
        for i in range(n):
            # Copy dimension vector
            luwh_i = [val for val in luwh]
            # Offset columns
            luwh_i[1] = luwh[1] + (i / n) * (luwh[3] - luwh[1])
            luwh_i[3] = luwh[1] + ((i + 1) / n) * (luwh[3] - luwh[1])
            # Create 2D image screen
            self.add2Dimage('%s%d' % (name, i), luwh_i, res)

    def add2DimageGrid(self, name, luwh, n, res=None):
        """
        Add grid with multiple 2D image screens

        Parameters
        ----------
        name : str
            Screen name
        luwh : tuple (left, up, width, height)
            Screen dimensions (pixels or percentage)
        n : tuple (int, int)
            Number of rows and columns in the grid
        res : tuple (width, height)
            Screen resolution
        """
        for i in range(n[0]):
            for j in range(n[1]):
                # Copy dimension vector
                luwh_i = [val for val in luwh]
                # Offset columns
                luwh_i[1] = luwh[1] + (i / n[0]) * (luwh[3] - luwh[1])
                luwh_i[3] = luwh[1] + ((i + 1) / n[0]) * (luwh[3] - luwh[1])
                # Offset rows
                luwh_i[0] = luwh[0] + (j / n[1]) * (luwh[2] - luwh[0])
                luwh_i[2] = luwh[0] + ((j + 1) / n[1]) * (luwh[2] - luwh[0])
                # Create 2D image screen
                self.add2Dimage('%s%d%d' % (name, i, j), luwh_i, res)

    def add3Dworld(self, name, luwh=(0.0, 0.0, 1.0, 1.0), **kwargs):
        """
        Add a 3D world screen

        Parameters
        ----------
        name : str
            Screen name
        luwh : tuple
            Screen dimensions (left, up, width, height), in pixels or percentage
        """
        # If name is a tuple, create labels for rows and columns
        if is_tuple(name):
            name = labelrc(name)
        # If name is a list, create several screens
        if is_list(name):
            for i in range(len(name)):
                luwh_i = list(luwh)
                d = (luwh[3] - luwh[1]) / len(name)
                luwh_i[1] = luwh[1] + i * d
                luwh_i[3] = luwh_i[1] + d
                for j in range(len(name[i])):
                    d = (luwh[2] - luwh[0]) / len(name[i])
                    luwh_i[0] = luwh[0] + j * d
                    luwh_i[2] = luwh_i[0] + d
                    self.add3Dworld(name[i][j], luwh_i, **kwargs)
        # Else, create a single screen
        else:
            self.screens[name] = Screen3Dworld(self.addScreen(luwh), **kwargs)

    @staticmethod
    def clear():
        """Clear window"""
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    def populate(self, data, fit=False):
        """
        Populate screens with information from a dictionary

        Parameters
        ----------
        data : dict
            Dictionary with information for each screen
        fit : bool
            If true, resize screens to fit the data showing
        """
        for key, val in data.items():
            # If it's a tuple, use key and val from positions 0 and 1
            if is_tuple(val):
                self.screen(key).image(val[0], data=val[1], fit=fit)
            # Else, use key and val directly
            else:
                self.screen(key).image(key, data=val, fit=fit)

    def size(self, n):
        """Set point size"""
        self.curr_size = 1
        setPointSize(n)
        return self

    def width(self, n):
        """Set line width"""
        self.curr_width = n
        setLineWidth(n)
        return self

    def color(self, clr):
        """Set plot color"""
        self.curr_color = clr
        setColor(clr)
        return self

    def setCSW(self, csw):
        """Set color, size and width (CSW) simultaneously"""
        self.color(csw[0]).size(csw[1]).width(csw[2])

    def getCSW(self):
        """Get color, size and width (CSW) information"""
        return self.curr_color, self.curr_size, self.curr_width

    @staticmethod
    def halt(n):
        """Stop for n milliseconds"""
        time.sleep(n/1000)

    def save(self, filename):
        """Save window as an image file"""
        # Get dimensions
        width, height = self.wh
        # Store window information in a variable
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGBA", (width, height), data)
        image = ImageOps.flip(image)  # in my case image is flipped top-bottom for some reason
        # Save image and halt for a bit
        image.save(filename, 'PNG')
        self.halt(1000)
