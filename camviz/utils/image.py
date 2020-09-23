
import numpy as np
from PIL import Image

def load_image(file, shape=None):
    image = Image.open(file)
    if shape:
        image = image.resize(shape, resample=Image.ANTIALIAS)
    return np.array(image)

