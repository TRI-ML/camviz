
from graphics.objects.object import *
from graphics.utils import *


class Pointcloud(Object):

    def __init__(self, scale=1.0, pts=None, pose=None, draw=None):
        super().__init__(scale, pose)
        if draw is not None:
            draw.addBufferf('pts', pts)
            self.pts = 'pts'
        else:
            self.pts = pts


    @property
    def pos(self): return self.T()[:3, 3]

    @property
    def rot(self): return self.T()[:3, :3]

    def draw(self, draw, size=1, color='whi'):
        draw.color(color).size(size).points(self.pts)

