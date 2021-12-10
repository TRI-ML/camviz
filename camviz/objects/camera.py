# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np

from camviz.objects.object import Object
from camviz.utils.geometry import transpose, invert
from camviz.utils.types import is_list, is_float
from camviz.utils.utils import numpyf, add_row0, add_col1, image_grid


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
    def __init__(self, scale=1.0, wh=None, K=None, pose=None):
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
            self.v = add_row0(self.i2c(scale, uv))

    @staticmethod
    def from_vidar(cam, b, scale=1.0):
        return Camera(K=cam.K[b][:3, :3],
                      pose=cam.Tcw.T[b] if cam.Twc is not None else None,
                      wh=cam.wh, scale=scale)

    def i2c(self, depth=1.0, uv=None):
        """
        Project an image to camera coordinates using a depth map

        Parameters
        ----------
        depth : float or np.array
            Depth values for lifting
        uv : np.array
            Image grid for lifting

        Returns
        -------
        xyz : np.array
            Lifted 3D points in camera frame of reference
        """
        # If no grid is provided, uses depth map
        if uv is None:
            if not is_float(depth):
                # Create image grid from depth values
                uv = image_grid(depth)
            else:
                # Impossible to create an image grid
                raise ValueError('No available grid for camera')
        # Add third unitary coordinate to the image grid
        if uv.shape[1] == 2:
            uv = add_col1(uv)
        # A depth map was provided, create a grid from it
        elif uv.shape[1] > 3:
            uv = image_grid(uv)
        # If there are individual depth values per image grid cell
        if not is_float(depth):
            if len(depth.shape) == 1:
                depth = depth[:, np.newaxis]
            elif depth.shape[1] > 1:
                if len(depth.shape) == 3:
                    depth = depth[:, :, 0]
                depth = depth.reshape(-1, 1)
        return (uv @ self.iK) * depth

    def c2i(self, xyz, filter=False, padding=0, return_z=False):
        """
        Project 3D points in camera frame of reference to the image plane

        Parameters
        ----------
        xyz : np.array
            3D points to be projected
        filter : bool
            Filter points outside boundaries
        padding : int or float
            Padding for filtering
        return_z : bool
            Return z values as well or not

        Returns
        -------
        uv : np.array
            2D coordinates of projected points
        idx : np.array
            Valid indexes in case filtering was enabled
        depth : np.array
            Depth values in case return_z was enabled
        """
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
        """Transform 3D points in camera frame of reference to world frame of reference"""
        if xyz.shape[1] == 3:
            xyz = add_col1(xyz)
        return (xyz @ self.Tt)[:, :3]

    def w2c(self, xyz):
        """Transform 3D points in world frame of reference to camera frame of reference"""
        if xyz.shape[1] == 3:
            xyz = add_col1(xyz)
        return (xyz @ invert(self.Tt))[:, :3]

    def i2w(self, depth=1.0, uv=None):
        """Lift 2D image points to 3D space in world frame of reference"""
        return self.c2w(self.i2c(depth, uv))

    def w2i(self, xyz, filter=False, padding=0, return_z=False):
        """Project 3D points in world frame of reference to the image plane"""
        return self.c2i(self.w2c(xyz), filter=filter,
                        padding=padding, return_z=return_z)

    def draw(self, draw, tex=None, axes=True, color='gra'):
        """
        Draw a camera in a 3D screen

        Parameters
        ----------
        draw : Draw
            Draw class to be used
        tex : int
            Optional texture to draw on the camera image plane
        axes : bool
            True if coordinate axes should be drawn as well
        color : str
            Which color should be used for the camera
        """
        draw.image(tex, verts=self.v[:4])
        draw.color(color).width(4).connects(self.v[4], self.v[:4]).loop(self.v[:4])
        if axes:
            draw.axis(0.25 * self.scale)
