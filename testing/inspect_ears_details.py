import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, get_exact_base_polygon, OUTER_WALL_THICK
import numpy as np
import shapely.geometry as sg

base_poly, outer_poly, _ = get_exact_base_polygon()
inner_poly = outer_poly.buffer(-OUTER_WALL_THICK)

print("Base polygon bounds:", base_poly.bounds)
print("Outer polygon bounds:", outer_poly.bounds)

# Let's inspect the ear regions
# Right ear is around X in [18, 21], Y in [-5, 5]
# Left ear is around X in [-21, -18], Y in [-5, 5]

right_pts = [p for p in outer_poly.exterior.coords if p[0] > 18.0]
left_pts = [p for p in outer_poly.exterior.coords if p[0] < -18.0]

print("\nRight ear exterior coords:")
for p in right_pts:
    print(f"  X = {p[0]:7.3f}, Y = {p[1]:7.3f}")

print("\nLeft ear exterior coords:")
for p in left_pts:
    print(f"  X = {p[0]:7.3f}, Y = {p[1]:7.3f}")

right_y = [p[1] for p in right_pts]
left_y = [p[1] for p in left_pts]

print(f"\nRight ear Y range: min={min(right_y):.3f}, max={max(right_y):.3f}, total height in Y = {max(right_y) - min(right_y):.3f} mm")
print(f"Left ear Y range:  min={min(left_y):.3f}, max={max(left_y):.3f}, total height in Y = {max(left_y) - min(left_y):.3f} mm")
