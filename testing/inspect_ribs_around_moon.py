"""
testing/inspect_ribs_around_moon.py
Inspects all ribs (floor grid ribs and bracket seating ribs) near the half moon.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon

import build_part as bp

print("=== BRACKET SEATING RIBS ===")
for i, y in enumerate(bp.BRACKET_SEATING_RIB_Y):
    print(f"Seating Rib {i+1}: Y = {y:.2f} mm (Z: 1.00 to 2.15 mm)")

print("\n=== FLOOR GRID RIBS ===")
base_poly, outer_poly, _ = bp.get_exact_base_polygon()
grid_ribs = bp.create_grid_ribs_poly(base_poly, outer_poly)
# Check grid lines around Brackets 3 & 4
# In build_part.py, what are the grid lines?
# Let's inspect create_grid_ribs_poly source code
import inspect
print(inspect.getsource(bp.create_grid_ribs_poly))
