# Copyright 2021 Toyota Research Institute.  All rights reserved.

from OpenGL.GL import *

from camviz.objects.pose import Pose


class Object:
    """
    Base object draw class

    Parameters
    ----------
    scale : float
        Scale used when drawing the object
    pose : np.array
        Object pose
    """
    def __init__(self, scale=1.0, pose=None):
        self.scale = scale
        self.pose = pose if isinstance(pose, Pose) else Pose(pose)

    @property
    def t(self):
        """Return pose translation"""
        return self.pose.t

    @property
    def R(self):
        """Return pose rotation"""
        return self.pose.R

    @property
    def T(self):
        """Return pose transformation"""
        return self.pose.T

    @property
    def Rt(self):
        """Return pose rotation transposed"""
        return self.pose.Rt

    @property
    def Tt(self):
        """Return pose transformation transposed"""
        return self.pose.Tt

    def translateX(self, m):
        """Translate object in X by m"""
        return self.pose.translateX(m)

    def translateY(self, m):
        """Translate object in Y by m"""
        return self.pose.translateY(m)

    def translateZ(self, m):
        """Translate object in Z by m"""
        return self.pose.translateZ(m)

    def rotateX(self, d):
        """Rotate object in X by d degrees"""
        return self.pose.rotateX(d)

    def rotateY(self, d):
        """Rotate object in Y by d degrees"""
        return self.pose.rotateY(d)

    def rotateZ(self, d):
        """Rotate object in Z by d degrees"""
        return self.pose.rotateZ(d)

    def rotateI(self, d):
        """Rotate object in X by d degrees (from the camera's perspective)"""
        return self.pose.rotateI(d)

    def rotateJ(self, d):
        """Rotate object in Y by d degrees (from the camera's perspective)"""
        return self.pose.rotateJ(d)

    def rotateK(self, d):
        """Rotate object in Z by d degrees (from the camera's perspective)"""
        return self.pose.rotateK(d)

    def setPose(self, pose):
        """Set object pose"""
        return self.pose.setPose(pose)

    def display(self, *args, align=None, **kwargs):
        """
        Display object

        Parameters
        ----------
        args : args
            Extra draw arguments
        align : camviz.Pose
            Pose used to align the object
        kwargs : kwargs
            Extra draw arguments
        """
        # Get transformation (aligned or not)
        if align is not None:
            T = (align @ self.pose).Tt
        else:
            T = self.Tt

        # Draw object
        glPushMatrix()
        glMultMatrixf(T)
        self.draw(*args, **kwargs)
        glPopMatrix()
