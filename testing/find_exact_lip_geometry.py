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

print("=== FINDING EXACT RIGHT LIP & SOCKET GEOMETRY ===")
# Slit box (1.20 x 3.40) in relative coords
slit_box = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
# In plate coords:
slit_in_plate = translate(slit_box, xoff=cx, yoff=cy)

# Let's inspect inner_wall boundary points near the bottom right:
# In relative coordinates:
pts_rel = []
for pt in inner_wall.exterior.coords:
    rx, ry = pt[0] - cx, pt[1] - cy
    if -1.0 <= rx <= 2.5 and -3.0 <= ry <= 0.0:
        pts_rel.append((rx, ry))

print(f"Inner wall points near bottom-right of key:")
for rx, ry in pts_rel:
    print(f"   rel: ({rx:+.3f}, {ry:+.3f}) -> plate: ({rx+cx:.3f}, {ry+cy:.3f})")

