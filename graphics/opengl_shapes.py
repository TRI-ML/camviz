
import numpy as np
from graphics.utils import numpyf, add_list
from graphics.opengl_colors import *

from OpenGL.GL import *
from OpenGL.GLU import *

def has_multiple(data):
    return (isinstance(data, np.ndarray) and len(data.shape) > 1) or \
           (isinstance(data, list) and isinstance(data[0], list))


def setPointSize(n=1): glPointSize(n)
def setLineWidth(n=1): glLineWidth(n)


def drawLine(pt1, pt2):
    glVertex = glVertex2fv if len(pt1) == 2 else glVertex3fv
    glBegin(GL_LINES)
    glVertex(pt1); glVertex(pt2)
    glEnd()


def drawMatches(pts1, pts2):
    glVertex = glVertex2fv if len(pts1[0]) == 2 else glVertex3fv
    glBegin(GL_LINES)
    for i in range(len(pts1)):
        glVertex([pts1[i,0], pts1[i,1], pts1[i,2]])
        glVertex([pts2[i,0], pts2[i,1], pts2[i,2]])
    glEnd()


def drawConnects(vert1, verts2):
    vert1, verts2 = numpyf(vert1), numpyf(verts2)
    glVertex = glVertex2fv if len(vert1) == 2 else glVertex3fv
    glBegin(GL_LINES)
    for vert in verts2:
        glVertex(vert1); glVertex(vert)
    glEnd()


def drawRect(lu=None, rd=None, ct=None, wh=None, x=False):
    if ct is not None and wh is not None:
        lu = [ct[0]-wh[0]/2, ct[1]-wh[1]/2]
        rd = [ct[0]+wh[0]/2, ct[1]+wh[1]/2]
        ld, ru = [lu[0], rd[1]], [rd[0], lu[1]]
    elif lu is not None:
        if rd is not None:
            ld, ru = [lu[0], rd[1]], [rd[0], lu[1]]
        elif wh is not None:
            ld, ru = [lu[0], lu[1]+wh[1]], [lu[0]+wh[0], rd[1]]
    glBegin(GL_LINE_LOOP)
    glVertex2fv(lu); glVertex2fv(ld)
    glVertex2fv(rd); glVertex2fv(ru)
    if x:
        glVertex2fv(lu); glVertex2fv(rd)
        glVertex2fv(ld); glVertex2fv(ru)
    glEnd()


def drawCross(ct, sz):
    if has_multiple(ct):
        for pt in ct:
            drawCross(pt, sz)
    else:
        u, d = ct[1] - sz/2, ct[1] + sz/2
        l, r = ct[0] - sz/2, ct[0] + sz/2
        glBegin(GL_LINES)
        glVertex2fv([l, ct[1]]); glVertex2fv([r, ct[1]])
        glVertex2fv([ct[0], u]); glVertex2fv([ct[0], d])
        glEnd()


def drawAxis(scale=1.0, center=(0, 0, 0), width=None):
    if width is not None: setLineWidth(width)
    center = numpyf(center)

    glBegin(GL_LINES)
    Green(); glVertex3fv(center); glVertex3fv(add_list(center, (scale, 0, 0)))
    Blue();  glVertex3fv(center); glVertex3fv(add_list(center, (0, scale, 0)))
    Red();   glVertex3fv(center); glVertex3fv(add_list(center, (0, 0, scale)))
    glEnd()


def drawEllipse(mean, cov):

    if len(mean.shape) > 1:
        for i in range(mean.shape[0]):
            drawEllipse(mean[i], cov[i])
    else:
        val, vec = np.linalg.eig(cov)

        Tt = np.eye(4)
        Tt[:3, :3] = vec
        Tt[3, :3] = mean

        glPushMatrix()
        glMultMatrixf(Tt)
        glScalef(2.0 * np.sqrt(val[0]), 2.0 * np.sqrt(val[1]), 2.0 * np.sqrt(val[2]))
        gluSphere(gluNewQuadric(), 1.00, 100, 20)
        glPopMatrix()

