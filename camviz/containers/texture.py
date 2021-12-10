
import cv2
import numpy as np
import pygame
from OpenGL.GL import \
    glEnable, glDisable, glTexParameterf, \
    glBindTexture, glGenTextures, glTexImage2D, glTexSubImage2D, \
    GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_TEXTURE_MAG_FILTER, \
    GL_TEXTURE_MIN_FILTER, GL_REPEAT, GL_NEAREST, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE

from camviz.utils.types import is_str, is_tensor, is_numpy, is_tuple


def load(image):
    """
    Load an image as a texture surface

    Parameters
    ----------
    image : np.array or str
        Input image
    Returns
    -------
    surface : pygame surface
        Output surface for texture buffer
    """
    # Return None if image is None
    if image is None:
        return None
    # If image is a string, load from file
    if is_str(image):
        surface = pygame.image.load(image)
    # If it's a numpy array
    else:
        #  Convert to uint8 and transpose
        image = image.astype(np.uint8)
        image = np.transpose(image, (1, 0, 2))
        # Create surface
        surface = pygame.surfarray.make_surface(image)
    # Return surface
    return pygame.image.tostring(surface, "RGBA", 1)


class Texture:
    """
    Initialize a texture buffer

    Parameters
    ----------
    data : np.array [N,D] or tuple (n,d)
        Data to be added to the buffer
        If it's a tuple, create a data buffer of that size
    """
    def __init__(self, data=None):
        # Create a new texture ID
        self.id = glGenTextures(1)
        # If data exists create texture buffer from it
        if data is not None:
            self._create(data)
        # Otherwise, just store dimensions
        else:
            self.wh = None

    def process(self, image):
        """Process a new image to produce a texture buffer"""
        # If it's a tensor
        if is_tensor(image):
            # Detach and transpose
            image = image.detach().cpu().numpy()
            if len(image.shape) == 4:
                image = image[0]
            if len(image.shape) == 3 and image.shape[0] == 3:
                image = image.transpose((1, 2, 0))
        # If it's a numpy array
        if is_numpy(image):
            # Resize to proper shape
            if image.shape[0] != self.wh[0] or image.shape[1] != self.wh[1]:
                image = cv2.resize(image, self.wh, interpolation=cv2.INTER_LINEAR)
            # Squeeze if necessary
            if len(image.shape) == 3 and image.shape[2] == 1:
                image = image.squeeze(-1)
            # Stack to 3 channels if necessary
            if len(image.shape) == 2:
                image = np.stack([image] * 3, axis=2)
        # Return image
        return image * 255

    def _create(self, data):
        """Create a texture buffer from data"""
        # If it's tuple, it only contains dimensions
        if is_tuple(data):
            image = None
            w, h = data[:2]
        # If it's a tensor, convert to numpy
        elif is_tensor(data):
            image = data.detach().cpu().numpy().transpose(1, 2, 0) * 255
            h, w = data.shape[-2:]
        # Otherwise, it contains data and dimensions
        else:
            image = data * 255
            h, w = data.shape[:2]
        # Store dimensions
        self.wh = (int(w), int(h))
        # Bind and fill texture
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.wh[0], self.wh[1],
                     0, GL_RGBA, GL_UNSIGNED_BYTE, load(image))
        glBindTexture(GL_TEXTURE_2D, 0)
        # Return image
        return image

    def update(self, image):
        """Update texture buffer from an image"""
        # Return None if image is None
        if image is None:
            return None
        # If there are no stored dimensions, create a new texture buffer
        if self.wh is None:
            self._create(image)
        # Otherwise, update texture buffer
        else:
            # Process image
            image = self.process(image)
            # Bind and update buffer
            glBindTexture(GL_TEXTURE_2D, self.id)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.wh[0], self.wh[1],
                            GL_RGBA, GL_UNSIGNED_BYTE, load(image))
            glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self):
        """Bind and store data in texture buffer"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S     , GL_REPEAT )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T     , GL_REPEAT )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER , GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER , GL_NEAREST)

    @staticmethod
    def unbind():
        """Unbind texture buffer"""
        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
