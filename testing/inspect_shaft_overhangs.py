"""
testing/inspect_shaft_overhangs.py
Inspect the printable shaft rocker mesh orientation, overhang angles, contact area at Z=0,
and identify all unsupported overhangs.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

shaft_print = build_shaft_rocker_mesh(in_assembly_coords=False)

print("=" * 60)
print("SHAFT ROCKER PRINTABLE MESH ANALYSIS")
print("=" * 60)
bounds = shaft_print.bounds
print(f"Mesh bounds:")
print(f"  X: [{bounds[0, 0]:.2f}, {bounds[1, 0]:.2f}] (span: {bounds[1, 0] - bounds[0, 0]:.2f} mm)")
print(f"  Y: [{bounds[0, 1]:.2f}, {bounds[1, 1]:.2f}] (span: {bounds[1, 1] - bounds[0, 1]:.2f} mm)")
print(f"  Z: [{bounds[0, 2]:.2f}, {bounds[1, 2]:.2f}] (span: {bounds[1, 2] - bounds[0, 2]:.2f} mm)")
print(f"Watertight: {shaft_print.is_watertight}")
print(f"Volume: {shaft_print.volume:.2f} mm^3")

# Find faces at Z close to 0 (bed contact)
v = shaft_print.vertices
f = shaft_print.faces
normals = shaft_print.face_normals

# Bed contact faces: normal pointing -Z (normal[2] < -0.9) and vertices near Z=0
bed_faces = []
bed_area = 0.0
for i, face in enumerate(f):
    z_coords = v[face, 2]
    if np.all(z_coords < 0.05) and normals[i, 2] < -0.8:
        bed_faces.append(i)
        bed_area += shaft_print.area_faces[i]

print(f"\nBed contact area (Z <= 0.05mm, normal -Z): {bed_area:.2f} mm^2")

# Check overhang angles
# Standard 3D printing overhang angle is measured from vertical:
# Face normal angle to -Z: theta = arccos(-normal[2])
# Overhang if normal[2] < 0 and face is facing downward:
# If normal[2] is between -1.0 and 0.0:
# Critical overhang is when slope angle with horizontal < 45 degrees, i.e. normal[2] < -cos(45) = -0.707.
# Downward facing faces (normal[2] < -0.1) that are above Z=0.2mm:
overhang_faces = []
overhang_area = 0.0
steep_overhang_faces = [] # steeper than 45 deg from vertical (i.e. angle to horizontal < 45 deg, normal[2] < -0.707)

for i, face in enumerate(f):
    z_min = np.min(v[face, 2])
    n_z = normals[i, 2]
    if z_min > 0.10 and n_z < -0.1: # Downward facing above bed
        # Angle with -Z axis:
        # normal dot [0, 0, -1] = -n_z
        # If normal is [0, 0, -1], angle is 0 (completely horizontal flat ceiling overhang)
        cos_down = -n_z
        if cos_down > np.cos(np.radians(45)): # angle < 45 deg to horizontal
            steep_overhang_faces.append(i)
            overhang_area += shaft_print.area_faces[i]

print(f"Overhang area requiring support (above Z=0.10mm, angle < 45 deg to horizontal): {overhang_area:.2f} mm^2")

# Let's inspect where these overhangs are located in X, Y, Z
if len(steep_overhang_faces) > 0:
    overhang_v_indices = np.unique(f[steep_overhang_faces])
    ov_v = v[overhang_v_indices]
    print(f"Overhang regions bounds:")
    print(f"  X: [{np.min(ov_v[:, 0]):.2f}, {np.max(ov_v[:, 0]):.2f}]")
    print(f"  Y: [{np.min(ov_v[:, 1]):.2f}, {np.max(ov_v[:, 1]):.2f}]")
    print(f"  Z: [{np.min(ov_v[:, 2]):.2f}, {np.max(ov_v[:, 2]):.2f}]")

# Let's cluster or analyze parts: Axle pins, Hub, Ribs, Plunger, Cam
