
from camviz.objects.object import *
from camviz.utils import *


class Camera(Object):

    def __init__(self, scale=1.0, wh=None, K=None, pose=None, align=None):
        super(Camera, self).__init__(scale, pose)

        if K is not None:
            self.K = transpose(numpyf(K))
            self.iK = np.linalg.inv(self.K)

        if wh is not None:
            if not isinstance(wh, (list, tuple)):
                wh = wh.shape[:2]
            self.w, self.h = wh
            uv = numpyf([[self.w - 1, 0],
                         [self.w - 1, self.h - 1],
                         [0, self.h - 1],
                         [0, 0]])
            self.v = add_row0(self.i2c(uv, scale))

    @property
    def pos(self): return self.T()[:3, 3]

    @property
    def rot(self): return self.T()[:3, :3]

    def i2c(self, uv, depth=1.0):
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

