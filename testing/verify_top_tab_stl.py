import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np

mesh = trimesh.load('part.stl')
print(f"Total Vertices: {len(mesh.vertices)}, Total Faces: {len(mesh.faces)}")

# Top Tab: Y > 19.5, Z in [0, 6.77]
top_mask = (mesh.vertices[:, 1] > 19.5)
top_verts = mesh.vertices[top_mask]
print(f"\n--- Top Tab Mesh Check ---")
print(f"Vertices found: {len(top_verts)}")
print(f"X range: [{np.min(top_verts[:, 0]):.3f}, {np.max(top_verts[:, 0]):.3f}] mm")
print(f"Y range: [{np.min(top_verts[:, 1]):.3f}, {np.max(top_verts[:, 1]):.3f}] mm")
tab_width_x = np.max(top_verts[:, 0]) - np.min(top_verts[:, 0])
tab_center_x = (np.max(top_verts[:, 0]) + np.min(top_verts[:, 0])) / 2.0
print(f"Top Tab Width in X: {tab_width_x:.3f} mm")
print(f"Top Tab Center X: {tab_center_x:.3f} mm")
print(f"Fits in 8.33mm gap: {tab_width_x <= 8.33 and abs(np.min(top_verts[:, 0])) <= 8.33/2 and abs(np.max(top_verts[:, 0])) <= 8.33/2}")
