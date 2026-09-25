import sys
sys.path.insert(0, '.')
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box, LineString
import build_part
from build_part import get_exact_base_polygon, OUTER_WALL_THICK
import build_clamp

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Let's see what happens if we contour the Right Clamp:
# Right Tower: X in [13.10, 14.60]
# Shaft pin: ends at X = 15.00
# Right Clamp U-Saddle: X in [13.20, 14.60]
# Right Clamp Outer Cheek: X in [14.60, 15.10] (thickness = 0.50mm, wraps pin tip)
# Rear wall of saddle: Y in [12.18, 13.00] (0.80mm thick tension wall)
# Front wall of saddle: Y in [5.75, 6.55] (0.80mm thick tension wall)

# Let's inspect the clearance of this streamlined envelope:
test_box = box(13.20, 5.75, 15.10, 13.00)
corners = [
    (13.20, 5.75), (15.10, 5.75),
    (15.10, 12.00), (15.10, 12.50), (15.10, 13.00),
    (14.60, 13.00), (13.20, 13.00)
]

print("Streamlined envelope corner checks:")
for x, y in corners:
    p = Point(x, y)
    d_ext = outer_body_poly.exterior.distance(p) * (-1 if outer_body_poly.contains(p) else 1)
    d_int = inner_poly.exterior.distance(p) * (-1 if inner_poly.contains(p) else 1)
    print(f"({x:5.2f}, {y:5.2f}) -> in_ext={outer_body_poly.contains(p)}, dist_ext={d_ext:6.2f} mm | in_int={inner_poly.contains(p)}, dist_int={d_int:6.2f} mm")
