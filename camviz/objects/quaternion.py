# Copyright 2021 Toyota Research Institute.  All rights reserved.

import math

import numpy as np


class Quaternion:
    """Quaternion class"""
    def __init__(self, *args):
        # If no arguments are provided, create an identity quaternion
        if len(args) == 0:
            self.coefs = 1.0, 0.0, 0.0, 0.0
        # If a single argument is provided
        elif len(args) == 1:
            # If it's a tuple, it contains coefficients
            if isinstance(args[0], tuple):
                self.coefs = args[0]
            # Otherwise, assume it's a rotation matrix
            else:
                R = np.array(args[0])
                w = np.sqrt(1.0 + R[0, 0] + R[1, 1] + R[2, 2]) / 2
                x = (R[1, 2] - R[2, 1]) / (4.0 * w)
                y = (R[2, 0] - R[0, 2]) / (4.0 * w)
                z = (R[0, 1] - R[1, 0]) / (4.0 * w)
                self.coefs = w, x, y, z
        # If two arguments are provided, assume it's axis and degree
        elif len(args) == 2:
            v, d = args
            r = d * math.pi / 360.0
            c, s = math.cos(r), math.sin(r)
            self.coefs = c, v[0] * s, v[1] * s, v[2] * s
        # If there are four arguments, assume each individual coefficient is provided
        elif len(args) == 4:
            self.coefs = args

    def __getitem__(self, idx):
        """Return quaternion coefficients"""
        return self.coefs[idx]

    def __mul__(self, r):
        """Multiply quaternion with rotation angles"""
        q, r = self.coefs, r.coefs
        return Quaternion(r[0] * q[0] - r[1] * q[1] - r[2] * q[2] - r[3] * q[3],
                          r[0] * q[1] + r[1] * q[0] - r[2] * q[3] + r[3] * q[2],
                          r[0] * q[2] + r[1] * q[3] + r[2] * q[0] - r[3] * q[1],
                          r[0] * q[3] - r[1] * q[2] + r[2] * q[1] + r[3] * q[0])

    def invert(self):
        """Return inverted quaternion"""
        w, x, y, z = self.coefs
        d = np.sqrt(w * w + x * x + y * y + z * z)
        return Quaternion(w / d, - x / d, - y / d, - z / d)

    def rotate(self, p):
        """Rotate points"""
        vec = self.coefs[1:]

        uv = np.cross(p, vec)
        uuv = np.cross(uv, vec)

        return p + 2 * (self.coefs[0] * uv + uuv)

    def rotmat(self):
        """Return rotation matrix"""
        w, x, y, z = self.coefs
        xx, yy, zz = x * x, y * y, z * z
        return np.array([[1-2*yy-2*zz, 2*x*y-2*z*w, 2*x*z+2*y*w],
                         [2*x*y+2*z*w, 1-2*xx-2*zz, 2*y*z-2*x*w],
                         [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*xx-2*yy]])


