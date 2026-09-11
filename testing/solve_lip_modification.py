import os, sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, INSERT_KEY_HEIGHT,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_CLEARANCE,
    SLIT_W_X, SLIT_LEN_Y
)

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_wall = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_poly = outer_body_poly.difference(inner_wall)

cx = 8.453
cy = -13.589

# In baseplate coordinates:
# The socket cutout in base_poly is detent_right.
# But the solid wall is wall_poly.
# So the physical socket hole in part.stl is:
x_r_max = cx + SOCKET_W_X/2
y_r_bot = cy - SOCKET_LEN_Y/2
chamfer_right_tri = Polygon([[x_r_max - 0.75, y_r_bot - 0.05],
                             [x_r_max + 0.05, y_r_bot + 0.75],
                             [x_r_max + 0.05, y_r_bot - 0.05]])
detent_right = box(cx - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_right_tri)

actual_socket = detent_right.difference(wall_poly)
actual_socket_rel = translate(actual_socket, xoff=-cx, yoff=-cy)

print("=== ACTUAL PHYSICAL SOCKET IN PART.STL ===")
print("Actual socket bounds (rel):", actual_socket_rel.bounds)
print("Actual socket area:", actual_socket_rel.area)

# Now, what does the lip (key) need to be to fit inside actual_socket?
# If the lip is the raw key box: [-1.30, 1.30] x [-2.40, 2.40]
key_raw = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2)

# What part of key_raw is outside actual_socket_rel?
key_colliding = key_raw.difference(actual_socket_rel)
print("Colliding key area outside actual socket:", key_colliding.area)
print("Colliding key bounds (rel):", key_colliding.bounds)

# To give clearance inside actual_socket, the key should fit inside:
# safe_zone = actual_socket_rel.buffer(-0.15) or similar.
# Let's inspect the boundary of actual_socket_rel where it cuts off the key:
print("\nBoundary points of actual_socket_rel at the bottom-right corner:")
for pt in actual_socket_rel.exterior.coords:
    if pt[0] > 0.1 and pt[1] < -1.0:
        print(f"   ({pt[0]:.3f}, {pt[1]:.3f})")

