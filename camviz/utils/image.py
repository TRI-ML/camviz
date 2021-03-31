# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np
from PIL import Image

def load_image(file, shape=None):
    """
    Load an image and optionally resizes it

    Parameters
    ----------
    file : str
        Image filename
    shape : tuple (width, height)
        Optional reshape size

    Returns
    -------
    image : np.array [H,W]
        Loaded image
    """
    image = Image.open(file)
    if shape:
        image = image.resize(shape, resample=Image.ANTIALIAS)
    return np.array(image)

