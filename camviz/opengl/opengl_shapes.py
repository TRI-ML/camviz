# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np
from OpenGL.GL import \
    glPointSize, glLineWidth, glVertex2fv, glVertex3fv, \
    glPushMatrix, glPopMatrix, glMultMatrixf, glScalef, glBegin, glEnd, \
    GL_LINES, GL_LINE_LOOP
from OpenGL.GLU import \
    gluSphere, gluNewQuadric

from camviz.opengl.opengl_colors import Green, Blue, Red
from camviz.utils.utils import numpyf, add_list
from camviz.utils.types import is_numpy, is_double_list


def vertex_line(pt1, pt2):
    """Create line vertices"""
    glVertex = glVertex2fv if len(pt1) == 2 else glVertex3fv
    glVertex(pt1)
    glVertex(pt2)

def has_multiple(data):
    """Checks if data has multiple entries (list of lists or (n,d) numpy array)"""
    return (is_numpy(data) and len(data.shape) > 1) or is_double_list(data)

def setPointSize(n=1):
    """Set point size"""
    glPointSize(n)

def setLineWidth(n=1):
    """Set line width"""
    glLineWidth(n)

def drawLine(pt1, pt2):
    """Draw a line from two points"""
    glBegin(GL_LINES)
    vertex_line(pt1, pt2)
    glEnd()

def drawMatches(pts1, pts2):
    """Draw 1 to 1 matches between two sets of points"""
    glBegin(GL_LINES)
    for i in range(len(pts1)):
        vertex_line([pts1[i, 0], pts1[i, 1], pts1[i, 2]],
                    [pts2[i, 0], pts2[i, 1], pts2[i, 2]])
    glEnd()

def drawConnects(vert1, verts2):
    """Draw connections from each vert1 to all vert2"""
    vert1, verts2 = numpyf(vert1), numpyf(verts2)
    glBegin(GL_LINES)
    for vert2 in verts2:
        vertex_line(vert1, vert2)
    glEnd()

def drawRect(lu=None, rd=None, ct=None, wh=None, x=False):
    """
    Draw a rectangle

    Parameters
    ----------
    lu : np.array
        Left/Up point
    rd : np.array
        Right/Down point
    ct : np.array
        Center point
    wh : np.array
        Width/height
    x : bool
        Draw an x inside the rectangle
    """
    # If no center is provided, get border points
    if ct is not None and wh is not None:
        lu = [ct[0] - wh[0] / 2, ct[1] - wh[1] / 2]
        rd = [ct[0] + wh[0] / 2, ct[1] + wh[1] / 2]
        ld, ru = [lu[0], rd[1]], [rd[0], lu[1]]
    # Else, get points based on center
    elif lu is not None:
        if rd is not None:
            ld, ru = [lu[0], rd[1]], [rd[0], lu[1]]
        elif wh is not None:
            ld, ru = [lu[0], lu[1] + wh[1]], \
                     [lu[0] + wh[0], rd[1]]
    # Wrong parameters
    else:
        raise ValueError('wrong drawRect parameters')
    # Draw rectangle
    glBegin(GL_LINE_LOOP)
    vertex_line(lu, ld)
    vertex_line(rd, ru)
    # Draw x
    if x:
        vertex_line(lu, rd)
        vertex_line(ld, ru)
    glEnd()

def drawCross(ct, sz):
    """
    Draw a cross on screen

    Parameters
    ----------
    ct : np.array
        Cross center
    sz : float
        Cross size
    """
    # If there are multiple centers, draw one cross for each
    if has_multiple(ct):
        [drawCross(pt, sz) for pt in ct]
    # If there is a single center
    else:
        # Get borders
        u, d = ct[1] - sz / 2, ct[1] + sz / 2
        l, r = ct[0] - sz / 2, ct[0] + sz / 2
        # Draw cross
        glBegin(GL_LINES)
        vertex_line([l, ct[1]], [r, ct[1]])
        vertex_line([ct[0], u], [ct[0], d])
        glEnd()

def drawAxis(scale=1.0, center=(0, 0, 0), width=None):
    """
    Draw a xyz axis on screen

    Parameters
    ----------
    scale : float
        Axis scale
    center : np.array
        Axis center
    width : int
        Axis line width
    """
    # Set width if provided
    if width is not None:
        setLineWidth(width)
    # Convert center to numpy
    center = numpyf(center)
    # Draw axis
    glBegin(GL_LINES)
    Green()
    vertex_line(center, add_list(center, (scale, 0, 0)))
    Blue()
    vertex_line(center, add_list(center, (0, scale, 0)))
    Red()
    vertex_line(center, add_list(center, (0, 0, scale)))
    glEnd()

def drawEllipse(mean, cov):
    """
    Draw an ellipse on screen

    Parameters
    ----------
    mean : np.array
        Ellipse mean
    cov : np.array
        Ellipse covariance
    """
    # If there are multiple means, draw one ellipse for each
    if len(mean.shape) > 1:
        for i in range(mean.shape[0]):
            drawEllipse(mean[i], cov[i])
    # Else, draw a single ellipse
    else:
        # Get eigenvalue and eigenvector
        val, vec = np.linalg.eig(cov)
        # Get transformation matrix
        Tt = np.eye(4)
        Tt[:3, :3] = vec
        Tt[3, :3] = mean
        # Apply transformation matrix and draw
        glPushMatrix()
        glMultMatrixf(Tt)
        glScalef(2.0 * np.sqrt(val[0]),
                 2.0 * np.sqrt(val[1]),
                 2.0 * np.sqrt(val[2]))
        gluSphere(gluNewQuadric(), 1.00, 100, 20)
        glPopMatrix()
