import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# Load / build
part_flat, base_poly = bp.build_exact_3d_model()
ins_r = bp.build_slit_insert_mesh(is_right=True)
ins_l = bp.build_slit_insert_mesh(is_right=False)

cx_left = -7.853
cx_right = 8.453
cy = -13.589
z_insert = -bp.SLIT_BOSS_HEIGHT

ins_r_placed = ins_r.copy().apply_translation([cx_right, cy, z_insert])
ins_l_placed = ins_l.copy().apply_translation([cx_left, cy, z_insert])

part_with_inserts = trimesh.util.concatenate([part_flat, ins_r_placed, ins_l_placed])

# Let's inspect what the support fins in build_45deg_supported_part_mesh do:
combined, m_tilted, all_fins = bp.build_45deg_supported_part_mesh(part_with_inserts)

print("m_tilted bounds:", m_tilted.bounds)
print("all_fins bounds:", all_fins.bounds)

# Check interference between all_fins and m_tilted:
# In the Slant3D spec, fins have a 0.20mm standoff from the part, except for the tines.
# Let's check where the fin walls are at X = -8.0 and X = +8.0:
# The fin top was calculated as: z_top = y - z_min - standoff
# This was based on the backplate underside at Z_flat = 0.
# BUT the insert protrudes out the back to Z_flat = -2.47mm!
# For a point on the insert at Z_flat = -2.47mm:
# In tilted space:
# y_tilt = y * cos(45) - z * sin(45) = y * cos(45) - (-2.47) * sin(45) = y * cos(45) + 1.747mm!
# z_tilt_raw = y * sin(45) + z * cos(45) = y * sin(45) - 1.747mm!
# So the insert protrudes DOWNWARD toward the bed!
# Lowest Z of the insert in tilted space is Z = 0.20mm!
# While the backplate underside at that Y was at Z = 1.41mm to 7.0mm!
print("Insert protrudes downward toward the bed in tilted space!")
