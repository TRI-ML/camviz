# Copyright 2021 Toyota Research Institute.  All rights reserved.

import numpy as np
from matplotlib.cm import get_cmap

from camviz.utils.types import is_numpy, is_tensor


def jet(data, range=None, exp=1.0):
    """
    Creates a JET colormap from data

    Parameters
    ----------
    data : np.array [N,1]
        Data to be converted into a colormap
    range : tuple (min,max)
        Optional range value for the colormap (if None, use min and max from data)
    exp : float
        Exponential value to weight the color differently

    Returns
    -------
    colormap : np.array [N,3]
        Colormap obtained from data
    """
    # Return if data is not available
    if data is None or data.size == 0 or isinstance(data, tuple):
        return data
    else:
        # If data is a tensor, convert to numpy
        if is_tensor(data):
            data = data.detach().cpu().numpy()
        # If data is [N,1], remove second dimensions
        if len(data.shape) > 1:
            data = data.reshape(-1)
        # Determine range if not available
        if range is None:
            data = data.copy() - np.min(data)
            data = data / (np.max(data) + 1e-6)
        else:
            data = (data - range[0]) / (range[1] - range[0])
            data = np.maximum(np.minimum(data, 1.0), 0.0)
        # Use exponential if requested
        if exp != 1.0:
            data = data ** exp
        # Initialize colormap
        jet = np.ones((data.shape[0], 3), dtype=np.float32)
        # First stage
        idx = (data <= 0.33)
        jet[idx, 1] = data[idx] / 0.33
        jet[idx, 0] = 0.0
        # Second stage
        idx = (data > 0.33) & (data <= 0.67)
        jet[idx, 0] = (data[idx] - 0.33) / 0.33
        jet[idx, 2] = 1.0 - jet[idx, 0]
        # Third stage
        idx = data > 0.67
        jet[idx, 1] = 1.0 - (data[idx] - 0.67) / 0.33
        jet[idx, 2] = 0.0
        # Return colormap
        return jet

