
import cv2
import pygame
import numpy as np

from OpenGL.GL import \
    glEnable, glDisable, glTexParameterf, \
    glBindTexture, glGenTextures, glTexImage2D, glTexSubImage2D, \
    GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_TEXTURE_MAG_FILTER, \
    GL_TEXTURE_MIN_FILTER, GL_REPEAT, GL_NEAREST, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE
from camviz.utils.types import is_str, is_tct, is_npy, is_tup


def load(image):

    if image is None:
        return None
    if is_str(image):
        surface = pygame.image.load(image)
    else:
        image = image.astype(np.uint8)
        image = np.transpose(image, (1, 0, 2))
        surface = pygame.surfarray.make_surface(image)
    return pygame.image.tostring(surface, "RGBA", 1)


class Texture:

    def __init__(self, data=None):

        self.id = glGenTextures(1)
        if data is not None:
            self._create(data)
        else:
            self.wh = None

    def process(self, image):
        if is_tct(image):
            image = image.detach().cpu().numpy()
            if len(image.shape) == 3:
                image = image.transpose((1, 2, 0))
        if is_npy(image):
            if image.shape[0] != self.wh[0] or image.shape[1] != self.wh[1]:
                image = cv2.resize(image, self.wh, interpolation=cv2.INTER_LINEAR)
            if len(image.shape) == 3 and image.shape[2] == 1:
                image = image.squeeze(-1)
            if len(image.shape) == 2:
                image = np.stack([image] * 3, axis=2)
        return image

    def _create(self, data):

        if is_tup(data):
            image, (w, h) = None, data[:2]
        else:
            image, (h, w) = data, data.shape[:2]
        self.wh = (int(w), int(h))

        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.wh[0], self.wh[1],
                     0, GL_RGBA, GL_UNSIGNED_BYTE, load(image))
        glBindTexture(GL_TEXTURE_2D, 0)
        return image

    def update(self, image):

        if image is None:
            return None

        if self.wh is None:
            self._create(image)
        else:
            image = self.process(image)

            glBindTexture(GL_TEXTURE_2D, self.id)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.wh[0], self.wh[1],
                            GL_RGBA, GL_UNSIGNED_BYTE, load(image))
            glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self):

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S     , GL_REPEAT )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T     , GL_REPEAT )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER , GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER , GL_NEAREST)

    @staticmethod
    def unbind():

        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
