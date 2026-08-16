"""
Analyze user measurements:
1) X: Left tower in line with top right corner of bracket 3 (X = 4.705mm)
2) Y: 22.68mm from bottom wall (interior)
"""
from shapely.geometry import box, LineString, Point
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_THICK, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

print(f"Bracket 3 X bounds: [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}], Y bounds: [{b3.bounds[1]:.3f}, {b3.bounds[3]:.3f}]")
print(f"Bracket 3 top-right corner: X = {b3.bounds[2]:.3f} mm, Y = {b3.bounds[3]:.3f} mm")

# Bottom wall Y coordinates:
# Flat bottom tab
y_bot_outer = base_poly.bounds[1]  # -18.718mm
y_bot_inner = inner_wall_poly.bounds[1]  # -17.518mm

print(f"Bottom outer wall Y: {y_bot_outer:.3f} mm")
print(f"Bottom inner wall Y: {y_bot_inner:.3f} mm")

# Measurement: 22.68mm from bottom wall (interior)
# Let's check:
# If 22.68mm is to the bottom face of the tower:
y_tower_bot_1 = y_bot_inner + 22.68
y_tower_top_1 = y_tower_bot_1 + TOWER_Y_LEN
y_tower_mid_1 = (y_tower_bot_1 + y_tower_top_1) / 2.0

# If 22.68mm is to the top face of the tower:
y_tower_top_2 = y_bot_inner + 22.68
y_tower_bot_2 = y_tower_top_2 - TOWER_Y_LEN
y_tower_mid_2 = (y_tower_bot_2 + y_tower_top_2) / 2.0

# If 22.68mm is to the center / cradle of the tower:
y_tower_mid_3 = y_bot_inner + 22.68
y_tower_top_3 = y_tower_mid_3 + TOWER_Y_LEN / 2.0
y_tower_bot_3 = y_tower_mid_3 - TOWER_Y_LEN / 2.0

print(f"\nCase 1 (22.68mm to Tower Bottom): Y in [{y_tower_bot_1:.3f}, {y_tower_top_1:.3f}], center={y_tower_mid_1:.3f}")
print(f"Case 2 (22.68mm to Tower Top):    Y in [{y_tower_bot_2:.3f}, {y_tower_top_2:.3f}], center={y_tower_mid_2:.3f}")
print(f"Case 3 (22.68mm to Tower Center): Y in [{y_tower_bot_3:.3f}, {y_tower_top_3:.3f}], center={y_tower_mid_3:.3f}")

# Left tower aligned with top-right corner of Bracket 3:
# Top right corner of B3 is X = 4.705mm.
# If Left tower right face aligns with B3 right wall (X = 4.705):
x_left_outer = 4.705 - TOWER_WALL_THICK  # 3.705
x_left_inner = 4.705
# If Left tower is centered on B3 right wall (X = 4.705):
x_left_mid = 4.705

print(f"\nTop-right hole bounds: X in [{hole_x - hole_w/2:.3f}, {hole_x + hole_w/2:.3f}], Y in [{hole_y - hole_h/2:.3f}, {hole_y + hole_h/2:.3f}]")
