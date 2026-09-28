import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model

part_flat, _ = build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
part_tilted = part_flat.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]
part_tilted.apply_translation([0, 0, -z_min])

print("Part bounds:", part_tilted.bounds)

# Find part exterior at Y = -2.0, 0.0, 2.0
v = part_tilted.vertices
for y_target in [-4.0, -2.0, 0.0, 2.0, 4.0]:
    v_near_y = v[np.abs(v[:, 1] - y_target) < 1.0]
    if len(v_near_y) > 0:
        print(f"Near Y={y_target:4.1f}: min X={v_near_y[:, 0].min():.2f}, max X={v_near_y[:, 0].max():.2f}, Z range: [{v_near_y[:, 2].min():.2f}, {v_near_y[:, 2].max():.2f}]")
