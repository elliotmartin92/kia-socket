import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from build_shaft import build_shaft_rocker_mesh

subparts = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False, return_subparts=True)
cam = subparts['cam']
hub = subparts['hub']

# The boundary between cam and the outside of hub
# Let's subtract hub from cam
cam_outside = cam.difference(hub, engine='manifold')
print(f"Cam outside hub volume: {cam_outside.volume:.3f} mm^3")
print(f"Cam outside hub bounds: {cam_outside.bounds.tolist()}")

# Let's inspect the contact area / cross section where cam joins hub:
# In assembly coords, the hub is a cylinder along X from 5.80 to 12.70, radius 2.10 at Y=9.279, Z=11.190.
# The cam is from X=5.80 to 7.70.
# Let's slice cam_outside right at the hub boundary:
# A cylinder surface at r=2.10.
# What is the cross section of cam at r=2.15 (just outside hub)?
# Let's sample points along the cam mesh on the hub boundary
import trimesh.proximity
prox = trimesh.proximity.ProximityQuery(hub)
d = prox.signed_distance(cam_outside.vertices)
near_hub = np.where(np.abs(d) < 0.05)[0]
print(f"Number of vertices of cam_outside on hub boundary: {len(near_hub)}")
pts_near = cam_outside.vertices[near_hub]
print(f"X range of junction: [{pts_near[:, 0].min():.3f}, {pts_near[:, 0].max():.3f}]")
print(f"Y range of junction: [{pts_near[:, 1].min():.3f}, {pts_near[:, 1].max():.3f}]")
print(f"Z range of junction: [{pts_near[:, 2].min():.3f}, {pts_near[:, 2].max():.3f}]")
