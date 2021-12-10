# Copyright 2021 Toyota Research Institute.  All rights reserved.

from camviz.objects.object import *


class Pointcloud(Object):
    """
    Bounding Box 3D draw class

    Parameters
    ----------
    scale : float
        Scale used when drawing the object
    pts : np.array
        Pointcloud points
    pose : np.array
        Bounding box pose
    draw : camviz.Draw
        Draw instance
    """
    def __init__(self, scale=1.0, pts=None, pose=None, draw=None):
        super().__init__(scale, pose)
        if draw is not None:
            draw.addBufferf('pts', pts)
            self.pts = 'pts'
        else:
            self.pts = pts

    def draw(self, draw, size=1, color='whi'):
        """
        Draw pointcloud on screen

        Parameters
        ----------
        draw : camviz.Draw
            Draw instance
        size : int
            Point size
        color : str
            Point color
        """
        draw.color(color).size(size).points(self.pts)

