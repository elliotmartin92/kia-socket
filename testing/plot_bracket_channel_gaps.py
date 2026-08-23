"""
Test ribbing where the vertical clearance gaps are inside the left bracket pair
(between the 2 left walls) and inside the right bracket pair (between the 2 right walls).
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

# Base grid
bounds = base_poly.bounds
rib_boxes = []
for x in np.arange(bounds[0] + 1, bounds[2] - 1, RIB_GRID_X):
    rib_boxes.append(box(x - RIB_THICK/2, bounds[1], x + RIB_THICK/2, bounds[3]))
for y in np.arange(bounds[1] + 1, bounds[3] - 1, RIB_GRID_Y):
    rib_boxes.append(box(bounds[0], y - RIB_THICK/2, bounds[2], y + RIB_THICK/2))
raw_grid = unary_union(rib_boxes)

inner_bounds = base_poly.buffer(-OUTER_WALL_THICK - 0.2)

# Bracket solid footprints
bracket_footprints = brackets_poly.buffer(0.3)

# 1. Left Pair Channel Gap (between Wall 1 and Wall 2) extending vertically all the way through
# Left channel span: from B1 inner edge (-7.85) to B2 inner edge (-4.67), or full pair bounding box [-10.79, -1.77]
# Let's test clearing between Wall 1 & Wall 2 (X: -7.85 to -4.67) or full pair channel
left_pair_gap_inner = box(b1.bounds[2] - 0.1, -25.0, b2.bounds[0] + 0.1, 25.0)
right_pair_gap_inner = box(b3.bounds[2] - 0.1, -25.0, b4.bounds[0] + 0.1, 25.0)

# Full bracket envelope gap (across each entire bracket pair)
left_pair_gap_full = box(b1.bounds[0] - 0.2, -25.0, b2.bounds[2] + 0.2, 25.0)
right_pair_gap_full = box(b3.bounds[0] - 0.2, -25.0, b4.bounds[2] + 0.2, 25.0)

fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

for idx, (title, left_gap, right_gap) in enumerate([
    ("Option 1: Vertical Gap in Channel Between the 2 Walls of Each Pair", left_pair_gap_inner, right_pair_gap_inner),
    ("Option 2: Vertical Gap Covering the Entire Pair Envelopes", left_pair_gap_full, right_pair_gap_full)
]):
    ax = axes[idx]
    
    valid_ribs = raw_grid.intersection(inner_bounds).difference(bracket_footprints).difference(unary_union([left_gap, right_gap]))
    
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
    for geom in (valid_ribs.geoms if hasattr(valid_ribs, 'geoms') else [valid_ribs]):
        rx, ry = geom.exterior.xy
        ax.fill(rx, ry, color='orange', alpha=0.85, edgecolor='none')
        
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(-22, 22)
    ax.set_ylim(-22, 22)
    ax.set_title(title, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('bracket_channels_gap_preview.png', dpi=150)
print("Saved bracket_channels_gap_preview.png")
