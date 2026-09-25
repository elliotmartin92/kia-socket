import sys
sys.path.insert(0, '.')
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box, LineString
import build_part
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Proposed Right Clamp 2D Footprint:
# 1. Main Saddle on Tower: X in [13.20, 14.60], Y in [5.75, 12.75]
saddle_2d = box(13.20, 5.75, 14.60, 12.75)

# 2. Compact Outer Cheek: X in [14.60, 15.05], Y in [7.10, 11.00]
cheek_2d = box(14.60, 7.10, 15.05, 11.00)

# 3. Tie Bar: X in [5.30, 13.20], Y in [11.80, 12.75]
tie_2d = box(5.30, 11.80, 13.20, 12.75)

# Left Clamp: X in [1.60, 5.30], Y in [5.75, 12.75]
left_2d = box(1.60, 5.75, 5.30, 12.75)

proposed_clamp_2d = saddle_2d.union(cheek_2d).union(tie_2d).union(left_2d)

# Let's test the minimum clearance from proposed_clamp_2d to outer_body_poly
pts = list(proposed_clamp_2d.exterior.coords)
print("Testing proposed clamp footprint boundary points:")
print(f"{'Point (X, Y)':<20} | {'Inside Ext?':<12} | {'Dist to Ext Wall':<18} | {'Inside Int?':<12} | {'Dist to Int Wall'}")
print("-" * 85)

min_d_ext = 999.0
for pt in pts:
    p = Point(pt[0], pt[1])
    in_ext = outer_body_poly.contains(p)
    d_ext = outer_body_poly.exterior.distance(p)
    in_int = inner_poly.contains(p)
    d_int = inner_poly.exterior.distance(p)
    if in_ext:
        min_d_ext = min(min_d_ext, d_ext)
    else:
        min_d_ext = -d_ext
    print(f"({pt[0]:5.2f}, {pt[1]:5.2f})          | {str(in_ext):<12} | {d_ext:8.3f} mm {'(INSIDE)' if in_ext else '(OUTSIDE!)':<10} | {str(in_int):<12} | {d_int:8.3f} mm")

print(f"\nMinimum margin to outer wall exterior: {min_d_ext:.3f} mm")
assert min_d_ext > 0.40, f"Margin {min_d_ext} mm is too small!"
print("SUCCESS: Proposed clamp footprint is 100% inside outer wall with ample margin!")
