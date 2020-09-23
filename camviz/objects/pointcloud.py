
from camviz.objects.object import *
from camviz.utils.utils import *


class Pointcloud(Object):

    def __init__(self, scale=1.0, pts=None, pose=None, draw=None):
        super().__init__(scale, pose)
        if draw is not None:
            draw.addBufferf('pts', pts)
            self.pts = 'pts'
        else:
            self.pts = pts

    def draw(self, draw, size=1, color='whi'):
        draw.color(color).size(size).points(self.pts)

