
import numpy as np

from camviz.draw import Draw
from camviz.utils import cmapJET
from camviz.objects.bbox3d import BBox3D
from camviz.objects.camera import Camera


class_color = {
    0: 'blu',
    1: 'mag',
    2: 'gre',
    3: 'red',
    4: 'yel',
    5: 'cya',
}


def get_class_color(n):
    """Returns corresponding color, or white if there is none"""
    if n in class_color:
        return class_color[n]
    else:
        return 'whi'


def get_inside_indices(points, bboxes):
    """Returns list containing indices of points inside each bounding box"""
    indices = []
    for bbox in bboxes:
        p1, p2, p3, p4 = np.array(bbox.corners)[[0, 1, 3, 4]]
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


def parse_sample(sample):
    """Parse dataset sample into a dictionary that can be displayed"""

    ### Lidar is assumed to be the first sensor

    # Extract information
    lidar_point_cloud = sample[0]['point_cloud']
    lidar_bounding_box_3d = sample[0]['bounding_box_3d']
    lidar_class_ids = sample[0]['class_ids']
    lidar_instance_ids = sample[0]['instance_ids']
    lidar_extrinsics = sample[0]['extrinsics']
    lidar_pose = sample[0]['pose']

    idx = lidar_point_cloud[:, 2] < 100
    lidar_point_cloud = lidar_point_cloud[idx]

    # Get inside indices and filter the point_cloud for each bounding box
    lidar_inside_indices = get_inside_indices(lidar_point_cloud, lidar_bounding_box_3d)
    lidar_inside_points = [lidar_point_cloud[index] for index in lidar_inside_indices]

    ### Cameras are all the remaining sensors

    sample = sample[1:]

    camera_rgb = [np.array(smp['rgb']) for smp in sample]
    camera_intrinsics = [smp['intrinsics'] for smp in sample]
    camera_extrinsics = [smp['extrinsics'] for smp in sample]
    camera_pose = [smp['pose'] for smp in sample]

    # Create cameras for projection
    camera_cam = [Camera(K=intr, wh=rgb.shape[:2][::-1])
                  for intr, rgb in zip(camera_intrinsics, camera_rgb)]

    # Project 3d bounding box corners to each camera
    bounding_box_3d_2d = []
    world_corners = [(lidar_extrinsics * bbox).corners for bbox in lidar_bounding_box_3d]
    for i in range(len(sample)):
        bounding_box_3d_2d.append([])
        for j in range(len(world_corners)):
            cam_corners_j = camera_extrinsics[i].inverse() * world_corners[j]
            bounding_box_3d_2d[i].append(np.array(camera_cam[i].w2i(
                cam_corners_j, filter=True, padding=10000)[0]))

    return {
        'lidar': {
            'point_cloud': lidar_point_cloud,
            'inside_points': lidar_inside_points,
            'bounding_box_3d': lidar_bounding_box_3d,
            'class_ids': lidar_class_ids,
            'instances_ids': lidar_instance_ids,
            'extrinsics': lidar_extrinsics,
            'pose': lidar_pose,
        },
        'camera': {
            'rgb': camera_rgb,
            'bounding_box_3d_2d': bounding_box_3d_2d,
            'intrinsics': camera_intrinsics,
            'extrinsics': camera_extrinsics,
            'pose': camera_pose,
        }
    }


class CamvizBBoxes:
    def __init__(self, scale=1.0):

        wh = (1936, 1216)
        self.num_cameras = 6

        window_size = (wh[0] * 4 // 3, wh[1])
        window_size = [int(size * scale) for size in window_size]

        # Create window and different screens
        self.draw = Draw(window_size)
        self.draw.add3Dworld('wld', (0.50, 0.00, 1.00, 1.00), nf=(0.1, 1000), ref='lid',
                             pose=(-74.37884, 4.35606, 53.99322, 0.29453, 0.64556, -0.64107, 0.29248))
        self.draw.add2Dimage('img0', (0.00, 0.00, 0.25, 0.33), wh)
        self.draw.add2Dimage('img1', (0.25, 0.00, 0.50, 0.33), wh)
        self.draw.add2Dimage('img2', (0.00, 0.33, 0.25, 0.67), wh)
        self.draw.add2Dimage('img3', (0.25, 0.33, 0.50, 0.67), wh)
        self.draw.add2Dimage('img4', (0.00, 0.67, 0.25, 1.00), wh)
        self.draw.add2Dimage('img5', (0.25, 0.67, 0.50, 1.00), wh)

        # Create buffers
        self.draw.addBuffer3f('lidar_xyz', 1000000)
        self.draw.addBuffer3f('lidar_hgt', 1000000)
        for i in range(200):
            self.draw.addBuffer3f('lidar_inside_%d' % i, 10000)
        for i in range(self.num_cameras):
            self.draw.addTexture('img%d' % i, wh)

    def loop(self, dataset, n=0):

        change = True
        n_min, n_max = 0, len(dataset) - 1

        while self.draw.input():

            # If you press down
            if self.draw.DOWN and n > n_min:
                n -= 1
                change = True
            # If you press up
            if self.draw.UP and n < n_max:
                n += 1
                change = True

            # If there is a change, update buffers
            if change:
                change = False
                sample = parse_sample(dataset[n])

                lidar_xyz = sample['lidar']['point_cloud']
                self.draw.updBufferf('lidar_xyz', lidar_xyz)

                lidar_hgt = cmapJET(sample['lidar']['point_cloud'][:, 2], range=(-2, 10))
                self.draw.updBufferf('lidar_hgt', lidar_hgt)

                for i, inside_points in enumerate(sample['lidar']['inside_points']):
                    self.draw.updBufferf('lidar_inside_%d' % i, inside_points)
                for i in range(self.num_cameras):
                    self.draw.tex('img%d' % i).update(sample['camera']['rgb'][i])

            # Clear window
            self.draw.clear()

            # Draw lidar pointcloud + red dot in the center
            self.draw['wld'].size(2).points('lidar_xyz', 'lidar_hgt')
            self.draw['wld'].size(8).color('red').points(np.array([[0, 0, 0]]))

            # Draw 3d bounding boxes with colored inside points
            lidar_bounding_box_3d = [BBox3D(bbox.corners)
                                     for bbox in sample['lidar']['bounding_box_3d']]
            for i, bbox in enumerate(lidar_bounding_box_3d):
                class_color = get_class_color(sample['lidar']['class_ids'][i])
                self.draw['wld'].object(bbox, color_line=class_color)
                self.draw['wld'].size(4).color(class_color).points('lidar_inside_%d' % i)

            # Draw images and projected 3d bounding boxes
            for i in range(self.num_cameras):
                self.draw['img%d' % i].image('img%d' % i)
                for j, bbox in enumerate(sample['camera']['bounding_box_3d_2d'][i]):
                    if len(bbox) == 8:
                        class_color = get_class_color(sample['lidar']['class_ids'][j])
                        self.draw['img%d' % i].width(2).object(
                            BBox3D(bbox), color_line=class_color)

            # Update every 30ms
            self.draw.update(30)