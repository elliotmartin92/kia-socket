"""
Find the exact closest point on the interior wall above the left tower and solve for Y position.
"""
from shapely.geometry import Point, LineString, Polygon, box
import numpy as np

from build_part import (
    get_exact_base_polygon, bracket_3_raw_pts, to_mm_poly,
    OUTER_WALL_THICK, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

b3 = to_mm_poly(bracket_3_raw_pts)
b3_center_x = (b3.bounds[0] + b3.bounds[2]) / 2.0  # 3.236mm

x_left_min = b3_center_x - TOWER_WALL_THICK / 2.0
x_left_max = b3_center_x + TOWER_WALL_THICK / 2.0

print(f"Left tower X span: [{x_left_min:.3f}, {x_left_max:.3f}], center={b3_center_x:.3f}")

# Ray straight up from tower center
ray = LineString([(b3_center_x, 0), (b3_center_x, 30)])
inter = inner_wall_poly.exterior.intersection(ray)
y_inner_straight_up = inter.y if hasattr(inter, 'y') else max(p.y for p in inter.geoms)

print(f"Inner wall Y directly straight up above X={b3_center_x:.3f}: {y_inner_straight_up:.3f} mm")

# If distance directly straight up to interior wall is 6.77mm:
# y_tower_top = y_inner_straight_up - 6.77
y_top_straight = y_inner_straight_up - 6.77
print(f"Option 1 (Straight Up Y distance from inner wall = 6.77mm):")
print(f"  Tower Top Y: {y_top_straight:.3f} mm")
print(f"  Tower Bottom Y: {y_top_straight - TOWER_Y_LEN:.3f} mm")
print(f"  Tower Mid Y: {y_top_straight - TOWER_Y_LEN/2:.3f} mm")

# Check closest point on interior wall boundary to the tower's top edge
# Let's test a range of y_top values to find exact minimum distance = 6.77mm
for y_top_test in np.arange(10.0, 13.5, 0.01):
    tower_top_segment = LineString([(x_left_min, y_top_test), (x_left_max, y_top_test)])
    dist = inner_wall_poly.exterior.distance(tower_top_segment)
    if abs(dist - 6.77) < 0.01:
        print(f"Option 2 (Euclidean minimum distance from tower top edge to inner wall = 6.77mm):")
        print(f"  Tower Top Y: {y_top_test:.3f} mm")
        print(f"  Tower Bottom Y: {y_top_test - TOWER_Y_LEN:.3f} mm")
        print(f"  Tower Mid Y: {y_top_test - TOWER_Y_LEN/2:.3f} mm")
        break
