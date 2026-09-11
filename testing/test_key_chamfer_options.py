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

slit_box = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
blade_box = box(-0.77/2, -3.10/2, 0.77/2, 3.10/2)

# Floor socket detent_right in relative coords:
# With 0.75mm chamfer:
x_r_max = SOCKET_W_X/2
y_r_bot = -SOCKET_LEN_Y/2
chamfer_sock = Polygon([[x_r_max - 0.75, y_r_bot - 0.05],
                        [x_r_max + 0.05, y_r_bot + 0.75],
                        [x_r_max + 0.05, y_r_bot - 0.05]])
sock_rel = box(-SOCKET_W_X/2, -SOCKET_LEN_Y/2, SOCKET_W_X/2, SOCKET_LEN_Y/2).difference(chamfer_sock)

# What if chamfer on key is varied:
print("=== TESTING VARIOUS KEY CHAMFER SIZES ===")
# In relative coords:
# corner is at (1.30, -2.40)
# Chamfer cut with size d_chamfer:
# p1 = (1.30 - d_chamfer, -2.40)
# p2 = (1.30, -2.40 + d_chamfer)
for d in [0.60, 0.75, 0.85, 1.00, 1.10, 1.20, 1.30]:
    p1 = [1.30 - d, -2.40]
    p2 = [1.30, -2.40 + d]
    tri = Polygon([[p1[0], p1[1] - 0.02],
                   [p2[0] + 0.02, p2[1]],
                   [p2[0] + 0.02, p1[1] - 0.02]])
    key = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2).difference(tri)
    
    # Distance to slit
    d_slit = key.boundary.distance(slit_box)
    # Does key fit in sock_rel?
    fits_in_socket = sock_rel.contains(key)
    # Distance from key to sock_rel boundary
    d_to_sock = sock_rel.boundary.distance(key)
    
    # Key in plate:
    key_in_plate = translate(key, xoff=cx, yoff=cy)
    # Overlap with wall_poly
    overlap_wall = key_in_plate.intersection(wall_poly).area
    
    print(f"Chamfer {d:.2f}mm: fits_in_nominal_sock={fits_in_socket} (clr={d_to_sock:.3f}mm), "
          f"min_wall_to_slit={d_slit:.3f}mm, wall_overlap={overlap_wall:.4f}mm^2")

