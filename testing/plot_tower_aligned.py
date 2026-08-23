"""
Plot the new aligned shaft towers based on the exact user measurements:
- Left tower aligned with top-right corner of Bracket 3 (X = 4.705mm)
- Right tower 7.86mm to the right (X = 12.565mm)
- Y span: 22.68mm from bottom inner wall (Y in [5.34mm, 9.99mm])
"""
import matplotlib.pyplot as plt
from shapely.geometry import box
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_THICK, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

# Left tower aligned with right wall of Bracket 3 (X = 4.705mm)
x_left_inner = 4.705
x_left_outer = x_left_inner - TOWER_WALL_THICK

# Right tower spaced 7.86mm to the right
x_right_inner = x_left_inner + TOWER_INTERNAL_GAP  # 12.565mm
x_right_outer = x_right_inner + TOWER_WALL_THICK   # 13.565mm

# Y coordinates: 22.68mm from bottom inner wall (-17.339mm)
y_bot = -17.339 + 22.68  # 5.341mm
y_top = y_bot + TOWER_Y_LEN  # 9.991mm
y_shaft = (y_bot + y_top) / 2.0  # 7.666mm

left_tower_box = box(x_left_outer, y_bot, x_left_inner, y_top)
right_tower_box = box(x_right_inner, y_bot, x_right_outer, y_top)

fig, ax = plt.subplots(figsize=(14, 14), dpi=180)

# Base and rim
x, y = base_poly.exterior.xy
ax.plot(x, y, color='#1f77b4', linewidth=2.5, label='Perimeter Wall')
ix, iy = inner_wall_poly.exterior.xy
ax.plot(ix, iy, color='#1f77b4', linestyle='--', linewidth=1.5, label='Inner Perimeter Wall')

# Holes
for interior in base_poly.interiors:
    hx, hy = interior.xy
    ax.plot(hx, hy, color='#d62728', linewidth=2, label='Through Holes' if interior == base_poly.interiors[0] else "")

# Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax.plot(bx, by, color='#2ca02c', linewidth=2, label='Brackets' if geom == brackets_poly.geoms[0] else "")

# Towers
for tbox in [left_tower_box, right_tower_box]:
    tx, ty = tbox.exterior.xy
    ax.fill(tx, ty, color='#e377c2', alpha=0.85, edgecolor='#c51b7d', linewidth=2, label='Shaft Towers' if tbox == left_tower_box else "")

# Shaft axis line
ax.plot([x_left_outer - 1.5, x_right_outer + 1.5], [y_shaft, y_shaft], color='#ff7f0e', linestyle='-.', linewidth=2.5, label='Shaft Axis (Y = 7.67mm)')

# Annotations
ax.set_xlim(-6, 20)
ax.set_ylim(-10, 20)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.7)

ax.text(3.24, -2.0, "Bracket 3", fontsize=11, fontweight='bold', color='#2ca02c', ha='center')
ax.text(9.32, -2.0, "Bracket 4", fontsize=11, fontweight='bold', color='#2ca02c', ha='center')
ax.text(hole_x, hole_y, "Top-Right Hole", fontsize=10, fontweight='bold', color='#d62728', ha='center', va='center')

# Callouts
ax.annotate('Left Tower\nshares Bracket 3\ntop-right corner', xy=(4.705, 7.17), xytext=(0, 10.5),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=6),
            fontsize=10, fontweight='bold', color='#c51b7d')

ax.annotate(f'Internal Span\n{TOWER_INTERNAL_GAP}mm', xy=((x_left_inner + x_right_inner)/2, y_top + 0.5),
            fontsize=10, fontweight='bold', color='#8c8d00', ha='center')

ax.annotate(f'Y = 22.68mm from\nbottom inner wall', xy=(x_left_outer - 0.5, (y_bot + y_top)/2),
            fontsize=9, fontweight='bold', color='#333333', ha='right', va='center')

ax.set_title('Aligned Shaft Support Towers (Based on Caliper Measurements)', fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.savefig('aligned_towers_preview.png', dpi=180)
print("Saved aligned_towers_preview.png")
