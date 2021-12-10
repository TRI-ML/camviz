# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np

def unitX(m=1.0):
    """Return an unit vector on X"""
    return np.array((m, 0, 0))

def unitY(m=1.0):
    """Return an unit vector on Y"""
    return np.array((0, m, 0))

def unitZ(m=1.0):
    """Return an unit vector on Z"""
    return np.array((0, 0, m))

def transpose(data):
    """Transpose numpy array"""
    return data.T

def invert(data):
    """Invert numpy array"""
    return np.linalg.inv(data)
