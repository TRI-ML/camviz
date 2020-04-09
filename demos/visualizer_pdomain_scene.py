
import os
import argparse

from glob import glob
from dgp.datasets.pd_dataset import ParallelDomainScene
from camviz.visualizers.bboxes import CamvizBBoxes

parser = argparse.ArgumentParser(description='DGP-Camviz Visualization')
parser.add_argument('--path', type=str, help='path to s3 scene')
parser.add_argument('--folder', type=str, default=None, help='folder to save data')
args = parser.parse_args()

lidar = 'lidar'
cameras = ['camera_%02d' % idx for idx in [1, 5, 6, 7, 8, 9]]
annotations = ['bounding_box_3d']

if args.path.startswith('s3'):
    print('Downloading {} to {}'.format(args.path, args.folder))
    local_path = '{}/'.format(args.folder) + '/'.join(args.path.split('/')[-2:])
    os.system('aws s3 sync {} {} --quiet'.format(args.path, local_path))
    scene_dataset_json = glob(local_path + '/*.json')[0]
    print('Download done')
elif args.path.endswith('json'):
    scene_dataset_json = args.path

datum_names = [lidar] + cameras
requested_annotations = annotations

# Create dataset class
dataset = ParallelDomainScene(
    scene_dataset_json,
    datum_names=datum_names,
    requested_annotations=requested_annotations,
    requested_autolabels=None,
    backward_context=0,
    forward_context=0,
    generate_depth_from_datum=None,
    only_annotated_datums=False,
)

display = CamvizBBoxes()
display.loop(dataset)

