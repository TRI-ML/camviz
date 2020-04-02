
from OpenGL.GL import *
from camviz.objects.pose import Pose


class Object:

    def __init__(self, scale=1.0, pose=None):
        self.scale = scale
        self.pose = pose.copy() if isinstance(pose, Pose) else Pose(pose)

    @property
    def t(self): return self.pose.t

    @property
    def R(self): return self.pose.R

    @property
    def T(self): return self.pose.T

    @property
    def Rt(self): return self.pose.Rt

    @property
    def Tt(self): return self.pose.Tt

    def translateX(self, m):
        return self.pose.translateX(m)

    def translateY(self, m):
        return self.pose.translateY(m)

    def translateZ(self, m):
        return self.pose.translateZ(m)

    def rotateX(self, d):
        return self.pose.rotateX(d)

    def rotateY(self, d):
        return self.pose.rotateY(d)

    def rotateZ(self, d):
        return self.pose.rotateZ(d)

    def rotateI(self, d):
        return self.pose.rotateI(d)

    def rotateJ(self, d):
        return self.pose.rotateJ(d)

    def rotateK(self, d):
        return self.pose.rotateK(d)

    def setPose(self, pose):
        return self.pose.setPose(pose)

    def display(self, *args, align=None, **kwargs):

        if align is not None:
            T = (align @ self.pose).Tt
        else:
            T = self.Tt

        glPushMatrix()
        glMultMatrixf(T)
        self.draw(*args, **kwargs)
        glPopMatrix()
