
from camviz.objects.object import Object


class BBox3D(Object):

    def __init__(self, points, pose=None):
        super().__init__(pose=pose)
        self.pts = points

    def draw(self, draw, color_line='gre', color_edge=None):
        if color_line is not None:
            draw.color(color_line).width(2).lines(
                self.pts[[0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6,
                          6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7]])
        if color_edge is not None:
            draw.color(color_edge).size(4).points(self.pts)
