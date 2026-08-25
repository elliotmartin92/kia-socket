import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    get_exact_base_polygon, OUTER_WALL_THICK,
    TOWER_HEIGHT, TOWER_INTERNAL_GAP, TOWER_WALL_THICK,
    create_all_brackets_poly
)

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

print("Bracket 3 bounds:", b3.bounds)
print("Bracket 3 raw points:")
for p in bracket_3_raw_pts:
    print(f"  ({p[0]:.4f}, {p[1]:.4f})")

# Let's inspect the top wall of Bracket 3:
# Top outer edge: Y = 7.171 (from X = 1.766 to 4.705)
# Top inner roof edge: Y = 6.250 (from X = 2.851 to 3.708)
# Top hook roof: Y = 4.800 (from X = 3.708 to 4.705)
y_top_outer = 7.171
y_top_inner = 6.250
y_wall_mid = (y_top_outer + y_top_inner) / 2.0
wall_thick = y_top_outer - y_top_inner

print(f"\nBracket 3 Top Wall:")
print(f"  Outer edge Y: {y_top_outer:.4f} mm")
print(f"  Inner edge Y: {y_top_inner:.4f} mm")
print(f"  Wall thickness: {wall_thick:.4f} mm")
print(f"  Wall centerline (middle): Y = {y_wall_mid:.4f} mm")

# Current Front Strut / Rib of Left Tower:
# Currently in build_part.py:
# y_min = 7.171, y_max = 13.771
# strut_front: Y in [7.171, 7.971] (0.80mm thick, rib_mid_Y = 7.571mm)
# y_shaft = 10.200

# With user's requirement:
# "the middle of the rib of the left tower shoud intersect with the middle of the wall of bracket 3"
# Mid Y of rib = y_wall_mid = 6.7105 mm
strut_thick = 0.80
new_strut_front_min = y_wall_mid - strut_thick / 2.0 # 6.3105 mm
new_strut_front_max = y_wall_mid + strut_thick / 2.0 # 7.1105 mm

# Tower base y_min should align with front strut min:
new_y_min_base = new_strut_front_min # 6.3105 mm
# Tower length at base = 6.60 mm (13.771 - 7.171)
tower_base_len = 6.60
new_y_max_base = new_y_min_base + tower_base_len # 12.9105 mm

# Tower length at top = 5.63 mm (13.101 - 7.471)
# Top offsets relative to base:
# min_top_offset = 7.471 - 7.171 = 0.30 mm
# max_top_offset = 13.101 - 13.771 = -0.67 mm
new_y_min_top = new_y_min_base + 0.30 # 6.6105 mm
new_y_max_top = new_y_max_base - 0.67 # 12.2405 mm

# Shaft / cradle center:
# Previously: 10.200 - 7.171 = 3.029 mm offset from y_min_base
new_y_shaft = new_y_min_base + 3.029 # 9.3395 mm (~9.340 mm)

# Rear strut:
# Previously: Y in [12.571, 13.771] (thickness = 1.20mm at rear edge)
new_strut_rear_min = new_y_max_base - 1.20 # 11.7105 mm
new_strut_rear_max = new_y_max_base # 12.9105 mm

print(f"\nNew Tower & Rib Dimensions:")
print(f"  Shift delta: {new_y_min_base - 7.171:.4f} mm")
print(f"  New Tower Base Y: [{new_y_min_base:.4f}, {new_y_max_base:.4f}] mm")
print(f"  New Tower Top Y: [{new_y_min_top:.4f}, {new_y_max_top:.4f}] mm")
print(f"  New Shaft Cradle Y: {new_y_shaft:.4f} mm")
print(f"  New Front Strut Y: [{new_strut_front_min:.4f}, {new_strut_front_max:.4f}] mm (Mid: {(new_strut_front_min + new_strut_front_max)/2:.4f} mm)")
print(f"  New Rear Strut Y: [{new_strut_rear_min:.4f}, {new_strut_rear_max:.4f}] mm")

# Plot 2D comparison
fig, ax = plt.subplots(figsize=(12, 10), dpi=180)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
bx, by = base_poly.exterior.xy
ax.plot(bx, by, 'k-', lw=1.5, label='Base Perimeter')
for interior in base_poly.interiors:
    ix, iy = interior.xy
    ax.plot(ix, iy, 'r-', lw=1.5)

# Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    gx, gy = geom.exterior.xy
    ax.plot(gx, gy, color='#2ca02c', lw=1.5)
    ax.fill(gx, gy, color='#2ca02c', alpha=0.15)

# Previous Left Tower & Ribs (dashed red)
prev_left_tower = box(3.90, 7.171, 5.40, 13.771)
prev_front_strut = box(1.90, 7.171, 3.90, 7.971)
ax.plot(*prev_left_tower.exterior.xy, 'r--', lw=1.2, label='Previous Tower (Y_base = 7.171mm)')
ax.plot(*prev_front_strut.exterior.xy, 'r--', lw=1.2)

# New Left & Right Tower & Ribs (solid blue)
new_left_tower = box(3.90, new_y_min_base, 5.40, new_y_max_base)
new_right_tower = box(13.10, new_y_min_base, 14.60, new_y_max_base)
new_front_strut = box(1.90, new_strut_front_min, 3.90, new_strut_front_max)
new_rear_strut = box(1.90, new_strut_rear_min, 3.90, new_strut_rear_max)

ax.fill(*new_left_tower.exterior.xy, color='#1f77b4', alpha=0.35, label='New Left Tower')
ax.plot(*new_left_tower.exterior.xy, color='#1f77b4', lw=2)

ax.fill(*new_right_tower.exterior.xy, color='#1f77b4', alpha=0.35, label='New Right Tower')
ax.plot(*new_right_tower.exterior.xy, color='#1f77b4', lw=2)

ax.fill(*new_front_strut.exterior.xy, color='#ff7f0e', alpha=0.5, label='New Front Strut/Rib')
ax.plot(*new_front_strut.exterior.xy, color='#ff7f0e', lw=2)

ax.fill(*new_rear_strut.exterior.xy, color='#ff7f0e', alpha=0.5, label='New Rear Strut')
ax.plot(*new_rear_strut.exterior.xy, color='#ff7f0e', lw=2)

# Centerlines
ax.axhline(y_wall_mid, color='magenta', linestyle=':', lw=2, label=f'Bracket 3 Wall Center (Y={y_wall_mid:.3f}mm)')
ax.axhline(new_y_shaft, color='cyan', linestyle='-.', lw=1.5, label=f'New Shaft Axis (Y={new_y_shaft:.3f}mm)')

ax.set_xlim(0, 16)
ax.set_ylim(3, 16)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title('Shaft Support Tower Repositioning (Rib Middle = Bracket 3 Wall Middle)', fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=8)

plt.tight_layout()
plt.savefig('testing/tower_bracket3_intersection.png', dpi=180)
print("Saved testing/tower_bracket3_intersection.png")
