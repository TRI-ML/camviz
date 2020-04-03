
import argparse
from dgp.datasets.pd_dataset import ParallelDomainSceneDataset
from camviz.visualizers.bboxes import CamvizBBoxes


parser = argparse.ArgumentParser(description='DGP-Camviz Visualization')
parser.add_argument('--json', type=str,
                    help='DGP dataset json')
parser.add_argument('--split', type=str,
                    help='DGP dataset split',
                    default='train')
parser.add_argument('--lidar', type=str,
                    help='LiDAR datum name',
                    default='lidar')
parser.add_argument('--cameras', type=int, nargs='+',
                    help='Camera datum names (camera_%02d)',
                    default=[1, 5, 6, 7, 8, 9])
parser.add_argument('--annotations', type=str, nargs='+',
                    help='Requested annotations',
                    default=['bounding_box_3d'])
args = parser.parse_args()
args.cameras = ['camera_%02d' % idx for idx in args.cameras]

# Arguments for dataset
scene_dataset_json, split = args.json, args.split
datum_names = [args.lidar] + args.cameras
requested_annotations = args.annotations

# Create dataset class
dataset = ParallelDomainSceneDataset(
    scene_dataset_json,
    split=split,
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

