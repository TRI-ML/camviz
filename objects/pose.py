
from copy import deepcopy

import numpy as np

from camviz.objects.quaternion import Quaternion
from camviz.utils.geometry import unitX, unitY, unitZ
from camviz.utils.utils import numpyf, add_col1


def rot2quat(R):

    qw = np.sqrt(1.0 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
    qx = (R[1, 2] - R[2, 1]) / (4.0 * qw)
    qy = (R[2, 0] - R[0, 2]) / (4.0 * qw)
    qz = (R[0, 1] - R[1, 0]) / (4.0 * qw)
    return Quaternion(qw, qx, qy, qz)


class Pose:

    def __init__(self, pose=None, align=False):
        self.q = self.M = None
        if pose is not None:
            self.setPose(pose, align)
        else:
            self.reset()

    def copy(self):
        return deepcopy(self)

    @property
    def t(self):
        return self.M[:3, 3]

    @property
    def R(self):
        return self.M[:3, :3]

    @property
    def T(self):
        return self.M

    @property
    def Rt(self):
        return self.R.T

    @property
    def Tt(self):
        return self.T.T

    @property
    def inv(self):
        Tinv = self.T.copy()
        Tinv[:3, :3] = np.transpose(self.T[:3, :3])
        Tinv[:3, -1] = np.matmul(-1. * Tinv[:3, :3], self.T[:3, -1])
        return Pose(Tinv)

    @property
    def Tinv(self):
        return self.inv.T

    def translateX(self, m):
        return self.translate(unitX(m))

    def translateY(self, m):
        return self.translate(unitY(m))

    def translateZ(self, m):
        return self.translate(unitZ(m))

    def rotateX(self, d):
        return self.rotate(d, self.M[:3, 0])

    def rotateY(self, d):
        return self.rotate(d, self.M[:3, 1])

    def rotateZ(self, d):
        return self.rotate(d, self.M[:3, 2])

    def rotateI(self, d):
        return self.rotate(d, unitX(1))

    def rotateJ(self, d):
        return self.rotate(d, unitY(1))

    def rotateK(self, d):
        return self.rotate(d, unitZ(1))

    def setPose(self, mat, align=False):
        mat = numpyf(mat)
        if len(mat.shape) == 1:
            if mat.shape[0] == 16:
                self.M = np.reshape(mat, (4, 4))
                self.q = rot2quat(self.M)
            if mat.shape[0] == 7:
                self.M = numpyf(np.identity(4))
                self.M[:3, 3] = [mat[0], mat[1], mat[2]]
                self.q = Quaternion(mat[3], mat[4], mat[5], mat[6])
                self.M[:3, :3] = self.q.rotmat().T
        elif len(mat.shape) == 2:
            if mat.shape[0] == 4 and mat.shape[1] == 4:
                self.M = mat
                self.q = rot2quat(self.M)
        self.M = numpyf(self.M)

        if align:
            R = np.array([[0, -1,  0, 0],
                          [0,  0, -1, 0],
                          [1,  0,  0, 0],
                          [0,  0,  0, 1]])
            self.M = R @ self.M
            self.q = rot2quat(self.M)

    def reset(self):
        self.q = Quaternion()
        self.M = numpyf(np.identity(4))

    def translate(self, axis):
        self.M[:3, 3] += self.q.rotate(numpyf(axis))
        return self

    def rotate(self, deg, axis):
        self.q *= Quaternion(numpyf(axis), deg)
        self.M[:3, :3] = self.q.rotmat().T
        return self

    def current7(self):
        t, q = self.M[:3, 3], self.q.coefs
        return t[0], t[1], t[2], q[0], q[1], q[2], q[3]

    def __matmul__(self, other):
        if isinstance(other, Pose):
            return Pose(self.M @ other.T)
        elif other.shape[1] == 3:
            return (add_col1(other) @ self.Tt)[:, :3]
        else:
            return self.M @ other.T
