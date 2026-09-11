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

# What is the boundary of inner_wall near (cx, cy) relative to (cx, cy)?
# Let's inspect the coordinates of inner_wall around the right socket:
p_box = box(cx - 3, cy - 4, cx + 3, cy + 4)
local_inner_wall = inner_wall.intersection(p_box)

print("Local inner wall bounds:", local_inner_wall.bounds)

# Available floor area inside inner_wall centered at (cx, cy):
local_floor = translate(local_inner_wall, xoff=-cx, yoff=-cy)

# Let's check where the wall boundary runs in relative coordinates (X, Y):
# For various Y values from -2.55 to 0:
print("\nWall profile in relative coordinates (X vs Y):")
for y in np.linspace(-2.55, -0.5, 10):
    line = LineString([(-2.0, y), (3.0, y)])
    inter = line.intersection(local_floor.exterior)
    if inter.geom_type == 'MultiPoint':
        pts = [p.x for p in inter.geoms if p.x > 0]
        x_val = pts[0] if pts else None
    elif inter.geom_type == 'Point':
        x_val = inter.x
    else:
        x_val = None
    if x_val is not None:
        print(f"  Y = {y:+.2f} mm -> Wall inner face is at X = {x_val:+.3f} mm")

