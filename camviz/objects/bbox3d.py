# Copyright 2021 Toyota Research Institute.  All rights reserved.

from camviz.objects.object import Object


class BBox3D(Object):
    """
    Bounding Box 3D draw class

    Parameters
    ----------
    points : np.array
        List of points for the bounding box dimension (assuming center is 0,0,0)
        Order: +++, +-+, +--, ++-, -++, --+, ---, -+- 
    pose : np.array
        Bounding box pose (x-forward, y-left, z-up)
    """
    def __init__(self, points, pose=None):
        super().__init__(pose=pose)
        self.pts = points

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
                self.pts[[0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6,
                          6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7]])
        # Set color edge if provided
        if color_edge is not None:
            draw.color(color_edge).size(4).points(self.pts)
