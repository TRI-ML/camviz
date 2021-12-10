# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np

from camviz.objects.object import Object


class BBox2D(Object):
    """
    Bounding Box 2D draw class

    Parameters
    ----------
    points : np.array
        List of points for the bounding box dimension (left, top, right, bottom)
    pose : np.array
        Bounding box pose on the screen (right, down)
    """
    def __init__(self, points, pose=None):
        super().__init__(pose=pose)
        self.pts = np.array([[points[0], points[1]], 
                             [points[2], points[1]],
                             [points[2], points[3]],
                             [points[0], points[3]]])

    def draw(self, draw, color_line='gre', color_edge=None):
        """
        Draw 2D bounding box on screen

        Parameters
        ----------
        draw : camviz.Draw
            Draw instance
        color_line : str
            Line color
        color_edge : str
            Edge color
        """
        # Set color line if provided
        if color_line is not None:
            draw.color(color_line).width(2).lines(
                self.pts[[0, 1, 1, 2, 2, 3, 3, 0]])
        # Set color edge if provided
        if color_edge is not None:
            draw.color(color_edge).size(4).points(self.pts)
