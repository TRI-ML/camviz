
from graphics.objects.object import *


class BBox3D(Object):

    def __init__(self, points, pose=None):
        super().__init__(1.0, pose)
        self.pts = points

    def draw(self, draw, color_line='gre', color_edge=None):
        if color_line is not None:
            draw.color(color_line).width(2).lines(self.pts[[0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6,
                                                            6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7]])
        if color_edge is not None:
            draw.color(color_edge).size(4).points(self.pts)


    # def __init__(self, xyz, lwh, rot, pose=None):
    #     super().__init__(1.0, pose)
    #     self.xyz = np.array(xyz)
    #     self.lwh = np.array(lwh)
    #     self.pts = [[self.xyz[0] - self.lwh[0] / 2, self.xyz[1] - self.lwh[1] / 2, self.xyz[2] - self.lwh[2] / 2],
    #                 [self.xyz[0] - self.lwh[0] / 2, self.xyz[1] - self.lwh[1] / 2, self.xyz[2] + self.lwh[2] / 2],
    #                 [self.xyz[0] - self.lwh[0] / 2, self.xyz[1] + self.lwh[1] / 2, self.xyz[2] - self.lwh[2] / 2],
    #                 [self.xyz[0] - self.lwh[0] / 2, self.xyz[1] + self.lwh[1] / 2, self.xyz[2] + self.lwh[2] / 2],
    #                 [self.xyz[0] + self.lwh[0] / 2, self.xyz[1] - self.lwh[1] / 2, self.xyz[2] - self.lwh[2] / 2],
    #                 [self.xyz[0] + self.lwh[0] / 2, self.xyz[1] - self.lwh[1] / 2, self.xyz[2] + self.lwh[2] / 2],
    #                 [self.xyz[0] + self.lwh[0] / 2, self.xyz[1] + self.lwh[1] / 2, self.xyz[2] - self.lwh[2] / 2],
    #                 [self.xyz[0] + self.lwh[0] / 2, self.xyz[1] + self.lwh[1] / 2, self.xyz[2] + self.lwh[2] / 2]]
    #     self.pts = np.array(self.pts)
    #     if rot[0] is not None:
    #         self.pts = rotX(self.xyz, self.pts, rot[0])
    #     if rot[1] is not None:
    #         self.pts = rotY(self.xyz, self.pts, rot[1])
    #     if rot[2] is not None:
    #         self.pts = rotZ(self.xyz, self.pts, rot[2])
    #
    # def draw(self, draw, color_line='cya', color_edge='blu'):
    #     if color_edge is not None:
    #         draw.color(color_line).width(2).lines(self.pts[[0, 1, 0, 2, 0, 4, 3, 1, 3, 2, 3, 7,
    #                                                                6, 7, 6, 2, 6, 4, 5, 1, 5, 4, 5, 7]])
    #     if color_line is not None:
    #         draw.color(color_edge).size(4).points(self.pts)
    #


# from graphics.utils import *
# import math

#
#
# def rotX(xyz, pts, angle):
#     c, s = math.cos(angle), math.sin(angle)
#     R = np.array([[1, 0, 0], [0, c, s], [0, -s, c]])
#     return xyz + ((pts - xyz) @ R)
#
#
# def rotY(xyz, pts, angle):
#     c, s = math.cos(angle), math.sin(angle)
#     R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
#     return xyz + ((pts - xyz) @ R)
#
#
# def rotZ(xyz, pts, angle):
#     c, s = math.cos(angle), math.sin(angle)
#     R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
#     return xyz + ((pts - xyz) @ R)
#
#
# def inside(pts, pcl):
#     idx = (pcl[:, 0] > pts[0, 0]) & (pcl[:, 0] < pts[-1, 0]) & \
#           (pcl[:, 1] > pts[0, 1]) & (pcl[:, 1] < pts[-1, 1]) & \
#           (pcl[:, 2] > pts[0, 2]) & (pcl[:, 2] < pts[-1, 2])
#     print('idx', idx.sum())
#     return pcl[idx]
