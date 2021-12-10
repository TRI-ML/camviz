# Copyright 2021 Toyota Research Institute.  All rights reserved.

from copy import deepcopy

import numpy as np

from camviz.objects.quaternion import Quaternion
from camviz.utils.geometry import unitX, unitY, unitZ
from camviz.utils.utils import numpyf, add_col1


def rot2quat(R):
    """Convert rotation matrix to quaternion"""
    qw = np.sqrt(1.0 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
    qx = (R[1, 2] - R[2, 1]) / (4.0 * qw)
    qy = (R[2, 0] - R[0, 2]) / (4.0 * qw)
    qz = (R[0, 1] - R[1, 0]) / (4.0 * qw)
    return Quaternion(qw, qx, qy, qz)


class Pose:

    def __init__(self, pose=None, align=False):
        """
        Pose class

        Parameters
        ----------
        pose : np.array
            Initial pose
        align : np.array
            Optional transformation matrix used for alignment
        """
        self.q = self.M = None
        # If pose is provided, use it
        if pose is not None:
            self.setPose(pose, align)
        # Otherwise, set to identity
        else:
            self.reset()

    def copy(self):
        """Return a copy of the instance"""
        return deepcopy(self)

    @property
    def t(self):
        """Return pose translation"""
        return self.M[:3, 3]

    @property
    def R(self):
        """Return pose translation"""
        return self.M[:3, :3]

    @property
    def T(self):
        """Return pose transformation"""
        return self.M

    @property
    def Rt(self):
        """Return pose rotation transposed"""
        return self.R.T

    @property
    def Tt(self):
        """Return pose transformation transposed"""
        return self.T.T

    @property
    def inv(self):
        """Return inverted pose"""
        Tinv = self.T.copy()
        Tinv[:3, :3] = np.transpose(self.T[:3, :3])
        Tinv[:3, -1] = np.matmul(-1. * Tinv[:3, :3], self.T[:3, -1])
        return Pose(Tinv)

    @property
    def Tinv(self):
        """Return inverted pose transformation"""
        return self.inv.T

    def translateX(self, m):
        """Translate object in X by m"""
        return self.translate(unitX(m))

    def translateY(self, m):
        """Translate object in Y by m"""
        return self.translate(unitY(m))

    def translateZ(self, m):
        """Translate object in Z by m"""
        return self.translate(unitZ(m))

    def rotateX(self, d, M=None):
        """Rotate object in X by d degrees"""
        return self.rotate(d, (self.M if M is None else M)[:3, 0])

    def rotateY(self, d, M=None):
        """Rotate object in Y by d degrees"""
        return self.rotate(d, (self.M if M is None else M)[:3, 1])

    def rotateZ(self, d, M=None):
        """Rotate object in Z by d degrees"""
        return self.rotate(d, (self.M if M is None else M)[:3, 2])

    def rotateI(self, d):
        """Rotate object in X by d degrees (from the camera's perspective)"""
        return self.rotate(d, unitX(1))

    def rotateJ(self, d):
        """Rotate object in Y by d degrees (from the camera's perspective)"""
        return self.rotate(d, unitY(1))

    def rotateK(self, d):
        """Rotate object in Z by d degrees (from the camera's perspective)"""
        return self.rotate(d, unitZ(1))

    def setPose(self, mat, align=False):
        """
        Set pose value

        Parameters
        ----------
        mat : np.array
            New pose value
        align : np.array
            Optional transformation matrix used for alignment
        """
        # Convert to numpy
        mat = numpyf(mat)
        # If mat is as 1-dimensional vector
        if len(mat.shape) == 1:
            # If it has 16 values, reshape and use it as a transformation matrix
            if mat.shape[0] == 16:
                self.M = np.reshape(mat, (4, 4))
                self.q = rot2quat(self.M)
            # If it has 7 values, treat is as translation + quaternion
            if mat.shape[0] == 7:
                self.M = numpyf(np.identity(4))
                self.M[:3, 3] = [mat[0], mat[1], mat[2]]
                self.q = Quaternion(mat[3], mat[4], mat[5], mat[6])
                self.M[:3, :3] = self.q.rotmat().T
        # If it's two-dimensional, treat it as a transformation matrix
        elif len(mat.shape) == 2:
            if mat.shape[0] == 4 and mat.shape[1] == 4:
                self.M = mat
                self.q = rot2quat(self.M)
        # Update transformation matrix
        self.M = numpyf(self.M)
        # Align if necessary
        if align:
            R = np.array([[0, -1,  0, 0],
                          [0,  0, -1, 0],
                          [1,  0,  0, 0],
                          [0,  0,  0, 1]])
            self.M = R @ self.M
            self.q = rot2quat(self.M)

    def reset(self):
        """Reset pose"""
        self.q = Quaternion()
        self.M = numpyf(np.identity(4))

    def translate(self, axis):
        """Translate pose in a certain axis"""
        self.M[:3, 3] += self.q.rotate(numpyf(axis))
        return self

    def rotate(self, deg, axis):
        """Rotate pose by deg in a certain axis"""
        self.q *= Quaternion(numpyf(axis), deg)
        self.M[:3, :3] = self.q.rotmat().T
        return self

    def current7(self):
        """Return current translation and quaternion values"""
        t, q = self.M[:3, 3], self.q.coefs
        return t[0], t[1], t[2], q[0], q[1], q[2], q[3]

    def __matmul__(self, other):
        """Multiply pose with something else"""
        # Pose x Pose
        if isinstance(other, Pose):
            return Pose(self.M @ other.T)
        # Pose x points
        elif other.shape[1] == 3:
            return (add_col1(other) @ self.Tt)[:, :3]
        # Generic multiplication
        else:
            return self.M @ other.T
