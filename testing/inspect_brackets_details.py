import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, X0, Y0, SCALE
)
from build_shaft import (
    X_LEFT_TOWER_INNER, X_LEFT_TOWER_OUTER,
    X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    Y_AXLE, Z_AXLE
)
import numpy as np
import shapely.geometry as sg

b1 = to_mm_poly(bracket_1_raw_pts)
b2 = to_mm_poly(bracket_2_raw_pts)
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

brackets = [('Bracket 1', b1, bracket_1_raw_pts),
            ('Bracket 2', b2, bracket_2_raw_pts),
            ('Bracket 3', b3, bracket_3_raw_pts),
            ('Bracket 4', b4, bracket_4_raw_pts)]

for name, poly, raw in brackets:
    pts_mm = [((x - X0) * SCALE, -(y - Y0) * SCALE) for x, y in raw]
    print(f"\n=== {name} ===")
    print(f"Bounds: X in [{poly.bounds[0]:.3f}, {poly.bounds[2]:.3f}], Y in [{poly.bounds[1]:.3f}, {poly.bounds[3]:.3f}]")
    print("Vertices (X, Y) in mm:")
    for i, (x, y) in enumerate(pts_mm):
        print(f"  [{i:2d}] X = {x:7.3f}, Y = {y:7.3f} (raw: {raw[i]})")

print("\n=== Left Tower Position ===")
print(f"Left Tower X in [{X_LEFT_TOWER_OUTER:.3f}, {X_LEFT_TOWER_INNER:.3f}]")
print(f"Bracket 3   X in [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}]")
