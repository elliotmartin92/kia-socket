"""
testing/inspect_bed_contact.py
Inspect what touches the bed at Z=0.00mm.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

shaft_print = build_shaft_rocker_mesh(in_assembly_coords=False)

v = shaft_print.vertices
f = shaft_print.faces

# Find all vertices with Z < 0.05
near_bed_v_idx = np.where(v[:, 2] < 0.05)[0]
print(f"Total vertices at Z < 0.05mm: {len(near_bed_v_idx)}")
print(f"X bounds of bed contact: [{np.min(v[near_bed_v_idx, 0]):.2f}, {np.max(v[near_bed_v_idx, 0]):.2f}]")
print(f"Y bounds of bed contact: [{np.min(v[near_bed_v_idx, 1]):.2f}, {np.max(v[near_bed_v_idx, 1]):.2f}]")

# Let's inspect which faces have all vertices at Z < 0.05
flat_bed_faces = []
for i, face in enumerate(f):
    if np.all(v[face, 2] < 0.05):
        flat_bed_faces.append(i)

print(f"Flat bed faces count: {len(flat_bed_faces)}")
for i in flat_bed_faces:
    print(f"  Face {i}: normal={shaft_print.face_normals[i]}, area={shaft_print.area_faces[i]:.2f}, centroid={np.mean(v[face], axis=0)}")
