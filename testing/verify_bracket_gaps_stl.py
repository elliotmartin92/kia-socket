import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np
from build_part import bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts
from build_shaft import X_LEFT_TOWER_INNER, X_LEFT_TOWER_OUTER
from shapely.geometry import Polygon

p1 = Polygon(bracket_1_raw_pts)
p2 = Polygon(bracket_2_raw_pts)
p3 = Polygon(bracket_3_raw_pts)
p4 = Polygon(bracket_4_raw_pts)

print("--- Bracket Poly Top Region Checks (Y > 4.5mm) ---")
b3_top_pts = [pt for pt in bracket_3_raw_pts if pt[1] > 4.5]
b3_top_x_max = max(pt[0] for pt in b3_top_pts)
print(f"Bracket 3 Top Max X (Y > 4.5mm): {b3_top_x_max:.3f} mm")
print(f"Left Tower Left Wall: X = {X_LEFT_TOWER_OUTER:.3f} mm")
print(f"Clearance at Top between Bracket 3 and Left Tower: {X_LEFT_TOWER_OUTER - b3_top_x_max:.3f} mm (Zero Overlap: {b3_top_x_max < X_LEFT_TOWER_OUTER})")

print("\n--- Bracket Top Hook Gaps ---")
for name, raw in [('Bracket 1', bracket_1_raw_pts), ('Bracket 2', bracket_2_raw_pts), ('Bracket 3', bracket_3_raw_pts), ('Bracket 4', bracket_4_raw_pts)]:
    hook_bot = [pt[1] for pt in raw if abs(pt[1] - 4.800) < 0.05]
    pocket_top = [pt[1] for pt in raw if abs(pt[1] - 6.250) < 0.05]
    print(f"{name}: Hook Lower Face Y = {hook_bot[0]:.3f} mm, Pocket Top Y = {pocket_top[0]:.3f} mm (Vertical Pocket Depth = {pocket_top[0] - hook_bot[0]:.3f} mm)")

