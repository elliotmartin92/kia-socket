"""
testing/analyze_arm_angles.py
Check the overhang angles of the plunger arm and cam tab in the current printable orientation.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

shaft_print = build_shaft_rocker_mesh(in_assembly_coords=False)

v = shaft_print.vertices
f = shaft_print.faces
normals = shaft_print.face_normals
areas = shaft_print.area_faces

print("=" * 60)
print("ARM OVERHANG ANGLE ANALYSIS")
print("=" * 60)

# Check faces on plunger arm (Y < -1.0)
plunger_faces = [i for i, face in enumerate(f) if np.mean(v[face, 1]) < -1.0]
print(f"Plunger arm faces: {len(plunger_faces)}")

plunger_downward = []
for i in plunger_faces:
    n_z = normals[i, 2]
    if n_z < -0.01:
        angle_to_vert = np.degrees(np.arccos(np.clip(-n_z, -1.0, 1.0)))
        angle_to_horiz = 90.0 - angle_to_vert
        plunger_downward.append((i, areas[i], n_z, angle_to_horiz, np.mean(v[f[i]], axis=0)))

print(f"Plunger downward-facing faces: {len(plunger_downward)}")
for i, area, n_z, ang_h, cent in plunger_downward:
    print(f"  Face {i}: area={area:.2f}mm², normal_z={n_z:+.3f}, angle_to_horizontal={ang_h:.1f}°, centroid=({cent[0]:.2f}, {cent[1]:.2f}, {cent[2]:.2f})")

# Check faces on cam tab (Y > 1.5)
cam_faces = [i for i, face in enumerate(f) if np.mean(v[face, 1]) > 1.5]
print(f"\nCam tab faces: {len(cam_faces)}")
cam_downward = []
for i in cam_faces:
    n_z = normals[i, 2]
    if n_z < -0.01:
        angle_to_vert = np.degrees(np.arccos(np.clip(-n_z, -1.0, 1.0)))
        angle_to_horiz = 90.0 - angle_to_vert
        cam_downward.append((i, areas[i], n_z, angle_to_horiz, np.mean(v[f[i]], axis=0)))

print(f"Cam downward-facing faces: {len(cam_downward)}")
for i, area, n_z, ang_h, cent in cam_downward:
    print(f"  Face {i}: area={area:.2f}mm², normal_z={n_z:+.3f}, angle_to_horizontal={ang_h:.1f}°, centroid=({cent[0]:.2f}, {cent[1]:.2f}, {cent[2]:.2f})")
