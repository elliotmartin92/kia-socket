import os, sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, INSERT_KEY_HEIGHT,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_CLEARANCE,
    INSERT_BODY_W_X, INSERT_BODY_LEN_Y,
    SLIT_W_X, SLIT_LEN_Y
)

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_wall = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_poly = outer_body_poly.difference(inner_wall)

cx = 8.453
cy = -13.589

print("=== DETAILED ANALYSIS: LIP FIT INTO ASSEMBLY FLOOR ===")
# 1. Available floor space at (cx, cy) inside inner_wall:
# Let's inspect the actual socket in the floor
# Raw socket box is 2.90 x 5.10
sock_raw = box(cx - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)

# Inside inner_wall:
sock_clean = sock_raw.intersection(inner_wall)
print(f"Clean socket area inside inner_wall: {sock_clean.area:.4f} mm^2")

# What is the boundary of sock_clean in relative coordinates?
sock_clean_rel = translate(sock_clean, xoff=-cx, yoff=-cy)
print(f"Clean socket relative bounds: {sock_clean_rel.bounds}")

# Let's see: if the key is inside sock_clean with 0.15mm clearance on all sides:
# That would be sock_clean.buffer(-0.15):
ideal_key_rel = sock_clean_rel.buffer(-0.15, join_style=2)
print(f"Ideal key relative bounds: {ideal_key_rel.bounds}")
print(f"Ideal key area: {ideal_key_rel.area:.4f} mm^2")

# Let's check slit hole in relative coords:
slit_box = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
print(f"Slit box relative bounds: {slit_box.bounds}")
print(f"Does ideal key contain slit box? {ideal_key_rel.contains(slit_box)}")
if not ideal_key_rel.contains(slit_box):
    slit_diff = slit_box.difference(ideal_key_rel)
    print(f"Slit area outside ideal key: {slit_diff.area:.4f} mm^2")
    print(f"Slit outside ideal key bounds: {slit_diff.bounds}")
else:
    print(f"Minimum wall thickness around slit: {ideal_key_rel.boundary.distance(slit_box):.3f} mm")

