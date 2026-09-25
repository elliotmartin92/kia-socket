import sys
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
import build_part
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Let's test a robust contoured cheek for the Right Clamp:
# Right Tower outer face: X = 14.60mm
# Front of cheek: Y = 7.10mm
# Retention bead: Y in [7.10, 8.00], bead sticks out to X = 15.30mm (protrusion = 0.70mm)
# Axle pin: at Y = 9.28mm, tip ends at X = 15.00mm
#
# If cheek outer face is at X = 16.10mm from Y = 7.10mm to Y = 9.80mm:
# Cheek thickness = 16.10 - 14.60 = 1.50mm! (Extremely rigid, 3-4 perimeters)
# Then from Y = 9.80mm, it angles / curves inward to meet X = 14.60mm at Y = 11.20mm:
# (16.10, 9.80) -> (14.60, 11.20)
#
# Let's check the distance to the outer wall exterior for this polygon:
cheek_profile_xy = [
    (14.60, 7.10),
    (16.10, 7.10),
    (16.10, 9.80),
    (15.50, 10.70),
    (14.60, 11.20),
    (14.60, 12.65),
    (13.20, 12.65),
    (13.20, 5.07),
    (14.60, 5.07),
]
poly_clamp = Polygon(cheek_profile_xy)

print(f"{'Point (X, Y)':<18} | {'Inside Wall?':<14} | {'Margin to Outer Wall Exterior'}")
print("-" * 65)
min_margin = 999.0
for pt in cheek_profile_xy:
    p = Point(pt[0], pt[1])
    in_ext = outer_body_poly.contains(p)
    d = outer_body_poly.exterior.distance(p)
    if in_ext:
        min_margin = min(min_margin, d)
    else:
        min_margin = -d
    print(f"({pt[0]:5.2f}, {pt[1]:5.2f})       | {str(in_ext):<14} | {d:6.3f} mm {'(INSIDE)' if in_ext else '(OUTSIDE!)'}")

print(f"\nMinimum margin to outer wall exterior: {min_margin:.3f} mm")
print(f"Cheek thickness at bead & pin: {16.10 - 14.60:.2f} mm (1.50mm thick solid beam!)")
