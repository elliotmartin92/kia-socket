"""
testing/compare_bracket_rib_positions.py
Compares rib Y-positioning options for the 4 sets of 1.48mm tall seating ribs.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK, BASE_THICK, BRACKET_HEIGHT,
    RIB_THICK, RIB_GRID_Y
)

b3_looser_pts = [
    (1.766,  7.171), (4.500,  7.171), (4.500,  4.950), (3.650,  4.950),
    (3.650,  6.400), (2.701,  6.400), (2.701, -6.200), (4.350, -6.200),
    (4.350, -7.171), (1.766, -7.171), (1.766,  7.171)
]

b4_looser_pts = [
    (10.791,  7.171), (8.000,  7.171), (8.000,  4.950), (8.900,  4.950),
    (8.900,  6.400), (9.857,  6.400), (9.857, -6.200), (8.150, -6.200),
    (8.150, -7.136), (10.791, -7.136), (10.791,  7.171)
]

p3 = Polygon(b3_looser_pts)
p4 = Polygon(b4_looser_pts)

def create_pair_ribs(y_list, ext=3.0, thick=0.60):
    b3_spine = 2.701
    b4_spine = 9.857
    boxes = []
    for y in y_list:
        boxes.append(box(b3_spine, y - thick/2, b3_spine + ext, y + thick/2))
        boxes.append(box(b4_spine - ext, y - thick/2, b4_spine, y + thick/2))
    return unary_union(boxes)

# Option 1: Symmetrical with 3.20mm pitch (Y = ±1.60, ±4.80 mm)
opt1_y = [-4.80, -1.60, 1.60, 4.80]

# Option 2: Symmetrical with 3.00mm pitch (Y = ±1.50, ±4.50 mm)
opt2_y = [-4.50, -1.50, 1.50, 4.50]

# Option 3: Direct grid pitch with 4 ribs (Y = -4.80, -1.60, +1.60, +4.80) or (Y = -3.20, 0.00, +3.20, +5.50)
opt3_y = [-4.80, -1.60, 1.60, 4.80]

fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)

for idx, (ax, title, y_list) in enumerate([
    (axes[0], "Option 1: Y = [-4.80, -1.60, +1.60, +4.80] mm (3.20mm Pitch)", opt1_y),
    (axes[1], "Option 2: Y = [-4.50, -1.50, +1.50, +4.50] mm (3.00mm Spacing)", opt2_y),
]):
    ax.plot(*p3.exterior.xy, color='#1b5e20', lw=2.5, label='Bracket 3 (Inner)')
    ax.plot(*p4.exterior.xy, color='#0d47a1', lw=2.5, label='Bracket 4 (Outer)')
    ax.fill(*p3.exterior.xy, color='#388e3c', alpha=0.15)
    ax.fill(*p4.exterior.xy, color='#1976d2', alpha=0.15)
    
    ribs = create_pair_ribs(y_list)
    for geom in (ribs.geoms if hasattr(ribs, 'geoms') else [ribs]):
        ax.fill(*geom.exterior.xy, color='#d32f2f', alpha=0.85, edgecolor='#b71c1c', lw=1.2)
        
    brass_rect = patches.Rectangle((6.28 - 3.37, -5.80), 6.74, 11.80,
                                   facecolor='#ffd54f', alpha=0.3, edgecolor='#f57f17', lw=1.8, ls='--', label='Brass Contact (6.74mm W)')
    ax.add_patch(brass_rect)
    
    for y in y_list:
        ax.axhline(y, color='gray', linestyle=':', alpha=0.5)
        ax.text(0.5, y, f"Y={y:+.2f}", fontsize=8, color='gray', va='center')
        
    ax.set_xlim(0.0, 12.5)
    ax.set_ylim(-8.5, 8.5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title(title, fontsize=11.5, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend(loc='lower right', fontsize=8.5)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'compare_seating_rib_positions.png')
plt.savefig(out_path, dpi=180)
print(f"Saved {out_path}")
