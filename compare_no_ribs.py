"""
Visual comparison of interpretations for 'no ribbing under the brackets at all':
1. No ribbing in the bottom region below the brackets (Y < -7.2mm).
2. No ribbing anywhere in the entire rectangular bounding box of each bracket pair.
3. No ribbing across the entire bottom half (Y < -7.2mm) AND entire bracket envelope.
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

# Interpretation A: Entire bounding box of each bracket pair is 100% clear of ribs (from Y = -7.2 to +7.2)
pair_left_bbox = box(b1.bounds[0] - 0.2, b1.bounds[1] - 0.2, b2.bounds[2] + 0.2, b2.bounds[3] + 0.2)
pair_right_bbox = box(b3.bounds[0] - 0.2, b3.bounds[1] - 0.2, b4.bounds[2] + 0.2, b4.bounds[3] + 0.2)
ribs_A = raw_grid.intersection(inner_bounds).difference(unary_union([pair_left_bbox, pair_right_bbox]))

# Interpretation B: Spatially below the brackets (Y < -7.2mm) is 100% clear of ribs, plus no ribs under bracket walls
below_brackets_box = box(-25, -25, 25, -7.17)
ribs_B = raw_grid.intersection(inner_bounds).difference(brackets_poly.buffer(0.3)).difference(below_brackets_box)

# Interpretation C: Both (Entire bracket pair envelopes + bottom area below brackets Y < -7.2mm)
ribs_C = raw_grid.intersection(inner_bounds).difference(unary_union([pair_left_bbox, pair_right_bbox, below_brackets_box]))

# Interpretation D: Bracket columns extending all the way down below brackets to bottom wall
column_left = box(b1.bounds[0] - 0.2, -25, b2.bounds[2] + 0.2, b2.bounds[3] + 0.2)
column_right = box(b3.bounds[0] - 0.2, -25, b4.bounds[2] + 0.2, b4.bounds[3] + 0.2)
ribs_D = raw_grid.intersection(inner_bounds).difference(unary_union([column_left, column_right]))

fig, axes = plt.subplots(2, 2, figsize=(14, 14), dpi=150)
options = [
    ("Option A: Zero Ribs in Entire Bracket Bounding Boxes (Y: -7.2 to +7.2)", ribs_A),
    ("Option B: Zero Ribs in Bottom Area Below Brackets (Y < -7.2mm)", ribs_B),
    ("Option C: Zero Ribs in Bracket Envelopes AND Below Brackets (Y < +7.2mm in bracket area)", ribs_C),
    ("Option D: Zero Ribs in Entire Bracket Columns (from top of brackets to bottom)", ribs_D)
]

for idx, (title, rib_geom) in enumerate(options):
    ax = axes[idx // 2, idx % 2]
    
    # Base perimeter
    x, y = base_poly.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2)
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        ax.plot(ix, iy, 'b-', linewidth=1.5)
        
    # Brackets
    for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
        bx, by = geom.exterior.xy
        ax.plot(bx, by, 'g-', linewidth=2)
        
    # Ribs
    for geom in (rib_geom.geoms if hasattr(rib_geom, 'geoms') else [rib_geom]):
        rx, ry = geom.exterior.xy
        ax.fill(rx, ry, color='orange', alpha=0.85, edgecolor='none')
        
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(-22, 22)
    ax.set_ylim(-22, 22)
    ax.set_title(title, fontsize=9.5, fontweight='bold')

plt.tight_layout()
plt.savefig('no_ribs_under_brackets_options.png', dpi=150)
print("Saved no_ribs_under_brackets_options.png")
