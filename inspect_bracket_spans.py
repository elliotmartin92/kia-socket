"""
Inspect SVG for any lines or hints in the bracket area and test rib gap interpretations.
"""
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, SCALE, X0, Y0, OUTER_WALL_THICK, RIB_GRID_X, RIB_GRID_Y, RIB_THICK
)

b1 = to_mm_poly(bracket_1_raw_pts)
b2 = to_mm_poly(bracket_2_raw_pts)
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)
brackets = [b1, b2, b3, b4]

print(f"B1 bounds: {b1.bounds}")
print(f"B2 bounds: {b2.bounds}")
print(f"B3 bounds: {b3.bounds}")
print(f"B4 bounds: {b4.bounds}")
print(f"Left bracket pair (B1..B2) X span: [{b1.bounds[0]:.2f}, {b2.bounds[2]:.2f}]")
print(f"Center space (B2..B3) X span: [{b2.bounds[2]:.2f}, {b3.bounds[0]:.2f}]")
print(f"Right bracket pair (B3..B4) X span: [{b3.bounds[0]:.2f}, {b4.bounds[2]:.2f}]")
print(f"Bracket Y span: [{b1.bounds[1]:.2f}, {b1.bounds[3]:.2f}], Height = {b1.bounds[3] - b1.bounds[1]:.2f} mm")
