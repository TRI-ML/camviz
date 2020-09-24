# Camviz
TRI Visualization Library

# Visualizing PD data

## Clone this repository

```
git clone git@github.com:TRI-ML/camviz.git
```

## Clone PackNet-SfM (specific branch)

```
 git clone -b multi-task-adaptation git@github.com:VitorGuizilini-TRI/packnet-sfm_internal.git
```
and add it to your $PYTHONPATH

## Clone Ouroboros

```
git clone git@github.awsinternal.tri.global:ouroboros/ouroboros.git
```
and add it to your $PYTHONPATH. Also, build the protobufs:
```
cd ouroboros/dgp & make build-proto
```

## Run visualizer (from camviz root folder)
```
python3 visualizers/draw_dataset_multicam.py --path /data/datasets/pd_phase2_010_00/scene_dataset_v00.json --start_frame 0 --cameras 1 5 --depth_type zbuffer --split train
```
