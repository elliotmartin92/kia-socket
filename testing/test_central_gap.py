"""
Test ribbing with central 3.66mm vertical gap extending all the way through.
"""
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, OUTER_WALL_THICK, RIB_GRID_X, RIB_GRID_Y, RIB_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
brackets_poly = create_all_brackets_poly()

# Base grid
bounds = base_poly.bounds
rib_boxes = []
for x in np.arange(bounds[0] + 1, bounds[2] - 1, RIB_GRID_X):
    rib_boxes.append(box(x - RIB_THICK/2, bounds[1], x + RIB_THICK/2, bounds[3]))
for y in np.arange(bounds[1] + 1, bounds[3] - 1, RIB_GRID_Y):
    rib_boxes.append(box(bounds[0], y - RIB_THICK/2, bounds[2], y + RIB_THICK/2))
raw_grid = unary_union(rib_boxes)

inner_bounds = base_poly.buffer(-OUTER_WALL_THICK - 0.2)

# 1. No ribs under brackets at all
bracket_footprints = brackets_poly.buffer(0.3)

# 2. Centered 3.66mm gap extending vertically all the way through between the bracket pairs (X = -1.83mm to +1.83mm)
central_vertical_gap = box(-3.66/2.0, -25.0, 3.66/2.0, 25.0)

valid_ribs = raw_grid.intersection(inner_bounds).difference(bracket_footprints).difference(central_vertical_gap)

fig, ax = plt.subplots(figsize=(8, 8), dpi=150)

# Base perimeter
x, y = base_poly.exterior.xy
ax.plot(x, y, 'b-', linewidth=2, label='Outer Wall')
for interior in base_poly.interiors:
    ix, iy = interior.xy
    ax.plot(ix, iy, 'b-', linewidth=1.5)

# Brackets
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax.plot(bx, by, 'g-', linewidth=2)

# Ribs
for geom in (valid_ribs.geoms if hasattr(valid_ribs, 'geoms') else [valid_ribs]):
    rx, ry = geom.exterior.xy
    ax.fill(rx, ry, color='orange', alpha=0.85, edgecolor='none')

ax.annotate('3.66mm Full-Height\nVertical Clearance Gap\n(Between Bracket Pairs)',
            xy=(0, 0), xytext=(0, 0),
            fontsize=9, fontweight='bold', color='purple', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='purple'))

ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_xlim(-22, 22)
ax.set_ylim(-22, 22)
ax.set_title('Updated Ribbing with Full Vertical 3.66mm Central Gap', fontsize=11, fontweight='bold')
plt.savefig('central_gap_preview.png', dpi=150)
print("Saved central_gap_preview.png")
