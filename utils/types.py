
import numpy as np
import torch as tc

def is_npy(data): return isinstance(data, np.ndarray)
def is_tct(data): return type(data) == tc.Tensor
def is_tup(data): return isinstance(data, tuple)
def is_lst(data): return isinstance(data, list)
def is_str(data): return isinstance(data, str)
def is_int(data): return isinstance(data, int)
def is_flt(data): return isinstance(data, float)
def is_seq(data): return is_lst(data) or is_tup(data)

