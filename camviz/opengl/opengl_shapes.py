
import numpy as np

from OpenGL.GL import \
    glPointSize, glLineWidth, glVertex2fv, glVertex3fv, \
    glPushMatrix, glPopMatrix, glMultMatrixf, glScalef, glBegin, glEnd, \
    GL_LINES, GL_LINE_LOOP
from OpenGL.GLU import \
    gluSphere, gluNewQuadric

from camviz.utils.types import is_lst, is_npy
from camviz.utils.utils import numpyf, add_list
from camviz.opengl.opengl_colors import Green, Blue, Red


def vertex_line(pt1, pt2):
    glVertex = glVertex2fv if len(pt1) == 2 else glVertex3fv
    glVertex(pt1)
    glVertex(pt2)


def has_multiple(data):
    return (is_npy(data) and len(data.shape) > 1) or \
           (is_lst(data) and is_lst(data[0]))


def setPointSize(n=1):
    glPointSize(n)


def setLineWidth(n=1):
    glLineWidth(n)


def drawLine(pt1, pt2):
    glBegin(GL_LINES)
    vertex_line(pt1, pt2)
    glEnd()


def drawMatches(pts1, pts2):
    glBegin(GL_LINES)
    for i in range(len(pts1)):
        vertex_line([pts1[i,0], pts1[i,1], pts1[i,2]],
                    [pts2[i,0], pts2[i,1], pts2[i,2]])
    glEnd()


def drawConnects(vert1, verts2):
    vert1, verts2 = numpyf(vert1), numpyf(verts2)
    glBegin(GL_LINES)
    for vert2 in verts2:
        vertex_line(vert1, vert2)
    glEnd()


def drawRect(lu=None, rd=None, ct=None, wh=None, x=False):
    if ct is not None and wh is not None:
        lu = [ct[0] - wh[0] / 2, ct[1] - wh[1] / 2]
        rd = [ct[0] + wh[0] / 2, ct[1] + wh[1] / 2]
        ld, ru = [lu[0], rd[1]], [rd[0], lu[1]]
    elif lu is not None:
        if rd is not None:
            ld, ru = [lu[0], rd[1]], [rd[0], lu[1]]
        elif wh is not None:
            ld, ru = [lu[0], lu[1] + wh[1]], \
                     [lu[0] + wh[0], rd[1]]
    else:
        raise ValueError('wrong drawRect parameters')
    glBegin(GL_LINE_LOOP)
    vertex_line(lu, ld)
    vertex_line(rd, ru)
    if x:
        vertex_line(lu, rd)
        vertex_line(ld, ru)
    glEnd()


def drawCross(ct, sz):
    if has_multiple(ct):
        [drawCross(pt, sz) for pt in ct]
    else:
        u, d = ct[1] - sz / 2, ct[1] + sz / 2
        l, r = ct[0] - sz / 2, ct[0] + sz / 2
        glBegin(GL_LINES)
        vertex_line([l, ct[1]], [r, ct[1]])
        vertex_line([ct[0], u], [ct[0], d])
        glEnd()


def drawAxis(scale=1.0, center=(0, 0, 0), width=None):
    if width is not None:
        setLineWidth(width)
    center = numpyf(center)

    glBegin(GL_LINES)
    Green(); vertex_line(center, add_list(center, (scale, 0, 0)))
    Blue();  vertex_line(center, add_list(center, (0, scale, 0)))
    Red();   vertex_line(center, add_list(center, (0, 0, scale)))
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
        glScalef(2.0 * np.sqrt(val[0]),
                 2.0 * np.sqrt(val[1]),
                 2.0 * np.sqrt(val[2]))
        gluSphere(gluNewQuadric(), 1.00, 100, 20)
        glPopMatrix()

