# Copyright 2020 Toyota Research Institute.  All rights reserved.

import os
from camviz.utils.utils import cmapJET


class DrawBase:
    """
    Base class for visualization display.

    Parameters
    ----------
    output_folder : str
        Output folder where the sequence will be saved
    """
    def __init__(self, files, args):
        """Initialize visualization."""
        self.files = files
        # Set initial variables
        self.change = False
        self.started = False
        self.draw = None
        # Parse arguments
        self.output_folder = args.output_folder
        self.use_gt_scale = args.use_gt_scale
        self.max_height = args.max_height
        self.scale = args.scale
        # Set first and final frames
        self.n = self.n_st = args.start_frame
        # self.n_fn = args.end_frame if args.end_frame > 0 else len(files[0]) if is_list(files[0]) else len(files)
        self.n_fn = args.end_frame if args.end_frame > 0 else len(files)

        # Create output folder if needed
        if self.output_folder is not None:
            os.makedirs(self.output_folder, exist_ok=True)

    def cmapJET(self, data):
        """Height color map"""
        minmax = None if self.max_height is None else (0.0, self.max_height)
        return cmapJET(data, range=minmax, exp=0.5)

    def get_data(self, n=None):
        """Method for getting data from a file at position n."""
        raise NotImplementedError('DrawBase: You need to implement get_data')

    def update(self, data):
        """Method for updating the visualization."""
        raise NotImplementedError('DrawBase: You need to implement update')

    def display(self):
        """Method for displaying the visualization."""
        raise NotImplementedError('DrawBase: You need to implement display')

    def commands(self):
        """Method for the commands used to control the visualization."""
        # Start saving (S)
        if self.draw.KEY_S and not self.started and self.output_folder is not None:
            self.started = True
            self.draw.halt(500)
        # Next frame (UP)
        if self.draw.UP and self.n < self.n_fn - 1:
            self.n += 1
            self.change = True
        # Previous frame (DOWN)
        if self.draw.DOWN and self.n > self.n_st:
            self.n -= 1
            self.change = True
        # If changing frames
        if self.change:
            self.update(self.get_data())
            self.change = False
            self.draw.halt(500)

    def loop(self):
        """Method for looping the visualization."""
        # Draw loop
        while self.draw.input():
            self.commands()
            self.display()
            # If we are saving frames
            if self.started:
                filename = os.path.join(self.output_folder, '%010d.png' % self.n)
                print('Saving {}'.format(filename))
                self.draw.save(filename)
                self.change = True
                self.n += 1
                if self.n == self.n_fn:
                    break
