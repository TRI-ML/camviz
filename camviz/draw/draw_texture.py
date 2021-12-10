# Copyright 2021 Toyota Research Institute.  All rights reserved.

from OpenGL.GL import \
    glTexCoord2f, glBegin, glEnd, glVertex2fv, glVertex3fv, \
    GL_QUADS

from camviz.containers.texture import Texture
from camviz.opengl.opengl_colors import White
from camviz.utils.utils import labelrc, numpyf
from camviz.utils.types import is_tuple, is_list, is_int

class DrawTexture:
    """Draw subclass containing texture methods"""
    def addTexture(self, name, data=None, n=None):
        """
        Create a new texture buffer

        Parameters
        ----------
        name : str
            Buffer name
        data : np.array [N,D] or tuple (n,d)
            Data to be added to the buffer
            If it's a tuple, create a data buffer of that size
        n : int or tuple
            Number of textures to be added
        """
        # If it's a tuple, create individual names for each texture
        if is_tuple(name):
            name = labelrc(name)
        # If it's a list, add each item to its own texture
        if is_list(name):
            for i in range(len(name)):
                self.addTexture(name[i], data[i] if is_list(data) else data)
        # Otherwise, create a single texture from data
        else:
            if n is not None:
                if is_tuple(n):
                    for i in range(n[0]):
                        for j in range(n[1]):
                            self.textures['%s%d%d' % (name, i, j)] = Texture(data)
                elif is_int(n):
                    for i in range(n):
                        self.textures['%s%d' % (name, i)] = Texture(data)
            self.textures[name] = Texture(data)

    def updTexture(self, name, data):
        """Update texture with new data"""
        self.textures[name].update(data)

    def image(self, name, data=None, verts=None, fit=False):
        """
        Display a texture on screen

        Parameters
        ----------
        name : str
            Name of the texture
        data : np.array
            Update texture with new data before displaying
        verts : np.array
            Vertices for the texture borders on screen
        fit : bool
            If true, resize screen to fit new image
        """
        # If no name is provided, return None
        if name is None:
            return
        # Get texture ID from name
        tex = self.textures[name]
        # Resize screen to fit screen if necessary
        if fit is True:
            self.currScreen().setRes(tex.wh)
        # If data is provided, update texture first
        if data is not None:
            tex.update(data)
        # If verts is not provided, create them based on screen dimension
        if verts is None:
            verts = [[tex.wh[0],    0.0   ], [tex.wh[0], tex.wh[1]],
                    [    0.0   , tex.wh[1]], [   0.0   ,    0.0   ]]
        verts = numpyf(verts)
        # Draw texture
        White()
        tex.bind()
        glBegin(GL_QUADS)
        glVertex = glVertex2fv if len(verts[0]) == 2 else glVertex3fv
        glTexCoord2f(1.0, 1.0)
        glVertex(verts[0])
        glTexCoord2f(1.0, 0.0)
        glVertex(verts[1])
        glTexCoord2f(0.0, 0.0)
        glVertex(verts[2])
        glTexCoord2f(0.0, 1.0)
        glVertex(verts[3])
        glEnd()
        tex.unbind()
        # Return self
        return self

