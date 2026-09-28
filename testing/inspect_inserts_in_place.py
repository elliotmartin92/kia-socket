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

print("Part flat bounds:", part_flat.bounds)
print("Insert R bounds:", ins_r_placed.bounds)
print("Insert L bounds:", ins_l_placed.bounds)

# Check union of part_flat with placed inserts
try:
    merged = part_flat.union(trimesh.util.concatenate([ins_r_placed, ins_l_placed]), engine='manifold')
    print("Merged watertight:", merged.is_watertight)
    print("Merged bounds:", merged.bounds)
except Exception as e:
    print("Union failed:", e)

# What if we just concatenate them?
concat = trimesh.util.concatenate([part_flat, ins_r_placed, ins_l_placed])
print("Concat watertight bodies:", len([b for b in concat.split(only_watertight=False) if b.is_watertight]))

# Now let's check what the OEM / monolithic bosses were:
bosses_poly = bp.create_backside_slit_bosses_poly()
print("Bosses poly bounds:", bosses_poly.bounds)
