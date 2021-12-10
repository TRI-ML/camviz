# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np
from matplotlib.cm import get_cmap

from camviz.utils.types import is_numpy, is_tensor


def add_row0(npy):
    """Add a row with zeros to a numpy array"""
    return np.vstack([npy, np.zeros((1, npy.shape[1]))])

def add_col1(npy):
    """Add a column with ones to a numpy array"""
    return np.hstack([npy, np.ones((npy.shape[0], 1))])

def flatten(lst):
    """Flatten a list of lists into a list"""
    return [l for ls in lst for l in ls]

def change_coords(xyz1):
    """Flip coordinates from camera to lidar frame of reference"""
    xyz2 = xyz1[:, [0, 2, 1]]
    xyz2[:, 1] *= -1
    return xyz2

def numpyf(data):
    """Convert data to a numpy array if necessary"""
    return data if is_numpy(data) else \
           data.cpu().detach().numpy() if is_tensor(data) else \
           np.array(data, dtype=np.float32)

def labelrc(tup):
    """Create row and column labels for buffers"""
    if len(tup) == 2:
        tup = ('', tup[0], tup[1])
    return [['%s%d%d' % (tup[0], j, i)
             for i in range(tup[2])] for j in range(tup[1])]

def add_list(lst1, lst2):
    """Add two lists element-wise"""
    return [l1 + l2 for l1, l2 in zip(lst1, lst2)]

def image_grid(mat):
    i, j = mat.shape[:2]
    u, v = np.meshgrid(np.arange(j), np.arange(i))
    return np.stack([u.reshape(-1), v.reshape(-1), np.ones(i * j)], 1)

def alternate_points(x1, x2):
    x = np.zeros((x1.shape[0] + x2.shape[0], 3))
    for i in range(x1.shape[0]):
        x[2*i], x[2*i+1] = x1[i], x2[i]
    return x


def vis_inverse_depth(inv_depth, normalizer=None, percentile=95, colormap='plasma'):
    cm = get_cmap(colormap)
    if normalizer:
        inv_depth /= normalizer
    else:
        inv_depth /= (np.percentile(inv_depth, percentile) + 1e-6)
    return cm(np.clip(inv_depth, 0., 1.0))[:, :, :3]


def grid_idx(grid):

    nx, ny = grid.shape[:2]
    nqx, nqy = nx - 1, ny - 1
    nqt = nqx * nqy

    idx = np.zeros(4 * nqt)
    cnt_idx, cnt_data = 0, 0
    for i in range(nx):
        for j in range(ny):
            if i < nqx and j < nqy:
                idx[cnt_idx + 0] = cnt_data
                idx[cnt_idx + 1] = cnt_data + 1
                idx[cnt_idx + 2] = cnt_data + ny + 1
                idx[cnt_idx + 3] = cnt_data + ny
                cnt_idx += 4
            cnt_data += 1

    return idx
