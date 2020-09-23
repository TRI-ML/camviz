
from OpenGL.GL import glColor3fv

def Red(n=1.0):     glColor3fv(( n ,0.0,0.0))
def Green(n=1.0):   glColor3fv((0.0, n ,0.0))
def Blue(n=1.0):    glColor3fv((0.0,0.0, n ))
def Yellow(n=1.0):  glColor3fv(( n , n ,0.0))
def Magenta(n=1.0): glColor3fv(( n ,0.0, n ))
def Cyan(n=1.0):    glColor3fv((0.0, n , n ))
def Black():        glColor3fv((0.0,0.0,0.0))
def White():        glColor3fv((1.0,1.0,1.0))
def Gray():         glColor3fv((0.5,0.5,0.5))

def setColor(clr, n=1.0):
    if clr == 'red': Red(n)
    if clr == 'gre': Green(n)
    if clr == 'blu': Blue(n)
    if clr == 'yel': Yellow(n)
    if clr == 'mag': Magenta(n)
    if clr == 'cya': Cyan(n)
    if clr == 'blk': Black()
    if clr == 'whi': White()
    if clr == 'gra': Gray()
    if isinstance(clr, tuple): glColor3fv(clr)
