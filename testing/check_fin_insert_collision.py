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

# What happens with current build_45deg_supported_part_mesh?
combined, m_tilted, all_fins = bp.build_45deg_supported_part_mesh(part_with_inserts)

# Check intersection between tilted inserts and all_fins
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
z_min = m_tilted.bounds[0, 2]

# Let's inspect collision between each fin and each insert:
# Main fins are at X = -8.0 and X = +8.0.
# The insert is at X in [-9.5, -6.2] and [6.8, 10.1].
print("Checking overlap between fins and inserts...")
try:
    inter = all_fins.intersection(m_tilted, engine='manifold')
    print("Intersection volume between fins and tilted part (including inserts):", inter.volume)
except Exception as e:
    print("Intersection error:", e)
