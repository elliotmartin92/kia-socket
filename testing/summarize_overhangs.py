"""
testing/summarize_overhangs.py
Summarize the steep overhangs on the plunger and cam.
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

# Plunger (Y < -1.0)
plunger_steep = [i for i, face in enumerate(f) if np.mean(v[face, 1]) < -1.0 and normals[i, 2] < -0.707 and np.min(v[face, 2]) > 0.15]
print("Plunger steep overhangs count:", len(plunger_steep))
for i in plunger_steep:
    print(f"  Face {i}: area={areas[i]:.2f}mm², z_min={np.min(v[f[i], 2]):.2f}mm, centroid={np.mean(v[f[i]], axis=0)}")

# Cam (Y > 1.5)
cam_steep = [i for i, face in enumerate(f) if np.mean(v[face, 1]) > 1.5 and normals[i, 2] < -0.707 and np.min(v[face, 2]) > 0.15]
print("\nCam steep overhangs count:", len(cam_steep))
for i in cam_steep:
    print(f"  Face {i}: area={areas[i]:.2f}mm², z_min={np.min(v[f[i], 2]):.2f}mm, centroid={np.mean(v[f[i]], axis=0)}")

# Axle pins (|X| > 3.70)
pin_steep = [i for i, face in enumerate(f) if np.abs(np.mean(v[face, 0])) > 3.70 and normals[i, 2] < -0.707 and np.min(v[face, 2]) > 0.15]
print("\nAxle Pin steep overhangs count:", len(pin_steep))
for i in pin_steep:
    print(f"  Face {i}: area={areas[i]:.2f}mm², z_min={np.min(v[f[i], 2]):.2f}mm, centroid={np.mean(v[f[i]], axis=0)}")

# Hub / Center (|X| <= 3.70 and -1.0 <= Y <= 1.5)
hub_steep = [i for i, face in enumerate(f) if np.abs(np.mean(v[face, 0])) <= 3.70 and -1.0 <= np.mean(v[face, 1]) <= 1.5 and normals[i, 2] < -0.707 and np.min(v[face, 2]) > 0.15]
print("\nHub / Center steep overhangs count:", len(hub_steep))
for i in hub_steep:
    print(f"  Face {i}: area={areas[i]:.2f}mm², z_min={np.min(v[f[i], 2]):.2f}mm, centroid={np.mean(v[f[i]], axis=0)}")
