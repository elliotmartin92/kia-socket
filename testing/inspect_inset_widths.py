"""
Calculate interior widths and dimensions of all inset sidewalls across the part.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon

from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

coords_out = np.array(outer_body_poly.exterior.coords)
coords_in = np.array(inner_wall_poly.exterior.coords)

print("=== 1. BOTTOM INSET NOTCH / SIDEWALLS ===")
# Bottom notch exterior sidewalls are at X = -3.70mm and X = +3.70mm
# Bottom tab outer face is Y = -18.539mm, Inset wall outer face is Y = -16.650mm (inset depth = 1.889mm)
# Wall thickness = 1.20mm
# Left inner tab wall: X = -3.70 - 1.20 = -4.90mm or inner corner of notch
# Let's inspect the inner wall coordinates around the bottom:
bottom_inner = coords_in[coords_in[:, 1] < -14.0]
print("Inner wall coordinates at bottom (Y < -14mm):")
for x, y in bottom_inner:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")

print("\n=== 2. SIDE EARS / SIDE INSETS (Left & Right) ===")
# Left side ear: X in SVG around Y = 0
left_pts = coords_out[coords_out[:, 0] < -19.0]
right_pts = coords_out[coords_out[:, 0] > 19.0]
print("Leftmost exterior points:")
for x, y in left_pts:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")
print("Rightmost exterior points:")
for x, y in right_pts:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")

left_inner = coords_in[coords_in[:, 0] < -18.0]
right_inner = coords_in[coords_in[:, 0] > 18.0]
print("Leftmost inner wall points:")
for x, y in left_inner:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")
print("Rightmost inner wall points:")
for x, y in right_inner:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")

print("\n=== 3. TOP TAB INSET SIDEWALLS ===")
top_out = coords_out[coords_out[:, 1] > 18.0]
top_in = coords_in[coords_in[:, 1] > 17.0]
print("Top exterior points:")
for x, y in top_out:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")
print("Top inner points:")
for x, y in top_in:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")
