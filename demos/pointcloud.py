# Copyright 2023 Toyota Research Institute.  All rights reserved.

import numpy as np

import camviz as cv

# Load evaluation data
data = np.load('demos/data/ddad_eval.npz')

# Get image resolution
wh = data['rgb'].shape[:2][::-1]

# Create draw tool with specific width and height window dimensions
draw = cv.Draw(wh=(2000, 900), title='CamViz Pointcloud Demo')

# Create image screen to show the RGB image
draw.add2Dimage('rgb', luwh=(0.00, 0.00, 0.33, 0.50), res=wh)

# Create image screen to show the depth visualization
draw.add2Dimage('viz', luwh=(0.00, 0.50, 0.33, 1.00), res=wh)

# Create world screen at specific position inside the window (% left/up/right/down)
draw.add3Dworld('wld', luwh=(0.33, 0.00, 1.00, 1.00),
    pose=(7.25323, -3.80291, -5.89996, 0.98435, 0.07935, 0.15674, 0.01431))

# Parse dictionary information
rgb = data['rgb']
intrinsics = data['intrinsics']
depth = data['depth']
viz = data['viz']

# Create camera from intrinsics and image dimensions (width and height)
camera = cv.objects.Camera(K=intrinsics, wh=wh)

# Project depth maps from image (i) to camera (c) coordinates
points = camera.i2c(depth)

# Create pointcloud colors
rgb_clr = rgb.reshape(-1, 3)                   # RGB colors
viz_clr = viz.reshape(-1, 3)                   # Depth visualization colors
hgt_clr = cv.utils.cmaps.jet(-points[:, 1])    # Height colors

# Create RGB and visualization textures
draw.addTexture('rgb', rgb)  # Create texture buffer to store rgb image
draw.addTexture('viz', viz)  # Create texture buffer to store visualization image

# Create buffers to store data for display
draw.addBufferf('pts', points)   # Create data buffer to store depth points
draw.addBufferf('clr', rgb_clr)  # Create data buffer to store rgb points color
draw.addBufferf('viz', viz_clr)  # Create data buffer to store pointcloud heights
draw.addBufferf('hgt', hgt_clr)  # Create data buffer to store pointcloud heights

# Color dictionary
color_dict = {0: 'clr', 1: 'viz', 2: 'hgt'}

# Display loop
color_mode = 0
while draw.input():
    # If RETURN is pressed, switch color mode
    if draw.RETURN:
        color_mode = (color_mode + 1) % len(color_dict)
    # Clear window
    draw.clear()
    # Draw image textures on their respective screens
    draw['rgb'].image('rgb')
    draw['viz'].image('viz')
    # Draw points and colors from buffer
    draw['wld'].size(2).points('pts', color_dict[color_mode])
    # Draw camera with texture as image
    draw['wld'].object(camera, tex='rgb')
    # Update window
    draw.update(30)
