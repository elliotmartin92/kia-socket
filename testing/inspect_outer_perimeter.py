import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model

part_flat, base_poly = build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
part_tilted = part_flat.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]
part_tilted.apply_translation([0, 0, -z_min])

# Check vertices near X = -19.0 and X = +19.0
v = part_tilted.vertices
left_v = v[v[:, 0] < -17.0]
right_v = v[v[:, 0] > 17.0]

print(f"Left outer (X < -17): min X={left_v[:, 0].min():.2f}, max X={left_v[:, 0].max():.2f}, Y range: [{left_v[:, 1].min():.2f}, {left_v[:, 1].max():.2f}], Z range: [{left_v[:, 2].min():.2f}, {left_v[:, 2].max():.2f}]")
print(f"Right outer (X > 17): min X={right_v[:, 0].min():.2f}, max X={right_v[:, 0].max():.2f}, Y range: [{right_v[:, 1].min():.2f}, {right_v[:, 1].max():.2f}], Z range: [{right_v[:, 2].min():.2f}, {right_v[:, 2].max():.2f}]")
