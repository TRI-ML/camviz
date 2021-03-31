# Copyright 2021 Toyota Research Institute.  All rights reserved.

from OpenGL.GL import glColor3fv

def Red(n=1.0):
    """Change to red color"""
    glColor3fv((n, 0.0, 0.0))

def Green(n=1.0):
    """Change to green color"""
    glColor3fv((0.0, n, 0.0))

def Blue(n=1.0):
    """Change to blue color"""
    glColor3fv((0.0, 0.0, n))

def Yellow(n=1.0):
    """Change to yellow color"""
    glColor3fv((n, n, 0.0))

def Magenta(n=1.0):
    """Change to magenta color"""
    glColor3fv((n, 0.0, n))

def Cyan(n=1.0):
    """Change to cyan color"""
    glColor3fv((0.0, n, n))

def Black():
    """Change to black color"""
    glColor3fv((0.0, 0.0, 0.0))

def White():
    """Change to white color"""
    glColor3fv((1.0, 1.0, 1.0))

def Gray():
    """Change to gray color"""
    glColor3fv((0.5, 0.5, 0.5))

def setColor(clr, n=1.0):
    """Change to an specific color based on a string"""
    if clr == 'red':
        Red(n)
    if clr == 'gre':
        Green(n)
    if clr == 'blu':
        Blue(n)
    if clr == 'yel':
        Yellow(n)
    if clr == 'mag':
        Magenta(n)
    if clr == 'cya':
        Cyan(n)
    if clr == 'blk':
        Black()
    if clr == 'whi':
        White()
    if clr == 'gra':
        Gray()
    # If clr is a tuple, create that specific color
    if isinstance(clr, tuple):
        glColor3fv(clr)
