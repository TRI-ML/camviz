
from copy import deepcopy


class Screen:

    def __init__(self, luwh, mode):
        self.luwh, self.mode = luwh, mode

    def inside(self, pos):
        return self.luwh[0] < pos[0] < self.luwh[0] + self.luwh[2] and \
               self.luwh[1] < pos[1] < self.luwh[1] + self.luwh[3]

    def saveViewer(self):
        self.origin = deepcopy(self.viewer)
        
    def reset(self):
        self.viewer = deepcopy(self.origin)

