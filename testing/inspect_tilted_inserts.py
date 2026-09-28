import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# 1. Assembled inserts
ins_r = bp.build_slit_insert_mesh(is_right=True)
ins_l = bp.build_slit_insert_mesh(is_right=False)

cx_left = -7.853
cx_right = 8.453
cy = -13.589
z_insert = -bp.SLIT_BOSS_HEIGHT  # -2.47 mm

ins_r_placed = ins_r.copy().apply_translation([cx_right, cy, z_insert])
ins_l_placed = ins_l.copy().apply_translation([cx_left, cy, z_insert])

part_flat, base_poly = bp.build_exact_3d_model()
part_with_inserts = trimesh.util.concatenate([part_flat, ins_r_placed, ins_l_placed])

# Rotate 45 deg about X
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
part_tilted = part_with_inserts.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]
part_tilted.apply_translation([0, 0, -z_min])

print(f"Overall tilted part bounds (Z >= 0):\n  X: {part_tilted.bounds[0, 0]:.2f} to {part_tilted.bounds[1, 0]:.2f}\n  Y: {part_tilted.bounds[0, 1]:.2f} to {part_tilted.bounds[1, 1]:.2f}\n  Z: {part_tilted.bounds[0, 2]:.2f} to {part_tilted.bounds[1, 2]:.2f}")

# Check where the inserts alone end up in tilted space:
ins_r_tilted = ins_r_placed.copy().apply_transform(R)
ins_r_tilted.apply_translation([0, 0, -z_min])
ins_l_tilted = ins_l_placed.copy().apply_transform(R)
ins_l_tilted.apply_translation([0, 0, -z_min])

print(f"Insert R tilted bounds:\n  X: {ins_r_tilted.bounds[0, 0]:.2f} to {ins_r_tilted.bounds[1, 0]:.2f}\n  Y: {ins_r_tilted.bounds[0, 1]:.2f} to {ins_r_tilted.bounds[1, 1]:.2f}\n  Z: {ins_r_tilted.bounds[0, 2]:.2f} to {ins_r_tilted.bounds[1, 2]:.2f}")
print(f"Insert L tilted bounds:\n  X: {ins_l_tilted.bounds[0, 0]:.2f} to {ins_l_tilted.bounds[1, 0]:.2f}\n  Y: {ins_l_tilted.bounds[0, 1]:.2f} to {ins_l_tilted.bounds[1, 1]:.2f}\n  Z: {ins_l_tilted.bounds[0, 2]:.2f} to {ins_l_tilted.bounds[1, 2]:.2f}")

# Check lowest point on the entire tilted model:
v = part_tilted.vertices
lowest_idx = np.argmin(v[:, 2])
print(f"Lowest point on tilted model: {v[lowest_idx]}")

# Also compare when monolithic bosses are used vs inserts:
# What is the difference between monolithic bosses (without sockets) and merging the inserts?
