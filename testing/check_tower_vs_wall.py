import sys
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import box, Polygon, Point
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Right Tower in build_part.py:
# X in [13.10, 14.60]
# Base Y in [6.25, 12.85]
# Top Y in [6.55, 12.18]
# Retention beads: X in [14.60, 15.30], Y in [7.10, 8.00] and [10.60, 11.55]

points_to_test = [
    ("Tower Top Rear-Outer", (14.60, 12.18)),
    ("Tower Top Rear-Inner", (13.10, 12.18)),
    ("Tower Base Rear-Outer", (14.60, 12.85)),
    ("Tower Base Rear-Inner", (13.10, 12.85)),
    ("Rear Bead Outer-Top", (15.30, 11.55)),
    ("Rear Bead Outer-Bot", (15.30, 10.60)),
    ("Front Bead Outer-Top", (15.30, 8.00)),
    ("Front Bead Outer-Bot", (15.30, 7.10)),
]

print(f"{'Feature':<25} | {'Coord (X, Y)':<15} | {'Inside Ext?':<12} | {'Inside Int?':<12} | {'Dist to Ext':<12} | {'Dist to Int'}")
print("-" * 95)
for name, (x, y) in points_to_test:
    p = Point(x, y)
    in_ext = outer_body_poly.contains(p)
    in_int = inner_poly.contains(p)
    d_ext = outer_body_poly.exterior.distance(p) * (-1 if in_ext else 1)
    d_int = inner_poly.exterior.distance(p) * (-1 if in_int else 1)
    print(f"{name:<25} | ({x:5.2f}, {y:5.2f})    | {str(in_ext):<12} | {str(in_int):<12} | {d_ext:8.3f} mm  | {d_int:8.3f} mm")
