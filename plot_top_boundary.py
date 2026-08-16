"""
Generate a detailed annotated plot showing the ribbing layout relative to the top of the brackets.
"""
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly, create_grid_ribs_poly,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, SCALE, X0, Y0
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
brackets_poly = create_all_brackets_poly()
valid_ribs = create_grid_ribs_poly(base_poly)

fig, ax = plt.subplots(figsize=(10, 10), dpi=150)

# Base perimeter
x, y = base_poly.exterior.xy
ax.plot(x, y, color='#1f77b4', linewidth=2.5, label='Outer Perimeter Wall (6.77mm)')
for interior in base_poly.interiors:
    ix, iy = interior.xy
    ax.plot(ix, iy, color='#d62728', linewidth=1.8)

# Brackets
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax.plot(bx, by, color='#2ca02c', linewidth=2)

# Ribs
for geom in (valid_ribs.geoms if hasattr(valid_ribs, 'geoms') else [valid_ribs]):
    rx, ry = geom.exterior.xy
    ax.fill(rx, ry, color='#ff7f0e', alpha=0.85, edgecolor='none')

# Reference line at top of brackets (Y = +7.17mm)
ax.axhline(y=7.17, color='purple', linestyle='--', linewidth=1.5, alpha=0.8)
ax.text(12, 7.4, 'Top of Brackets (Y = +7.17 mm)\nFull Ribbing Above This Line', 
        fontsize=8.5, fontweight='bold', color='purple')

# Annotations
ax.text(0, 16.5, 'Top Bay:\nContinuous Ribbing Grid', fontsize=9, fontweight='bold', color='#ff7f0e', ha='center')
ax.text(-6.28, 0, 'Left Bracket Pair\n(Zero Ribs in Envelope)', fontsize=8, fontweight='bold', color='#2ca02c', ha='center')
ax.text(6.28, 0, 'Right Bracket Pair\n(Zero Ribs in Envelope)', fontsize=8, fontweight='bold', color='#2ca02c', ha='center')
ax.text(0, 0, 'Center Spine\n(Ribbed)', fontsize=8, fontweight='bold', color='#ff7f0e', ha='center')

ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.4)
ax.set_xlim(-22, 22)
ax.set_ylim(-22, 22)
ax.set_title('Top of Brackets & Ribbing Boundary (Verified)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('top_ribs_boundary.png', dpi=150)
print("Saved top_ribs_boundary.png")
