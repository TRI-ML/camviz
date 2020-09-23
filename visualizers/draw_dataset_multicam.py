# Copyright 2020 Toyota Research Institute.  All rights reserved.

import argparse

import numpy as np
from ouroboros.dgp.utils.pose import Pose as Pose_DGP
from packnet_sfm.datasets.augmentations import to_tensor_sample
from packnet_sfm.datasets.ouroboros_dataset import OuroborosDataset
from packnet_sfm.utils.depth import viz_inv_depth, depth2inv
from packnet_sfm.utils.semantic import color_semantic, color_instance

from camviz.draw import Draw
from camviz.objects.bbox2d import BBox2D
from camviz.objects.bbox3d import BBox3D
from camviz.objects.camera import Camera
from camviz.utils.utils import cmapJET
from visualizers.draw_base import DrawBase
from visualizers.draw_utils import common_args


class DrawDatasetMultiCam(DrawBase):
    """
    Visualization tool for drawing multi-camera evaluation results.
    How to use: first run the "eval.py" script with the "save.depth.data" option enabled.
    You can then run this script pointing to the resulting folder.

    Parameters
    ----------
    files : list
        List containing the data files for each camera
    args : Namespace
        Arguments used by the visualizer
    """
    def __init__(self, files, args):
        super().__init__(files, args)
        # Set flags and dictionaries
        self.flag_pcl_color = 0
        self.dict_flag_pcl_color = {
            0: 'pcl_hgt%d', 1: 'pcl_rgb%d', 2: 'pcl_sem%d', 3: 'pcl_ins%d',
            # 4: 'msk3_pcl_hgt%d', 5: 'msk3_pcl_rgb%d', 6: 'msk3_pcl_sem%d',
            # 6: 'ins2_pcl_hgt%d', 7: 'ins2_pcl_rgb%d', 8: 'ins2_pcl_sem%d'
        }
        self.flag_cam = 0
        # self.dict_flag_cam = {0: 'rgb%d', 1: 'dep%d', 2: 'dep3%d', 3: 'dep2%d', 4: 'sem%d'}
        self.dict_flag_cam = {0: 'rgb%d', 1: 'dep%d', 2: 'sem%d', 3: 'ins%d'}
        self.flag_cache = 0
        self.flag_bbox2d = self.flag_bbox3d = False
        self.context_size = self.flag_context_idx = 0

        # Prepare data
        self.cams = []
        self.cams_context = []
        self.bboxes3d = []
        self.bboxes3d_proj = []
        self.bboxes2d = []
        self.ncams = len(args.cameras)
        self.prepare(self.get_data())

    def prepare(self, data):
        """Prepare visualization"""
        # Image dimensions
        wh = data['rgb'][0].shape[1:][::-1]
        wh = tuple([int(val * args.scale) for val in wh])
        # Initial pose
        pose = data['pose'][0].copy()
        # Check for available data
        self.with_context = 'rgb_context' in data
        self.with_bbox2d = 'bbox2d' in data
        self.with_bbox2d_depth = 'bbox2d_depth' in data
        self.with_bbox3d = 'bbox3d' in data
        self.with_bbox3d_depth = 'bbox3d_depth' in data
        self.with_semantic = 'semantic' in data
        self.with_instance = 'instance' in data
        self.with_pointcache = 'pointcache' in data
        # Create window
        self.draw = Draw((wh[0] * self.scale * 4 / 3, wh[1] * self.scale))
        self.draw.add3Dworld('wld', (0.5, 0.0, 1.0, 1.0), ref='lidar', nf=(0.1, 1000.), pose=pose)
        self.draw.scr('wld').viewer.translateZ(-20).translateY(-10).rotateX(25)
        self.draw.scr('wld').saveViewer()
        # Create 2D image screens and textures
        for i in range(self.ncams):
            x, y = i % 2, i % 3
            shape = data['rgb'][i].shape[1:][::-1]
            # Create screen
            self.draw.add2Dimage('cam%d' % i, (0.25 * x, 0.33 * y,
                                               0.25 * (x + 1), 0.33 * (y + 1)), shape)
            # Create image textures
            self.draw.addTexture('rgb%d' % i, shape)
            if self.with_context:
                self.context_size = len(data['rgb_context'])
                for j in range(self.context_size):
                    self.draw.addTexture('rgb%d%d' % (j, i), shape)
            # Create depth textures
            self.draw.addTexture('dep%d' % i, shape)
            if self.with_bbox2d_depth:
                self.draw.addTexture('dep2%d' % i, shape)
            if self.with_bbox3d_depth:
                self.draw.addTexture('dep3%d' % i, shape)
            # Create annotation textures
            if self.with_semantic:
                self.draw.addTexture('sem%d' % i, shape)
            if self.with_instance:
                self.draw.addTexture('ins%d' % i, shape)
        # Create buffers
        for i in range(self.ncams):
            # Add pointcloud buffers
            self.draw.addBuffer3f('pcl%d' % i, 1000000)
            self.draw.addBuffer3f('pcl_rgb%d' % i, 1000000)
            self.draw.addBuffer3f('pcl_sem%d' % i, 1000000)
            self.draw.addBuffer3f('pcl_ins%d' % i, 1000000)
            self.draw.addBuffer3f('pcl_hgt%d' % i, 1000000)
            # Add 2d bboxes buffer
            if self.with_bbox2d_depth:
                self.draw.addBuffer3f('msk2_pcl%d' % i, 1000000)
                self.draw.addBuffer3f('msk2_pcl_rgb%d' % i, 1000000)
                self.draw.addBuffer3f('msk2_pcl_sem%d' % i, 1000000)
                self.draw.addBuffer3f('msk2_pcl_hgt%d' % i, 1000000)
            # Add 3d bboxes buffer
            if self.with_bbox3d_depth:
                self.draw.addBuffer3f('msk3_pcl%d' % i, 1000000)
                self.draw.addBuffer3f('msk3_pcl_rgb%d' % i, 1000000)
                self.draw.addBuffer3f('msk3_pcl_sem%d' % i, 1000000)
                self.draw.addBuffer3f('msk3_pcl_hgt%d' % i, 1000000)
            # Add pointcache buffer
            if self.with_pointcache:
                self.draw.addBuffer3f('pointcache%d' % i, 10000000)
        # First update
        self.update(data)

    def get_data(self, n=None):
        """Get data from a new sample"""
        # Get data from a new frame
        n = self.n if n is None else n
        return self.files[n]

    def update(self, data):
        """Update visualization with new data"""
        # Clear lists
        self.cams.clear()
        if self.with_context:
            self.cams_context = [[] for _ in range(self.context_size)]
        self.bboxes2d.clear()
        self.bboxes3d.clear()
        self.bboxes3d_proj.clear()
        # For every camera
        for i in range(self.ncams):
            # Get camera pose
            pose = data['pose'][i]
            intrinsics = data['intrinsics'][i]
            # Get and store image data
            rgb = data['rgb'][i].detach().cpu().numpy().transpose(1, 2, 0)
            rgb_shape = rgb.shape[:2][::-1]
            self.draw.updTexture('rgb%d' % i, rgb * 255)
            # Create and append camera
            cam = Camera(wh=rgb_shape, K=intrinsics, pose=pose)
            self.cams.append(cam)
            # If there is a context
            if self.with_context:
                pose_dgp = Pose_DGP.from_matrix(pose)
                for j in range(self.context_size):
                    rgb_ji = data['rgb_context'][j][i]
                    pose_context_ji = pose_dgp * Pose_DGP.from_matrix(data['pose_context'][j][i])
                    cam_context_ji = Camera(wh=rgb_shape, K=intrinsics, pose=pose_context_ji.matrix)
                    self.cams_context[j].append(cam_context_ji)
                    self.draw.updTexture('rgb%d%d' % (j, i), rgb_ji * 255)
            # Get and store depth data
            depth = data['depth'][i].detach().cpu().numpy().squeeze()
            self.draw.updTexture('dep%d' % i, viz_inv_depth(depth2inv(depth), filter_zeros=True) * 255)
            # Get and store 2D bbox data
            if self.with_bbox2d:
                bbox2d = data['bbox2d'][i]
                self.bboxes2d.append([BBox2D(b) for b in bbox2d])
            # Get and store 3D bbox data
            if self.with_bbox3d:
                bbox3d = data['bbox3d'][i]
                self.bboxes3d.append([BBox3D(b) for b in bbox3d])
                self.bboxes3d_proj.append([BBox3D(cam.w2i(b)) for b in bbox3d])
            # Get and store pointcache data
            if self.with_pointcache:
                pointcache = data['pointcache'][i]
                if len(pointcache) > 0:
                    points = np.concatenate([val for val in pointcache.values()], 0)
                    self.draw.updBufferf('pointcache%d' % i, points)
                else:
                    self.draw.clrBuffer('pointcache%d' % i)
            # Get and store pointcloud data
            idx1 = depth.reshape(-1) > 0
            pcl = cam.i2w(rgb, depth)[idx1]
            pcl_rgb = rgb.reshape(-1, 3)[idx1]
            pcl_hgt = cmapJET(pcl[:, 2], range=(11, 35), exp=0.5).clip(0, 1)
            self.draw.updBufferf('pcl%d' % i, pcl)
            self.draw.updBufferf('pcl_rgb%d' % i, pcl_rgb)
            self.draw.updBufferf('pcl_hgt%d' % i, pcl_hgt)
            # Get and store semantic data
            if self.with_semantic:
                semantic = data['semantic'][i]
                semantic_color = color_semantic(semantic, data['ontology'][i])
                pcl_sem = semantic_color.reshape(-1, 3)[idx1]
                self.draw.updTexture('sem%d' % i, semantic_color * 255)
                self.draw.updBufferf('pcl_sem%d' % i, pcl_sem)
            # Get and store instance data
            if self.with_instance:
                instance = data['instance'][i]
                instance_color = color_instance(instance)
                pcl_ins = instance_color.reshape(-1, 3)[idx1]
                self.draw.updTexture('ins%d' % i, instance_color * 255)
                self.draw.updBufferf('pcl_ins%d' % i, pcl_ins)
            # Get and store 2D bbox data
            if self.with_bbox2d_depth:
                bbox2d_depth = data['bbox2d_depth'][i].detach().cpu().numpy().squeeze()
                idx2 = (bbox2d_depth.reshape(-1) > 0)[idx1]
                msk2_pcl = cam.i2w(rgb, bbox2d_depth)[idx1][idx2]
                msk2_pcl_rgb = pcl_rgb[idx2]
                msk2_pcl_hgt = pcl_hgt[idx2]
                self.draw.updBufferf('msk2_pcl%d' % i, msk2_pcl)
                self.draw.updBufferf('msk2_pcl_rgb%d' % i, msk2_pcl_rgb)
                self.draw.updBufferf('msk2_pcl_hgt%d' % i, msk2_pcl_hgt)
                self.draw.updTexture('dep2%d' % i, viz_inv_depth(depth2inv(bbox2d_depth), filter_zeros=True) * 255)
                # Include 2D bbox semantic data
                if self.with_semantic:
                    msk2_pcl_sem = pcl_sem[idx2]
                    self.draw.updBufferf('msk2_pcl_sem%d' % i, msk2_pcl_sem)
            # Get and store 3D bbox data
            if self.with_bbox3d_depth:
                bbox3d_depth = data['bbox3d_depth'][i].detach().cpu().numpy().squeeze()
                idx3 = (bbox3d_depth.reshape(-1) > 0)[idx1]
                msk3_pcl = cam.i2w(rgb, bbox3d_depth)[idx1][idx3]
                msk3_pcl_rgb = pcl_rgb[idx3]
                msk3_pcl_hgt = pcl_hgt[idx3]
                self.draw.updBufferf('msk3_pcl%d' % i, msk3_pcl)
                self.draw.updBufferf('msk3_pcl_rgb%d' % i, msk3_pcl_rgb)
                self.draw.updBufferf('msk3_pcl_hgt%d' % i, msk3_pcl_hgt)
                self.draw.updTexture('dep3%d' % i, viz_inv_depth(depth2inv(bbox3d_depth), filter_zeros=True) * 255)
                # Include 3D bbox semantic data
                if self.with_semantic:
                    msk3_pcl_sem = pcl_sem[idx3]
                    self.draw.updBufferf('msk3_pcl_sem%d' % i, msk3_pcl_sem)

    def display(self):
        """Display stored information"""
        self.draw.clear()
        # Display cameras
        for i in range(self.ncams):
            self.draw['wld'].object(self.cams[i], tex='rgb%d' % i,
                                    color='whi' if self.flag_context_idx == 0 else 'gra')
            for j in range(self.context_size):
                self.draw['wld'].object(self.cams_context[j][i], tex='rgb%d%d' % (j, i),
                                        color='whi' if self.flag_context_idx == j + 1 else 'gra')
        # Display 3D bboxes
        if self.with_bbox3d and self.flag_bbox3d:
            for bbox3d in self.bboxes3d:
                for bbox in bbox3d:
                    self.draw['wld'].object(bbox)
        # For each camera
        for i in range(self.ncams):
            # Get pointcloud data and color
            color = self.dict_flag_pcl_color[self.flag_pcl_color]
            data = 'msk3_pcl%d' if 'msk3' in color else 'msk2_pcl%d' if 'msk2' in color else 'pcl%d'
            self.draw['wld'].size(2).points(data % i, color % i)
            # Display camera image
            if self.flag_context_idx == 0:
                self.draw['cam%d' % i].image(self.dict_flag_cam[self.flag_cam] % i)
            else:
                self.draw['cam%d' % i].image('rgb%d%d' % (self.flag_context_idx - 1, i))
            # Display 2D bboxes
            if self.with_bbox2d and self.flag_bbox2d:
                for bbox in self.bboxes2d[i]:
                    self.draw['cam%d' % i].object(bbox, color_line='yel')
            # Display 3D bboxes
            if self.with_bbox3d and self.flag_bbox3d:
                for bbox in self.bboxes3d_proj[i]:
                    self.draw['cam%d' % i].object(bbox, color_line='gre')
            # Display pointcache
            if self.flag_cache:
                self.draw['wld'].size(1).color('whi').points('pointcache%d' % i)
        # Update display
        self.draw.update(30)

    def commands(self):
        """Commands to control the screen"""
        super().commands()
        # Change pointcloud mode
        if self.draw.RSHIFT:
            self.flag_pcl_color = (self.flag_pcl_color + 1) % len(self.dict_flag_pcl_color)
            self.draw.halt(500)
        # Change camera mode
        if self.draw.LSHIFT:
            self.flag_cam = (self.flag_cam + 1) % len(self.dict_flag_cam)
            self.draw.halt(500)
        if self.draw.SPACE:
            self.flag_cache = not self.flag_cache
            self.draw.halt(500)
        # Change context
        if self.draw.LEFT:
            self.flag_context_idx = (self.flag_context_idx - 1) % (self.context_size + 1)
            self.draw.halt(500)
        if self.draw.RIGHT:
            self.flag_context_idx = (self.flag_context_idx + 1) % (self.context_size + 1)
            self.draw.halt(500)
        # Toggle flags
        if self.draw.KEY_2:
            self.flag_bbox2d = not self.flag_bbox2d
            self.draw.halt(500)
        if self.draw.KEY_3:
            self.flag_bbox3d = not self.flag_bbox3d
            self.draw.halt(500)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Multi-camera evaluation display')
    parser = common_args(parser, mode='dataset-multicam')
    args = parser.parse_args()

    dataset = OuroborosDataset(
        args.path, args.split,
        with_semantic=True,
        with_instance=True,
        with_bbox2d=True,
        with_bbox3d=True,
        bbox2d_depth=True,
        bbox3d_depth=True,
        with_pose=True,
        with_pointcache=True,
        back_context=1, forward_context=1,
        cameras=['camera_%02d' % cam for cam in args.cameras],
        depth_type=args.depth_type,
        data_transform=to_tensor_sample,
        return_ontology=True,
        ontology='parallel_domain',
        dataset='parallel_domain',
    )

    # Create draw tool
    draw = DrawDatasetMultiCam(dataset, args)
    # Loop over draw tool
    draw.loop()



