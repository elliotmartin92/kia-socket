"""
testing/inspect_higher_overhangs.py
Analyze overhangs across all Z levels of shaft_rocker_clean.stl to find where
overhangs or cantilevers exist higher up on the lever.
"""

import trimesh
import numpy as np

mesh = trimesh.load('shaft_rocker_clean.stl')

print(f"Total vertices: {len(mesh.vertices)}, faces: {len(mesh.faces)}")
print(f"Bounds: X: [{mesh.bounds[0,0]:.2f}, {mesh.bounds[1,0]:.2f}]")
print(f"        Y: [{mesh.bounds[0,1]:.2f}, {mesh.bounds[1,1]:.2f}]")
print(f"        Z: [{mesh.bounds[0,2]:.2f}, {mesh.bounds[1,2]:.2f}]")

# Face normals and centers
normals = mesh.face_normals
centers = mesh.triangles_center
areas = mesh.area_faces

# An overhang relative to build plate (normal pointing downwards):
# Normal pointing straight down is [0, 0, -1], dot product with [0, 0, 1] is negative.
# Overhang angle from vertical (Z up):
# cosine of angle with Z-down [0, 0, -1] is -normal_z.
# If normal_z < -sin(deg2rad(45)) = -0.707, that's an overhang steeper than 45°.
# If normal_z < -0.05, that's any downward-sloping face.
# Let's inspect different bins of Z:

print("\n--- Downward facing facets by Z level ---")
z_bins = np.arange(0, 21, 2)
for i in range(len(z_bins)-1):
    z_lo, z_hi = z_bins[i], z_bins[i+1]
    mask_z = (centers[:, 2] >= z_lo) & (centers[:, 2] < z_hi)
    
    # Overhang steeper than 45°: normal_z < -0.707
    mask_oh45 = mask_z & (normals[:, 2] < -0.707)
    # Overhang between 30° and 45° from horizontal: normal_z between -0.707 and -0.5
    mask_oh30 = mask_z & (normals[:, 2] < -0.5) & (normals[:, 2] >= -0.707)
    # Horizontal downward: normal_z < -0.95
    mask_horiz_down = mask_z & (normals[:, 2] < -0.95)
    
    area_oh45 = np.sum(areas[mask_oh45])
    area_oh30 = np.sum(areas[mask_oh30])
    area_horiz = np.sum(areas[mask_horiz_down])
    
    if np.any(mask_oh45) or np.any(mask_oh30):
        print(f"Z [{z_lo:2d}, {z_hi:2d}] mm: Area oh>45° = {area_oh45:6.2f} mm², Area oh>30° = {area_oh30:6.2f} mm², Flat down (< -0.95) = {area_horiz:6.2f} mm²")
        # Print bounding box of oh45 faces
        if np.any(mask_oh45):
            c_oh = centers[mask_oh45]
            print(f"    oh>45° X: [{c_oh[:,0].min():.2f}, {c_oh[:,0].max():.2f}], Y: [{c_oh[:,1].min():.2f}, {c_oh[:,1].max():.2f}], Z: [{c_oh[:,2].min():.2f}, {c_oh[:,2].max():.2f}]")

print("\n--- Detailed search for downward facing faces with Z > 2.0 mm ---")
mask_high_down = (centers[:, 2] > 2.0) & (normals[:, 2] < -0.1)
if np.any(mask_high_down):
    print(f"Found {np.sum(mask_high_down)} downward faces above Z=2.0 mm, total area: {np.sum(areas[mask_high_down]):.2f} mm²")
    for nz_thresh in [-0.1, -0.3, -0.5, -0.707, -0.9]:
        m = (centers[:, 2] > 2.0) & (normals[:, 2] < nz_thresh)
        print(f"  normal_z < {nz_thresh:5.2f}: {np.sum(m)} faces, area = {np.sum(areas[m]):.2f} mm²")
else:
    print("No downward facing faces found above Z=2.0 mm!")
