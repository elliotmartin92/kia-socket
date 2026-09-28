"""
testing/inspect_overhang_locations.py
Identify exactly which subparts own the overhang faces in shaft_printable.
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

# Find all faces with downward normals (n_z < -0.1) and z_min > 0.05
# Group them by X, Y, Z locations
overhang_groups = {
    'Left Pin (X < -3.70)': [],
    'Right Pin (X > 3.70)': [],
    'Hub / Central Web (X in [-3.70, 3.70])': [],
    'Plunger Arm (Y < -1.00)': [],
    'Cam Tab (Y > 3.20)': []
}

for i, face in enumerate(f):
    z_min = np.min(v[face, 2])
    n_z = normals[i, 2]
    if z_min > 0.05 and n_z < -0.1:
        # Check angle to horizontal
        if -n_z > np.cos(np.radians(45)): # slope < 45 deg to horizontal
            centroid = np.mean(v[face], axis=0)
            area = shaft_print.area_faces[i]
            
            if centroid[0] < -3.70:
                overhang_groups['Left Pin (X < -3.70)'].append((centroid, area, z_min))
            elif centroid[0] > 3.70:
                overhang_groups['Right Pin (X > 3.70)'].append((centroid, area, z_min))
            elif centroid[1] < -1.00:
                overhang_groups['Plunger Arm (Y < -1.00)'].append((centroid, area, z_min))
            elif centroid[1] > 3.20:
                overhang_groups['Cam Tab (Y > 3.20)'].append((centroid, area, z_min))
            else:
                overhang_groups['Hub / Central Web (X in [-3.70, 3.70])'].append((centroid, area, z_min))

for group_name, items in overhang_groups.items():
    if len(items) > 0:
        total_area = sum(item[1] for item in items)
        z_range = [min(item[2] for item in items), max(item[2] for item in items)]
        x_range = [min(item[0][0] for item in items), max(item[0][0] for item in items)]
        y_range = [min(item[0][1] for item in items), max(item[0][1] for item in items)]
        print(f"Group: {group_name}")
        print(f"  Count: {len(items)} faces, Total Area: {total_area:.2f} mm^2")
        print(f"  X span: [{x_range[0]:.2f}, {x_range[1]:.2f}]")
        print(f"  Y span: [{y_range[0]:.2f}, {y_range[1]:.2f}]")
        print(f"  Z span: [{z_range[0]:.2f}, {z_range[1]:.2f}]")
        print()
    else:
        print(f"Group: {group_name} -> NO OVERHANGS!")
