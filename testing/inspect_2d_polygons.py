"""
testing/inspect_2d_polygons.py
Inspect the exact 2D (Y, Z) boundary polygons of Cam and Plunger in printable coordinates.
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

parts = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False, return_subparts=True)

cam = parts['cam']
plunger = parts['plunger']

# Extract 2D exterior boundary on Y-Z
# Since Cam is extruded along X, its vertices at X_min and X_max have the exact Y-Z cross section!
v_cam = cam.vertices
# Get vertices at one face (e.g. min X)
x_min_cam = v_cam[:, 0].min()
face_cam_v = v_cam[np.isclose(v_cam[:, 0], x_min_cam, atol=1e-3)]

print("=== CAM 2D BOUNDARY VERTICES (Y, Z) ===")
# Sort by angle around centroid
c_cam = np.mean(face_cam_v[:, 1:], axis=0)
angles = np.arctan2(face_cam_v[:, 2] - c_cam[1], face_cam_v[:, 1] - c_cam[0])
order = np.argsort(angles)
for idx in order:
    print(f"  Y: {face_cam_v[idx, 1]:6.2f} mm, Z: {face_cam_v[idx, 2]:6.2f} mm")

# Do the same for plunger
v_plunger = plunger.vertices
x_min_plunger = v_plunger[:, 0].min()
face_plunger_v = v_plunger[np.isclose(v_plunger[:, 0], x_min_plunger, atol=1e-3)]

print("\n=== PLUNGER 2D BOUNDARY VERTICES (Y, Z) ===")
c_p = np.mean(face_plunger_v[:, 1:], axis=0)
angles_p = np.arctan2(face_plunger_v[:, 2] - c_p[1], face_plunger_v[:, 1] - c_p[0])
order_p = np.argsort(angles_p)
for idx in order_p:
    print(f"  Y: {face_plunger_v[idx, 1]:6.2f} mm, Z: {face_plunger_v[idx, 2]:6.2f} mm")
