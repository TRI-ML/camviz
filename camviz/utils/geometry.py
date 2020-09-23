
import numpy as np

def unitX(m=1.0): return np.array((m, 0, 0))
def unitY(m=1.0): return np.array((0, m, 0))
def unitZ(m=1.0): return np.array((0, 0, m))

def transpose(data): return data.T
def invert(data): return np.linalg.inv(data)