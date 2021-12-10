# Copyright 2021 Toyota Research Institute.  All rights reserved.

from copy import deepcopy


class Screen:
    def __init__(self, luwh, mode):
        """
        Screen class

        Parameters
        ----------
        luwh : tuple
            Left/right/width/height values
        mode : str
            Screen mode ('2D_IMAGE' or '3D_WORLD')
        """
        assert mode in ['2D_IMAGE', '3D_WORLD'], 'Invalid screen mode'
        self.luwh, self.mode = luwh, mode
        self.origin = self.viewer = None

    def inside(self, pos):
        """
        Check if a 2D coordinate is inside the screen

        Parameters
        ----------
        pos : np.array
            Pose to check

        Returns
        -------
        inside : bool
            Whether pos is inside the screen
        """
        return self.luwh[0] < pos[0] < self.luwh[0] + self.luwh[2] and \
               self.luwh[1] < pos[1] < self.luwh[1] + self.luwh[3]

    def saveViewer(self):
        """Save current virtual viewer camera (pose and intrinsics)"""
        self.origin = deepcopy(self.viewer)
        
    def reset(self):
        """Reset current virtual viewer camera"""
        self.viewer = deepcopy(self.origin)

