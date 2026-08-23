"""
Generate different ribbing gap layouts to visually inspect.
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
b1 = to_mm_poly(bracket_1_raw_pts)
b2 = to_mm_poly(bracket_2_raw_pts)
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)
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

# Gap in Y: centered 3.66mm gap (Y from -1.83 to +1.83) in the bracket region
y_gap_box = box(-15, -3.66/2, 15, 3.66/2)

# Bracket solid walls (no ribbing under bracket at all)
bracket_footprints = brackets_poly.buffer(0.3)

fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

# Option A: Ribs everywhere except under brackets, with a centered 3.66mm Y-gap in the brackets
ribs_A = raw_grid.intersection(inner_bounds).difference(bracket_footprints).difference(
    box(b1.bounds[0] - 0.2, -3.66/2, b4.bounds[2] + 0.2, 3.66/2)
)

# Option B: Ribs in outer bays + in bracket channels (with 3.66mm Y gap), but completely clear in center channel (-1.83 to +1.83 in X)
center_channel_box = box(-3.66/2, -20, 3.66/2, 20)
ribs_B = raw_grid.intersection(inner_bounds).difference(bracket_footprints).difference(
    box(b1.bounds[0] - 0.2, -3.66/2, b4.bounds[2] + 0.2, 3.66/2)
).difference(center_channel_box)

for idx, (title, rib_geom) in enumerate([
    ("Layout A: 3.66mm Centered Y-Gap across Bracket Region", ribs_A),
    ("Layout B: 3.66mm Y-Gap + Clear Center Vertical Corridor", ribs_B)
]):
    ax = axes[idx]
    
    # Base
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
        ax.fill(rx, ry, color='orange', alpha=0.8, edgecolor='none')
        
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(-22, 22)
    ax.set_ylim(-22, 22)
    ax.set_title(title, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('rib_gap_options.png', dpi=150)
print("Saved rib_gap_options.png")
