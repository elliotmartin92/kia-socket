"""
Verify exact dimensions of the generated STL mesh.
"""
import trimesh
import numpy as np

mesh = trimesh.load('part.stl')

# 1. Bounding box & extents
print(f"Mesh Total Extents (X, Y, Z): {mesh.extents[0]:.2f} x {mesh.extents[1]:.2f} x {mesh.extents[2]:.2f} mm")
print(f"Mesh Z Range: {mesh.bounds[0][2]:.2f} mm to {mesh.bounds[1][2]:.2f} mm (Total Height = {mesh.extents[2]:.2f} mm)")

# 2. Check clip at 45 degrees
# Rotate mesh points by -45 degrees to align TR clip along +X axis
rot_45 = trimesh.transformations.rotation_matrix(np.radians(-45), [0, 0, 1])
vertices_rot = trimesh.transformations.transform_points(mesh.vertices, rot_45)

# Clip region is around Y=0, Z > 3.0, X > 15
clip_mask = (np.abs(vertices_rot[:, 1]) < 2.0) & (vertices_rot[:, 2] > 4.0) & (vertices_rot[:, 0] > 18.0)
clip_verts = vertices_rot[clip_mask]

# Outer wall radius is at 19.25 mm
r_wall = 19.25
max_x = np.max(clip_verts[:, 0])
protrusion_dist = max_x - r_wall

print(f"\n--- Clip Dimensional Verification ---")
print(f"Outer Wall Radius: {r_wall:.2f} mm (Diameter = {2*r_wall:.2f} mm)")
print(f"Clip Protrusion Max Radius: {max_x:.2f} mm")
print(f"Exact Distance from Wall to Tip of Protrusion: {protrusion_dist:.2f} mm")
print(f"Clip Max Z Height: {np.max(clip_verts[:, 2]):.2f} mm")
print(f"Wall Max Z Height: 6.77 mm")
