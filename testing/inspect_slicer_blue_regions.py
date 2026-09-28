"""
testing/inspect_slicer_blue_regions.py
Inspect the exact geometric features corresponding to the blue lines in the user's slicer:
1. Underside of Cam tab
2. Flank/underside of Plunger arm near base (Z in [2, 7] mm)
"""

import sys, os
import trimesh
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

parts = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False, return_subparts=True)
plunger = parts['plunger']
cam = parts['cam']
rib1 = parts['rib1']
rib3 = parts['rib3']
web = parts['web']

print("=== PLUNGER LOW-Z DOWNWARD FACES (Z in [1.0, 8.0]) ===")
c = plunger.triangles_center
n = plunger.face_normals
a = plunger.area_faces

mask_p = (c[:, 2] >= 1.0) & (c[:, 2] <= 8.0) & (n[:, 2] < -0.2)
for idx in np.where(mask_p)[0]:
    print(f"Face {idx:3d}: Center=[X={c[idx,0]:5.2f}, Y={c[idx,1]:5.2f}, Z={c[idx,2]:5.2f}], n=[{n[idx,0]:5.2f}, {n[idx,1]:5.2f}, {n[idx,2]:5.2f}], Area={a[idx]:4.2f}")

print("\n=== CAM LOW/MID-Z DOWNWARD FACES (Z in [1.0, 10.0]) ===")
c_c = cam.triangles_center
n_c = cam.face_normals
a_c = cam.area_faces

mask_c = (c_c[:, 2] >= 1.0) & (c_c[:, 2] <= 10.0) & (n_c[:, 2] < -0.2)
for idx in np.where(mask_c)[0]:
    print(f"Face {idx:3d}: Center=[X={c_c[idx,0]:5.2f}, Y={c_c[idx,1]:5.2f}, Z={c_c[idx,2]:5.2f}], n=[{n_c[idx,0]:5.2f}, {n_c[idx,1]:5.2f}, {n_c[idx,2]:5.2f}], Area={a_c[idx]:4.2f}")

print("\n=== RIB1 & RIB3 (FLANKS) DOWNWARD FACES ===")
for r_name, r_mesh in [('rib1', rib1), ('rib3', rib3)]:
    c_r = r_mesh.triangles_center
    n_r = r_mesh.face_normals
    mask_r = (c_r[:, 2] >= 1.0) & (n_r[:, 2] < -0.2)
    print(f"{r_name}: {np.sum(mask_r)} downward faces")
    for idx in np.where(mask_r)[0]:
        print(f"  Face {idx:3d}: Center=[X={c_r[idx,0]:5.2f}, Y={c_r[idx,1]:5.2f}, Z={c_r[idx,2]:5.2f}], n_z={n_r[idx,2]:5.2f}")
