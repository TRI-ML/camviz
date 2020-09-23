
import numpy as np
from matplotlib.cm import get_cmap
from camviz.utils.types import is_npy, is_tct

def add_row0(npy): return np.vstack([npy, np.zeros((1, npy.shape[1]))])
def add_col1(npy): return np.hstack([npy, np.ones((npy.shape[0], 1))])

def flatten(lst): return [l for ls in lst for l in ls]


def change_coords(xyz1):
    xyz2 = xyz1[:, [0, 2, 1]]
    xyz2[:, 1] *= -1
    return xyz2


def numpyf(data):
    return data if is_npy(data) else np.array(data, dtype=np.float32)


def labelrc(tup):
    if len(tup) == 2:
        tup = ('', tup[0], tup[1])
    return [['%s%d%d' % (tup[0], j, i)
             for i in range(tup[2])] for j in range(tup[1])]


def add_list(lst1, lst2):
    return [l1 + l2 for l1, l2 in zip(lst1, lst2)]


def cmapJET(data, range=None, exp=1.0):

    if data is None or data.size == 0 or isinstance(data, tuple):
        return data
    else:
        if is_tct(data):
            data = data.detach().cpu().numpy()
        if len(data.shape) > 1:
            data = data.reshape(-1)
        # data = - data
        if range is None:
            data = data.copy() - np.min(data)
            data = data / (np.max(data) + 1e-6)
        else:
            data = (data - range[0]) / (range[1] - range[0])
            data = np.maximum(np.minimum(data, 1.0), 0.0)

        if exp != 1.0:
            data = data ** exp

        jet = np.ones((data.shape[0], 3), dtype=np.float32)

        idx = (data <= 0.33)
        jet[idx, 1] = data[idx] / 0.33
        jet[idx, 0] = 0.0

        idx = (data > 0.33) & (data <= 0.67)
        jet[idx, 0] = (data[idx] - 0.33) / 0.33
        jet[idx, 2] = 1.0 - jet[idx, 0]

        idx = data > 0.67
        jet[idx, 1] = 1.0 - (data[idx] - 0.67) / 0.33
        jet[idx, 2] = 0.0

        return jet


def image_grid(mat):
    i, j = mat.shape[:2]
    u, v = np.meshgrid(np.arange(j), np.arange(i))
    return np.stack([u.reshape(-1), v.reshape(-1), np.ones(i * j)], 1)

def alternate_points(x1, x2):
    x = np.zeros((x1.shape[0] + x2.shape[0], 3))
    for i in range(x1.shape[0]):
        x[2*i], x[2*i+1] = x1[i], x2[i]
    return x


def vis_inverse_depth(inv_depth, normalizer=None, percentile=95, colormap='plasma'):
    cm = get_cmap(colormap)
    if normalizer:
        inv_depth /= normalizer
    else:
        inv_depth /= (np.percentile(inv_depth, percentile) + 1e-6)
    return cm(np.clip(inv_depth, 0., 1.0))[:, :, :3]


def grid_idx(grid):

    nx, ny = grid.shape[:2]
    nqx, nqy = nx - 1, ny - 1
    nqt = nqx * nqy

    idx = np.zeros(4 * nqt)
    cnt_idx, cnt_data = 0, 0
    for i in range(nx):
        for j in range(ny):
            if i < nqx and j < nqy:
                idx[cnt_idx + 0] = cnt_data
                idx[cnt_idx + 1] = cnt_data + 1
                idx[cnt_idx + 2] = cnt_data + ny + 1
                idx[cnt_idx + 3] = cnt_data + ny
                cnt_idx += 4
            cnt_data += 1

    return idx


# def invert_T( T ):
#
#     R , t = T[:3,:3] , T[:3,3]
#     T[:3,:3] , T[:3,3] = R.T , - np.matmul( R.T , t )
#     return T
#
# def uv_list( image ):
#
#     h , w = image.shape[:2]
#     hw = h * w
#
#     ww = np.tile( np.arange( 0 , w ) , ( h , 1 ) )
#     hh = np.tile( np.arange( 0 , h ) , ( w , 1 ) ).T
#
#     return np.stack( [ np.reshape( ww , hw ) ,
#                        np.reshape( hh , hw ) ] , axis = 1 )
#
# def d_list( depth ):
#     return np.reshape( depth , ( np.prod( depth.shape ) ) )
#
# def rgb_list( image ):
#     aaa = np.reshape( image , ( np.prod( image.shape[:2] ) , 3 ) ) / 255
#     return aaa
#
# def uvd_list( depth ):
#     return uv_list( depth ) , d_list( depth )
#
# def sample_idx( x , n ):
#     d = ( x - 1 ) / ( n - 1 )
#     return np.arange( 0 , x , d ).astype( np.int32 )
#
# def sample( x , n ):
#     return x[ sample_idx( len(x) , n ) ]
#
# def add_list( lst1 , lst2 ):
#     return [ l1 + l2 for l1 , l2 in zip( lst1 , lst2 ) ]
#
# def add_row0np( npy ):
#     return np.vstack( [ npy , np.zeros( ( 1 , npy.shape[1] ) ) ] )
# def add_col1np( npy ):
#     return np.hstack( [ npy , np.ones( ( npy.shape[0] , 1 ) ) ] )
# def add_row0tc( tct ):
#     return tc.cat( [ tct , tc.zeros( ( 1 , tct.shape[1] ) ) ] , dim = 0 )
# def add_col1tc( tct ):
#     return tc.cat( [ tct , tc.ones( ( tct.shape[0] , 1 ) ) ] , dim = 1 )
#
# def add_row0( data ):
#     if is_npy( data ): return add_row0np( data )
#     if is_tct( data ): return add_row0tc( data )
#     return None
#
# def add_col1( data ):
#     if is_npy( data ): return add_col1np( data )
#     if is_tct( data ): return add_col1tc( data )
#     return None
#
# def deg2rad( deg ):
#     return deg * math.pi / 180.0
#
#
# def transpose( data ):
#     if is_npy( data ): return data.T
#     if is_tct( data ): return tc.t( data )
#
# def identity( n ):
#     return np.identity( n )
#
# def invert( data ):
#     if is_npy( data ): return np.linalg.inv( data )
#     if is_tct( data ): return data.inverse()
#
# def matmul( data1 , data2 ):
#     if is_npy( data1 ): return np.matmul( data1 , data2 )
#     if is_tct( data1 ): return tc.matmul( data1 , data2 )
#
# def elmmul( data1 , data2 ):
#     if is_npy( data1 ): return np.multiply( data1 , data2 )
#     if is_tct( data1 ): return tc.mul( data1 , data2 )
#
# def numpyf( data ):
#     if is_npy( data ): return data
#     else: return np.array( data , dtype = np.float32 )
#
# def tensorf( data ):
#     if is_tct( data ): return data
#     else: return tc.tensor( data , dtype = tc.float32 )
#
# def cmapJET( data ):
#
#     if data is None or isinstance( data , tuple ):
#         return data
#     else:
#
#         data = - data
#         data -= np.min(data)
#         data /= np.max(data) + 1e-6
#
#         jet = np.ones( ( data.shape[0] , 3 ) , dtype = np.float32 )
#
#         idx = (data <= 0.33)
#         jet[idx, 1] = data[idx] / 0.33
#         jet[idx, 0] = 0.0
#
#         idx = (data > 0.33) & (data <= 0.66)
#         jet[idx, 0] = (data[idx] - 0.33) / 0.33
#         jet[idx, 2] = 1.0 - jet[idx, 0]
#
#         idx = data > 0.66
#         jet[idx, 1] = 1.0 - (data[idx] - 0.67) / 0.33
#         jet[idx, 2] = 0.0
#
#         return jet
