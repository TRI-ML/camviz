# Copyright 2023 Toyota Research Institute.  All rights reserved.

from OpenGL.GL import glColor3fv, glColor4fv


def Red(n=1.0, a=1.0):
    """Change to red color"""
    glColor4fv((n, 0.0, 0.0, a))


def Green(n=1.0, a=1.0):
    """Change to green color"""
    glColor4fv((0.0, n, 0.0, a))


def Blue(n=1.0, a=1.0):
    """Change to blue color"""
    glColor4fv((0.0, 0.0, n, a))


def Yellow(n=1.0, a=1.0):
    """Change to yellow color"""
    glColor4fv((n, n, 0.0, a))


def Magenta(n=1.0, a=1.0):
    """Change to magenta color"""
    glColor4fv((n, 0.0, n, a))


def Cyan(n=1.0, a=1.0):
    """Change to cyan color"""
    glColor4fv((0.0, n, n, a))


def Black(a=1.0):
    """Change to black color"""
    glColor4fv((0.0, 0.0, 0.0, a))


def White(a=1.0):
    """Change to white color"""
    glColor4fv((1.0, 1.0, 1.0, a))


def Gray(a=1.0):
    """Change to gray color"""
    glColor4fv((0.5, 0.5, 0.5, a))


def setColor(clr, n=1.0, a=1.0):
    """Change to an specific color based on a string"""
    if clr == 'red':
        Red(n, a=a)
    if clr == 'gre':
        Green(n, a=a)
    if clr == 'blu':
        Blue(n, a=a)
    if clr == 'yel':
        Yellow(n, a=a)
    if clr == 'mag':
        Magenta(n, a=a)
    if clr == 'cya':
        Cyan(n, a=a)
    if clr == 'blk':
        Black(a=a)
    if clr == 'whi':
        White(a=a)
    if clr == 'gra':
        Gray(a=a)
    # If clr is a tuple, create that specific color
    if isinstance(clr, tuple):
        glColor3fv(clr)
