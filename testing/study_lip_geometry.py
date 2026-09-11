import os, sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, INSERT_KEY_HEIGHT,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_CLEARANCE,
    INSERT_BODY_W_X, INSERT_BODY_LEN_Y, INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP,
    SLIT_W_X, SLIT_LEN_Y
)

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_wall = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_poly = outer_body_poly.difference(inner_wall)

cx = 8.453
cy = -13.589

print(f"=== DETAILED LIP GEOMETRY STUDY ===")
print(f"Key dims: W={INSERT_KEY_W_X}, L={INSERT_KEY_LEN_Y}")
print(f"Slit dims: W={SLIT_W_X}, L={SLIT_LEN_Y}")

# Slit hole in relative coords:
slit_box = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
# Blade is 0.77 x 3.10
blade_box = box(-0.77/2, -3.10/2, 0.77/2, 3.10/2)

# In plate coordinates:
slit_in_plate = translate(slit_box, xoff=cx, yoff=cy)
blade_in_plate = translate(blade_box, xoff=cx, yoff=cy)

print(f"Blade in plate intersects wall_poly? {blade_in_plate.intersects(wall_poly)}")
print(f"Blade distance to inner_wall: {inner_wall.exterior.distance(blade_in_plate):.4f} mm")

# Notice: The brass blade itself is 100% inside inner_wall with >0.30mm clearance!
# What about the slit hole (1.20 x 3.40mm)?
print(f"Slit in plate intersects wall_poly? {slit_in_plate.intersects(wall_poly)}")
if slit_in_plate.intersects(wall_poly):
    inter = slit_in_plate.intersection(wall_poly)
    print(f"Slit overlap area: {inter.area:.4f} mm^2, bounds: {inter.bounds}")

# Wait! Does the slit hole need a tiny corner bevel or is it fine?
# Let's check:
# Bottom right corner of blade is at:
# X = cx + 0.77/2 = 8.453 + 0.385 = 8.838
# Y = cy - 3.10/2 = -13.589 - 1.550 = -15.139
# At X = 8.838, what is the Y of inner_wall?
line_x = LineString([(8.838, -16.0), (8.838, -14.0)])
pt_wall = line_x.intersection(inner_wall.exterior)
print(f"At X = 8.838 (right edge of blade), inner wall Y is: {pt_wall.y:.4f} (blade bottom is -15.139)")
print(f"Margin in Y between blade and inner wall: {pt_wall.y - (-15.139):.4f} mm")

