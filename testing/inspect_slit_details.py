import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

# In flat coordinates: where is the slit insert, where is its through-hole, and where is the shroud?
# In build_part.py:
# cx_left, cx_right = -7.853, 8.453
# Let's inspect create_backside_slit_bosses_poly
poly = build_part.create_backside_slit_bosses_poly()
print(f"Backside slit bosses poly bounds: {poly.bounds}")

# Check where the actual slit hole through the floor is
# In ARCHITECTURE.md or build_part.py:
# SLIT_W_X = 1.10, SLIT_LEN_Y = 3.00
# Let's find slit hole in base_poly
ret = build_part.get_exact_base_polygon()
if isinstance(ret, tuple):
    base_poly = ret[0]
else:
    base_poly = ret
print(f"Base poly interiors (holes count): {len(base_poly.interiors)}")
for i, hole in enumerate(base_poly.interiors):
    print(f"  Hole {i} bounds: {hole.bounds}")
