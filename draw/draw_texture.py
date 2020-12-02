
from OpenGL.GL import \
    glTexCoord2f, glBegin, glEnd, glVertex2fv, glVertex3fv, \
    GL_QUADS

from camviz.texture import Texture
from camviz.opengl.opengl_colors import White
from camviz.utils.types import is_tup, is_lst
from camviz.utils.utils import labelrc, numpyf


class DrawTexture:

    def addTexture(self, name, data=None):
        if is_tup(name):
            name = labelrc(name)
        if is_lst(name):
            for i in range(len(name)):
                self.addTexture(name[i], data[i] if is_lst(data) else data)
        else:
            self.textures[name] = Texture(data)

    def updTexture(self, name, data):
        self.textures[name].update(data)

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

        White()
        tex.bind()
        glBegin(GL_QUADS)
        glVertex = glVertex2fv if len(verts[0]) == 2 else glVertex3fv
        glTexCoord2f(1.0, 1.0); glVertex(verts[0])
        glTexCoord2f(1.0, 0.0); glVertex(verts[1])
        glTexCoord2f(0.0, 0.0); glVertex(verts[2])
        glTexCoord2f(0.0, 1.0); glVertex(verts[3])
        glEnd()
        tex.unbind()

        return self

