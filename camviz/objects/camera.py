# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np

from display.camviz.objects.object import Object
from display.camviz.utils.geometry import transpose, invert
from display.camviz.utils.utils import numpyf, add_row0, add_col1, image_grid
from packnet_sfm.utils.types import is_list


def camviz_camera(camera):
    """
    Converts packnet-sfm cameras to camviz cameras

    Parameters
    ----------
    camera : Camera or list[Camera]
        Input packnet-sfm cameras

    Returns
    -------
    camera_cv : camviz.objects.camera.Camera
        output camviz cameras
    """
    # Create a list of cameras if necessary
    if is_list(camera):
        return [camviz_camera(cam) for cam in camera]
    # Return a list of cameras for each batch camera
    return [Camera(cam=cam) for cam in camera]


class Camera(Object):
    """
    Create a camera class

    Parameters
    ----------
    scale : float
        Scale used when drawing the object
    wh : tuple
        Image dimensions (width, height)
    K : np.array
        Camera intrinsics [3,3]
    pose : np.array
        Object pose
    """
    def __init__(self, scale=1.0, wh=None, K=None, pose=None, cam=None):
        # If a packnet_sfm camera is provided
        if cam is not None:
            K, pose, wh = cam.K[0], cam.Twc.mat[0], cam.wh
        # Initialize object super-class
        super().__init__(scale, pose)
        # If intrinsics is provided, use it
        if K is not None:
            self.K = transpose(numpyf(K))
            self.iK = np.linalg.inv(self.K)
        # If image dimensions is not provided, use it
        if wh is not None:
            if not isinstance(wh, (list, tuple)):
                wh = wh.shape[:2]
            self.w, self.h = wh
            uv = numpyf([[self.w - 1,     0     ],
                         [self.w - 1, self.h - 1],
                         [    0     , self.h - 1],
                         [    0     ,     0     ]])
            self.v = add_row0(self.i2c(uv, scale))

    def i2c(self, uv, depth=1.0):
        """
        Project an image to camera coordinates using a depth map

        Parameters
        ----------
        uv : image gri
        depth

        Returns
        -------

        """
        if uv.shape[1] == 2:
            uv = add_col1(uv)
        elif uv.shape[1] > 3:
            uv = image_grid(uv)
        if not isinstance(depth, float):
            if len(depth.shape) == 1:
                depth = depth[:, np.newaxis]
            elif depth.shape[1] > 1:
                if len(depth.shape) == 3:
                    depth = depth[:, :, 0]
                depth = depth.reshape(-1, 1)
        return (uv @ self.iK) * depth

    def c2i(self, xyz, filter=False, padding=0, return_z=False):
        uv = (xyz / xyz[:, 2:] @ self.K)[:, :2]
        if filter:
            idx = (uv[:, 0] > -padding) & (uv[:, 0] < self.w + padding) & \
                  (uv[:, 1] > -padding) & (uv[:, 1] < self.h + padding) & (xyz[:, 2] > 0)
            if return_z:
                return uv[idx], xyz[idx, 2:], idx
            else:
                return uv[idx], idx
        else:
            if return_z:
                return uv, xyz[:, 2:]
            else:
                return uv

    def c2w(self, xyz):
        if xyz.shape[1] == 3:
            xyz = add_col1(xyz)
        return (xyz @ self.Tt)[:, :3]

    def w2c(self, xyz):
        if xyz.shape[1] == 3:
            xyz = add_col1(xyz)
        return (xyz @ invert(self.Tt))[:, :3]

    def i2w(self, uv, depth=1.0):
        return self.c2w(self.i2c(uv, depth))

    def w2i(self, xyz, filter=False, padding=0, return_z=False):
        return self.c2i(self.w2c(xyz), filter=filter,
                        padding=padding, return_z=return_z)

    def draw(self, draw, tex=None, axes=True, color='gra'):
        draw.image(tex, verts=self.v[:4])
        draw.color(color).width(4).connects(self.v[4], self.v[:4]).loop(self.v[:4])
        if axes:
            draw.axis(0.25 * self.scale)

