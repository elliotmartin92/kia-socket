"""
Plot a clear zoomed-in view of Bracket 3 with simple landmarks.
"""
import matplotlib.pyplot as plt
from shapely.geometry import box
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

fig, ax = plt.subplots(figsize=(14, 14), dpi=180)

# Base and rim
x, y = base_poly.exterior.xy
ax.plot(x, y, color='#1f77b4', linewidth=2.5, label='Perimeter Wall')
ix, iy = inner_wall_poly.exterior.xy
ax.plot(ix, iy, color='#1f77b4', linestyle='--', linewidth=1.5)

# Holes
for interior in base_poly.interiors:
    hx, hy = interior.xy
    ax.plot(hx, hy, color='#d62728', linewidth=2)

# Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax.plot(bx, by, color='#2ca02c', linewidth=2.5)

# Shaded Bracket 3
b3_x, b3_y = b3.exterior.xy
ax.fill(b3_x, b3_y, color='#2ca02c', alpha=0.3, label='Bracket 3 (4.6mm tall wall)')

# Shaded Bracket 4
b4_x, b4_y = b4.exterior.xy
ax.fill(b4_x, b4_y, color='#2ca02c', alpha=0.15, label='Bracket 4 (4.6mm tall wall)')

# Shaded Hole
ax.fill([hole_x - hole_w/2, hole_x + hole_w/2, hole_x + hole_w/2, hole_x - hole_w/2],
        [hole_y - hole_h/2, hole_y - hole_h/2, hole_y + hole_h/2, hole_y + hole_h/2],
        color='#d62728', alpha=0.2, label='Top-Right Through Hole')

# Grid and limits
ax.set_xlim(-6, 20)
ax.set_ylim(-12, 22)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.7)

# Labels
ax.text(0, 0, "Center Spine\n(X = 0, Y = 0)", fontsize=11, fontweight='bold', color='#333333', ha='center')
ax.text(3.24, -2.0, "Bracket 3", fontsize=12, fontweight='bold', color='#2ca02c', ha='center')
ax.text(9.32, -2.0, "Bracket 4", fontsize=12, fontweight='bold', color='#2ca02c', ha='center')
ax.text(hole_x, hole_y, "Top-Right Hole", fontsize=11, fontweight='bold', color='#d62728', ha='center', va='center')
ax.text(0, 20.4, "Top Wall (Y = 20.0mm)", fontsize=11, fontweight='bold', color='#1f77b4', ha='center')
ax.text(0, -19.0, "Bottom Wall (Y = -18.7mm)", fontsize=11, fontweight='bold', color='#1f77b4', ha='center')

# Highlight landmark points with large markers
ax.plot(3.24, 7.17, 'o', color='purple', markersize=10)
ax.text(3.24, 7.6, "Point A: Top of Bracket 3", fontsize=10, fontweight='bold', color='purple', ha='center')

ax.plot(3.24, -7.17, 'o', color='blue', markersize=10)
ax.text(3.24, -7.8, "Point B: Bottom of Bracket 3", fontsize=10, fontweight='bold', color='blue', ha='center')

ax.plot(3.24, 4.58, 'o', color='darkorange', markersize=9)
ax.text(3.6, 4.58, "Point C: Inner hook of Bracket 3", fontsize=9, fontweight='bold', color='darkorange', va='center')

ax.set_title('Landmark Guide: Bracket 3 & Shaft Tower Region', fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.savefig('bracket_landmarks.png', dpi=180)
print("Saved bracket_landmarks.png")
