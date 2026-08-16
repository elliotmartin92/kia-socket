"""
Test removing all ribbing below the brackets (Y < -7.17mm).
"""
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, SCALE, X0, Y0, OUTER_WALL_THICK, RIB_GRID_X, RIB_GRID_Y, RIB_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
brackets_poly = create_all_brackets_poly()

b1 = to_mm_poly(bracket_1_raw_pts)
b2 = to_mm_poly(bracket_2_raw_pts)
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

bounds = base_poly.bounds
rib_boxes = []
for x in np.arange(bounds[0] + 1, bounds[2] - 1, RIB_GRID_X):
    rib_boxes.append(box(x - RIB_THICK/2, bounds[1], x + RIB_THICK/2, bounds[3]))
for y in np.arange(bounds[1] + 1, bounds[3] - 1, RIB_GRID_Y):
    rib_boxes.append(box(bounds[0], y - RIB_THICK/2, bounds[2], y + RIB_THICK/2))
raw_grid = unary_union(rib_boxes)
inner_bounds = base_poly.buffer(-OUTER_WALL_THICK - 0.2)

# Exclude left and right bracket bounding envelopes
left_pair_bbox = box(min(p[0] for p in b1.exterior.coords) - 0.2, min(p[1] for p in b1.exterior.coords) - 0.2,
                     max(p[0] for p in b2.exterior.coords) + 0.2, max(p[1] for p in b2.exterior.coords) + 0.2)
right_pair_bbox = box(min(p[0] for p in b3.exterior.coords) - 0.2, min(p[1] for p in b3.exterior.coords) - 0.2,
                      max(p[0] for p in b4.exterior.coords) + 0.2, max(p[1] for p in b4.exterior.coords) + 0.2)

# Exclude ALL area below the brackets (Y < -7.17mm)
below_brackets_box = box(-25, -25, 25, -7.17)

valid_ribs = raw_grid.intersection(inner_bounds).difference(left_pair_bbox).difference(right_pair_bbox).difference(below_brackets_box)

fig, ax = plt.subplots(figsize=(10, 10), dpi=150)

# Base perimeter
x, y = base_poly.exterior.xy
ax.plot(x, y, color='#1f77b4', linewidth=2.5, label='Outer Perimeter Wall')
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

ax.axhline(y=-7.17, color='purple', linestyle='--', linewidth=1.5)
ax.text(0, -9.0, 'No Ribbing Below Brackets (Y < -7.17 mm)', color='purple', fontweight='bold', ha='center')

ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.4)
ax.set_xlim(-22, 22)
ax.set_ylim(-22, 22)
ax.set_title('Zero Ribbing Below Brackets (Clean Bottom Floor)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('no_ribs_below_brackets.png', dpi=150)
print("Saved no_ribs_below_brackets.png")
