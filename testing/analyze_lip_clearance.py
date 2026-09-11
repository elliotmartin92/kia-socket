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

print("=== OPTIMIZING RIGHT INSERT LIP & SOCKET ===")
print(f"Center in baseplate: ({cx:.3f}, {cy:.3f})")
print(f"Slit hole in insert: {SLIT_W_X:.2f} x {SLIT_LEN_Y:.2f} mm")
print(f"Key dimensions:      {INSERT_KEY_W_X:.2f} x {INSERT_KEY_LEN_Y:.2f} mm")
print(f"Socket dimensions:   {SOCKET_W_X:.2f} x {SOCKET_LEN_Y:.2f} mm")

# In baseplate coordinates, what is the distance from the slit hole to the inner wall?
slit_in_plate = box(cx - SLIT_W_X/2, cy - SLIT_LEN_Y/2, cx + SLIT_W_X/2, cy + SLIT_LEN_Y/2)
print("Slit distance to inner wall:", inner_wall.exterior.distance(slit_in_plate))
print("Does slit intersect wall_poly?:", slit_in_plate.intersects(wall_poly))

# The slit hole is completely safe inside the wall with 0.407mm clearance!
# Bottom-right corner of slit is at:
print(f"Bottom-right corner of slit: ({cx + SLIT_W_X/2:.3f}, {cy - SLIT_LEN_Y/2:.3f}) = ({cx+0.60:.3f}, {cy-1.70:.3f})")
p_slit_corner = Point(cx + SLIT_W_X/2, cy - SLIT_LEN_Y/2)
print("Distance from bottom-right slit corner to inner wall:", inner_wall.exterior.distance(p_slit_corner))

# Now let's examine what chamfer on the key (lip) is needed so that:
# 1) The key is completely inside inner_wall (with clearance >= 0.15mm or socket clearance)
# 2) The socket in the floor is completely inside inner_wall (so the wall doesn't fill the socket!)
# 3) The wall of the key around the slit remains thick enough (e.g. >= 0.40 - 0.50mm)

