"""
testing/inspect_subpart_vertices.py
Find the exact coordinates and overhang profiles of the cam and plunger in printable orientation.
"""

import sys, os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

parts = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False, return_subparts=True)

cam = parts['cam']
plunger = parts['plunger']

print("=== CAM TAB VERTICES & BOUNDS ===")
print("Cam bounds:", cam.bounds)
# Sort cam vertices by Z
cam_v = cam.vertices
print("\nTop 10 highest Z vertices on CAM:")
top_idx = np.argsort(cam_v[:, 2])[-10:]
for idx in reversed(top_idx):
    print(f"  V[{idx}]: X={cam_v[idx,0]:6.2f}, Y={cam_v[idx,1]:6.2f}, Z={cam_v[idx,2]:6.2f}")

print("\nCam downward facing faces (normals with nz < -0.1):")
c = cam.triangles_center
n = cam.face_normals
a = cam.area_faces
mask = n[:, 2] < -0.1
for idx in np.where(mask)[0]:
    angle_from_vert = np.degrees(np.arccos(np.clip(-n[idx, 2], -1, 1))) # angle from straight down
    print(f"  Face {idx:3d}: Center=[{c[idx,0]:5.2f}, {c[idx,1]:5.2f}, {c[idx,2]:5.2f}], n_z={n[idx,2]:6.3f} (tilt {angle_from_vert:4.1f}° from horiz), Area={a[idx]:5.2f} mm²")

print("\n=== PLUNGER ARM VERTICES & BOUNDS ===")
print("Plunger bounds:", plunger.bounds)
print("\nTop 10 highest Z vertices on PLUNGER:")
top_p_idx = np.argsort(plunger.vertices[:, 2])[-10:]
for idx in reversed(top_p_idx):
    pv = plunger.vertices[idx]
    print(f"  V[{idx}]: X={pv[0]:6.2f}, Y={pv[1]:6.2f}, Z={pv[2]:6.2f}")

print("\nPlunger downward facing faces with Z > 2.0 mm (n_z < -0.1):")
c_p = plunger.triangles_center
n_p = plunger.face_normals
a_p = plunger.area_faces
mask_p = (c_p[:, 2] > 2.0) & (n_p[:, 2] < -0.1)
for idx in np.where(mask_p)[0]:
    angle_from_horiz = np.degrees(np.arcsin(np.clip(-n_p[idx, 2], -1, 1))) # overhang angle
    print(f"  Face {idx:3d}: Center=[{c_p[idx,0]:5.2f}, {c_p[idx,1]:5.2f}, {c_p[idx,2]:5.2f}], n_z={n_p[idx,2]:6.3f}, Area={a_p[idx]:5.2f} mm²")
