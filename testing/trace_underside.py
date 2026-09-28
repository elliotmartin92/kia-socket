import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

part_flat, _ = bp.build_exact_3d_model()
ins_r = bp.build_slit_insert_mesh(is_right=True)
ins_l = bp.build_slit_insert_mesh(is_right=False)

cx_left = -7.853
cx_right = 8.453
cy = -13.589
z_insert = -bp.SLIT_BOSS_HEIGHT

ins_r_placed = ins_r.copy().apply_translation([cx_right, cy, z_insert])
ins_l_placed = ins_l.copy().apply_translation([cx_left, cy, z_insert])

part_with_inserts = trimesh.util.concatenate([part_flat, ins_r_placed, ins_l_placed])

# Tilt 45 deg
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
part_tilted = part_with_inserts.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]
part_tilted.apply_translation([0, 0, -z_min])

# Find lowest Z on the underside at X = -8.0 and X = +8.0 as a function of Y:
for x_target in [-8.0, 8.0]:
    print(f"\n--- Underside profile at X = {x_target:+.1f}mm ---")
    for y in np.arange(-13.0, 13.0, 1.0):
        # find vertices near x and y
        pts = part_tilted.vertices
        mask = (np.abs(pts[:, 0] - x_target) < 0.5) & (np.abs(pts[:, 1] - y) < 0.5)
        if np.any(mask):
            z_low = pts[mask, 2].min()
            print(f"Y = {y:+5.1f} | min Z = {z_low:5.2f}")
        else:
            print(f"Y = {y:+5.1f} | no points")
