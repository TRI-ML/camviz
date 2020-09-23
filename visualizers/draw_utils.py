
import numpy as np
from ouroboros.dgp.utils.camera import Camera as Camera_DGP
from ouroboros.dgp.utils.camera import generate_depth_map
from packnet_sfm.datasets.augmentations import resize_depth


def create_depth_map(points, camera, shape):
    return generate_depth_map(Camera_DGP(K=np.transpose(camera.K)),
                              camera.pose.inv @ points, shape)

def get_inside_indices(points, bboxes3d):
    """Returns point indices inside bounding boxes"""
    indices = []
    for bbox in bboxes3d:
        p1, p2, p3, p4 = np.array(bbox)[[0, 1, 3, 4]]
        d12, d14, d15 = p1 - p2, p1 - p3, p1 - p4

        u = np.expand_dims(np.cross(d14, d15), 1)
        v = np.expand_dims(np.cross(d12, d14), 1)
        w = np.expand_dims(np.cross(d12, d15), 1)

        p1 = np.expand_dims(p1, 0)
        p2 = np.expand_dims(p2, 0)
        p3 = np.expand_dims(p3, 0)
        p4 = np.expand_dims(p4, 0)

        pdotu = np.dot(points, u)
        pdotv = np.dot(points, v)
        pdotw = np.dot(points, w)

        idx = (pdotu < np.dot(p1, u)) & (pdotu > np.dot(p2, u)) & \
              (pdotv < np.dot(p1, v)) & (pdotv > np.dot(p4, v)) & \
              (pdotw > np.dot(p1, w)) & (pdotw < np.dot(p3, w))
        indices.append(idx.nonzero()[0])
    return indices


def color_semantic(semantic, seed=142857):
    np.random.seed(seed)
    max_idx = semantic[semantic < 255].max()
    color = np.zeros((semantic.shape[0], semantic.shape[1], 3))
    rnd = np.random.random((max_idx, 3))
    for idx in range(max_idx):
        color[semantic == idx] = rnd[idx]
    return color

def use_gt_scale(depth, gt_depth):
    gt_depth_resized = resize_depth(gt_depth, depth.shape)[:, :, 0]
    return depth * np.median(gt_depth_resized[gt_depth_resized > 0]) / \
           np.median(depth[gt_depth_resized > 0])

def common_args(parser, mode):
    parser.add_argument('--path', type=str, default='/data/save/depth',
                        help='Root path where information is stored')
    parser.add_argument('--split', type=str, default='',
                        help='Which split was used (full split name, i.e. ddad-val-lidar')
    parser.add_argument('--start_frame', type=int, default=0,
                        help='Starting frame for the sequence')
    parser.add_argument('--end_frame', type=int, default=0,
                        help='End frame for the sequence')
    parser.add_argument('--output_folder', type=str, default=None,
                        help='Output folder to save the sequence (press S to start saving)')
    parser.add_argument('--max_height', type=float, default=None,
                        help='Maximum pointcloud height')
    parser.add_argument('--scale', type=float, default=1.0,
                        help='Scale for visualization window')
    parser.add_argument('--use_gt_scale', action='store_true',
                        help='Use median-scaling on predicted pointcloud')
    if 'dataset' in mode:
        parser.add_argument('--depth_type', type=str, default='',
                            help='Scale for visualization window')
    if 'eval' in mode:
        parser.add_argument('--model', type=str, default=None,
                            help='Which model was used (same as the checkpoint)')
        parser.add_argument('--min_depth', type=float, default=None,
                            help='Maximum pointcloud height')
        parser.add_argument('--crop_top', type=float, default=0.0,
                            help='How much to crop from the top of the depth map')
    if 'multicam' in mode:
        parser.add_argument('--cameras', type=int, nargs='+', default=[1, 5, 6, 9])
    return parser
