
import numpy as np

from camviz.draw import Draw
from camviz.utils import cmapJET
from camviz.objects.camera import Camera


# Color dictionary for each camera
camera_colors = {
    0: 'mag',
    1: 'red',
    2: 'blu',
    3: 'cya',
    4: 'gre',
    5: 'yel',
}


def parse_sample(sample):
    """Takes a DGP sample and parses it for visualization"""

    # Initialize the parsed sample
    prep_sample = {
        'lidar': {},
        'camera': {},
    }

    ### Lidar is assumed to be the first sensor

    # Extract lidar information
    lidar_point_cloud = sample[0]['point_cloud']
    lidar_extrinsics = sample[0]['extrinsics']
    lidar_pose = sample[0]['pose']

    prep_sample['lidar'].update({
            'point_cloud': lidar_point_cloud,
            'extrinsics': lidar_extrinsics,
            'pose': lidar_pose,
    })

    ### Cameras are all the remaining sensors

    sample = sample[1:]

    # Extract camera information
    camera_rgb = [np.array(smp['rgb']) for smp in sample]
    camera_intrinsics = [smp['intrinsics'] for smp in sample]
    camera_extrinsics = [smp['extrinsics'] for smp in sample]
    camera_depth = [smp['depth'] for smp in sample]
    camera_pose = [smp['pose'] for smp in sample]

    prep_sample['camera'].update({
        'rgb': camera_rgb,
        'intrinsics': camera_intrinsics,
        'extrinsics': camera_extrinsics,
        'pose': camera_pose,
    })

    # Create camera classes
    camera_cam = []
    for rgb, intrinsics, extrinsics in zip(camera_rgb, camera_intrinsics, camera_extrinsics):
        camera_cam.append(Camera(wh=rgb.shape[:2][::-1], K=intrinsics, pose=extrinsics.matrix))

    prep_sample['camera'].update({
        'cam': camera_cam,
    })

    # Create camera point cloud
    camera_point_cloud = []
    for rgb, depth, cam in zip(camera_rgb, camera_depth, camera_cam):
        point_cloud = cam.i2w(rgb, depth)
        idx = depth.reshape(-1) > 0
        point_cloud, point_cloud_color = point_cloud[idx], rgb.reshape(-1, 3)[idx]
        camera_point_cloud.append(np.concatenate([point_cloud, point_cloud_color], 1))

    prep_sample['camera'].update({
        'point_cloud': camera_point_cloud,
    })

    # Create camera projected points
    camera_projection = []
    for point_cloud, cam in zip(camera_point_cloud, camera_cam):
        projection, projection_z, idx = cam.w2i(
            point_cloud[:, :3], filter=True, return_z=True)
        camera_projection.append(np.concatenate(
            [projection, projection_z, point_cloud[idx, 3:]], 1))

    prep_sample['camera'].update({
        'projection': camera_projection,
    })

    # Create camera cross_projected points
    camera_cross_projection = []
    for i, cam in enumerate(camera_cam):
        camera_cross_projection.append([])
        for j, point_cloud in enumerate(camera_point_cloud):
            if i != j:
                cross_projection, cross_projection_z, idx = cam.w2i(
                    point_cloud[:, :3], filter=True, return_z=True)
                camera_cross_projection[i].append(np.concatenate(
                    [cross_projection, cross_projection_z, point_cloud[idx, 3:]], 1))
        camera_cross_projection[i] = np.concatenate(camera_cross_projection[i], 0)

    prep_sample['camera'].update({
        'cross_projection': camera_cross_projection,
    })

    return prep_sample


def prep_projection(draw, buffer, key, i):
    draw.updBufferf('%s_%d' % (buffer, i), key[i][:, :2])
    draw.updBufferf('%s_rgb_%d' % (buffer, i), key[i][:, 3:] / 255)
    draw.updBufferf('%s_z_%d' % (buffer, i), cmapJET(key[i][:, 2], range=(0.1, 100), exp=0.75))
    return draw


class CamvizDepth:
    def __init__(self, num_cams=6, wh=(1936, 1216), scale=3):

        self.num_cams = num_cams
        self.draw = Draw((wh[0] * 4 // scale, wh[1] * 3 // scale))

        self.draw.add3Dworld('wld', (0.50, 0.00, 1.00, 1.00), nf=(0.1, 1000), ref='lid',
                             pose=(-15.87691, -0.34308, 4.47827, 0.46147, 0.55535, -0.53210, 0.44215))
        self.draw.add2Dimage('cam_0', (0.00, 0.00, 0.25, 0.33), wh)
        self.draw.add2Dimage('cam_1', (0.00, 0.33, 0.25, 0.67), wh)
        self.draw.add2Dimage('cam_2', (0.00, 0.67, 0.25, 1.00), wh)
        self.draw.add2Dimage('cam_3', (0.25, 0.00, 0.50, 0.33), wh)
        self.draw.add2Dimage('cam_4', (0.25, 0.33, 0.50, 0.67), wh)
        self.draw.add2Dimage('cam_5', (0.25, 0.67, 0.50, 1.00), wh)

        self.draw.addBuffer3f('lid_xyz', 1000000)
        self.draw.addBuffer3f('lid_hgt', 1000000)

        for i in range(num_cams):
            self.draw.addTexture('cam_%d' % i, wh)
            self.draw.addBuffer3f('pcl_%d' % i, 1000000)
            self.draw.addBuffer3f('rgb_%d' % i, 1000000)
            self.draw.addBuffer2f('proj_%d' % i, 1000000)
            self.draw.addBuffer3f('proj_rgb_%d' % i, 1000000)
            self.draw.addBuffer3f('proj_z_%d' % i, 1000000)
            self.draw.addBuffer2f('cross_%d' % i, 1000000)
            self.draw.addBuffer3f('cross_rgb_%d' % i, 1000000)
            self.draw.addBuffer3f('cross_z_%d' % i, 1000000)

    def loop(self, dataset, n=0):

        change = True
        nmin, nmax = 0, len(dataset) - 1

        show_pcl, show_img, show_proj = 0, 0, 0
        keys_proj = {0: 'proj', 1: 'cross'}

        while self.draw.input():

            if self.draw.SPACE:
                show_pcl = (show_pcl + 1) % 3
            if self.draw.RETURN:
                show_img = (show_img + 1) % 3
            if self.draw.RSHIFT:
                show_proj = (show_proj + 1) % 2

            if self.draw.UP and n < nmax:
                n = n + 1
                change = True
            if self.draw.DOWN and n > nmin:
                n = n - 1
                change = True

            if change:
                change = False

                data = parse_sample(dataset[n])
                lidar, camera = data['lidar'], data['camera']

                self.draw.updBufferf('lid_xyz', lidar['point_cloud'])
                self.draw.updBufferf('lid_hgt', cmapJET(lidar['point_cloud'][:, 2], range=(-2, 10)))

                for i in range(self.num_cams):
                    self.draw.tex('cam_%d' % i).update(camera['rgb'][i])
                    self.draw.updBufferf('pcl_%d' % i, camera['point_cloud'][i][:, :3])
                    self.draw.updBufferf('rgb_%d' % i, camera['point_cloud'][i][:, 3:] / 255)
                    self.draw = prep_projection(self.draw, 'proj', camera['projection'], i)
                    self.draw = prep_projection(self.draw, 'cross', camera['cross_projection'], i)

            self.draw.clear()
            for i in range(self.num_cams):
                if show_img == 0:
                    self.draw['cam_%d' % i].image('cam_%d' % i)
                elif show_img == 1:
                    self.draw['cam_%d' % i].image('cam_%d' % i)
                    self.draw['cam_%d' % i].size(2).color('whi').points(
                        '%s_%d' % (keys_proj[show_proj], i), '%s_z_%d' % (keys_proj[show_proj], i))
                elif show_img == 2:
                    self.draw['cam_%d' % i].size(2).color('whi').points(
                        '%s_%d' % (keys_proj[show_proj], i), '%s_rgb_%d' % (keys_proj[show_proj], i))
                self.draw['wld'].object(camera['cam'][i], tex='cam_%d' % i)
                if show_pcl == 0:
                    self.draw['wld'].size(2).points('lid_xyz', 'lid_hgt')
                elif show_pcl == 1:
                    self.draw['wld'].size(2).color(camera_colors[i]).points('pcl_%d' % i)
                elif show_pcl == 2:
                    self.draw['wld'].size(2).points('pcl_%d' % i, 'rgb_%d' % i)

            self.draw.update(30)

