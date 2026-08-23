import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np

mesh = trimesh.load('part.stl')
print(f"Total Vertices: {len(mesh.vertices)}, Total Faces: {len(mesh.faces)}")
print(f"Is watertight: {mesh.is_watertight}")

# 1. Right Ear: X > 19.5, Z in [0, 6.77]
right_mask = (mesh.vertices[:, 0] > 19.5)
right_verts = mesh.vertices[right_mask]
print(f"\n--- Right Ear Mesh Check ---")
print(f"Vertices found: {len(right_verts)}")
print(f"X range: [{np.min(right_verts[:, 0]):.3f}, {np.max(right_verts[:, 0]):.3f}] mm")
print(f"Y range: [{np.min(right_verts[:, 1]):.3f}, {np.max(right_verts[:, 1]):.3f}] mm")
print(f"Ear width in Y: {np.max(right_verts[:, 1]) - np.min(right_verts[:, 1]):.3f} mm")
print(f"Fits in 8.30mm gap: {np.max(right_verts[:, 1]) - np.min(right_verts[:, 1]) <= 8.30}")

# 2. Left Ear: X < -20.5, Z in [0, 6.77]
left_mask = (mesh.vertices[:, 0] < -20.5)
left_verts = mesh.vertices[left_mask]
print(f"\n--- Left Ear Mesh Check ---")
print(f"Vertices found: {len(left_verts)}")
print(f"X range: [{np.min(left_verts[:, 0]):.3f}, {np.max(left_verts[:, 0]):.3f}] mm")
print(f"Y range: [{np.min(left_verts[:, 1]):.3f}, {np.max(left_verts[:, 1]):.3f}] mm")
print(f"Ear width in Y: {np.max(left_verts[:, 1]) - np.min(left_verts[:, 1]):.3f} mm")
print(f"Fits in 8.30mm gap: {np.max(left_verts[:, 1]) - np.min(left_verts[:, 1]) <= 8.30}")
