import os, sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y,
    SLIT_W_X, SLIT_LEN_Y
)

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_wall = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_poly = outer_body_poly.difference(inner_wall)

cx = 8.453
cy = -13.589

# Inner hole (slit) in relative coordinates:
slit_box = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
# Slit corners:
# X: [-0.60, +0.60], Y: [-1.70, +1.70]
# Bottom-right corner of slit is at (+0.60, -1.70).
# In baseplate coords: (cx + 0.60, cy - 1.70) = (9.053, -15.289)

# Key raw box: [-1.30, 1.30] x [-2.40, 2.40]
# Let's test chamfer cuts on the bottom-right corner of the key.
# A 45-degree chamfer cut line can be parameterized by c:
# x - y = c
# The unchamfered bottom-right corner is at x = 1.30, y = -2.40 -> x - y = 3.70
# The bottom-right corner of the slit is at x = 0.60, y = -1.70 -> x - y = 2.30

print("=== 45-DEGREE CHAMFER SWEEP ON KEY ===")
for c in np.linspace(2.50, 3.60, 12):
    # Chamfer line: x - y = c
    # Triangle to cut: for points with x - y > c, bounded by the key
    # Let's construct cutter:
    cutter = Polygon([(c - 2.40, -2.40), (1.30, 1.30 - c), (1.30 + 0.1, 1.30 - c), (1.30 + 0.1, -2.40 - 0.1), (c - 2.40, -2.40 - 0.1)])
    key_poly = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2).difference(cutter)
    
    # Place key in plate:
    key_in_plate = translate(key_poly, xoff=cx, yoff=cy)
    
    # Overlap with wall_poly:
    wall_overlap = key_in_plate.intersection(wall_poly).area
    
    # Minimum wall thickness around slit (distance from key exterior to slit_box):
    slit_dist = key_poly.boundary.distance(slit_box)
    
    print(f"c = {c:.2f} (cut x-y > {c:.2f}): Wall overlap = {wall_overlap:.4f} mm^2, Min wall around slit = {slit_dist:.3f} mm")

