"""
testing/test_bracket_seating_ribs.py
Models and visualizes the 1.48mm tall brass seating ribs inside both bracket pairs.
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

# Looser bracket coordinates
b1_looser_pts = [
    (-10.791,  7.136), (-8.000,  7.136), (-8.000,  4.950), (-8.900,  4.950),
    (-8.900,  6.400), (-9.857,  6.400), (-9.857, -6.200), (-8.150, -6.200),
    (-8.150, -7.171), (-10.791, -7.171), (-10.791,  7.136)
]

b2_looser_pts = [
    (-1.766,  7.171), (-4.500,  7.171), (-4.500,  4.950), (-3.650,  4.950),
    (-3.650,  6.400), (-2.701,  6.400), (-2.701, -6.200), (-4.350, -6.200),
    (-4.350, -7.136), (-1.766, -7.136), (-1.766,  7.171)
]

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

BRACKET_SEATING_RIB_HEIGHT = 1.48  # 1.48mm protrusion above floor (Z: 1.00 to 2.48mm)
BRACKET_SEATING_RIB_EXT = 3.00     # Extends ~3.0mm from interior bracket spine walls
BRACKET_SEATING_RIB_THICK = 0.60   # 0.60mm thick in Y (matching grid ribs)

# Let's inspect the 4 Y positions:
# In the bracket Y span [-6.20, +6.40], the grid lines are:
# Y = -3.20, 0.00, +3.20, +6.40
Y_POSITIONS_GRID = [-3.20, 0.00, 3.20, 6.40]

# Or 4 evenly distributed positions across the interior seating area Y in [-5.0, +5.0]:
# e.g. Y = -4.50, -1.50, +1.50, +4.50 (spacing = 3.0mm)
# Let's test both!

def create_bracket_seating_ribs_poly(y_positions=Y_POSITIONS_GRID, rib_thick=BRACKET_SEATING_RIB_THICK, ext=BRACKET_SEATING_RIB_EXT):
    """
    Creates 2D polygons for the 4 sets of 1.48mm tall seating ribs in both bracket pairs.
    - Left Pair (B1 & B2):
      - Ribs on B1 extend from X = -9.857 to X = -9.857 + ext = -6.857
      - Ribs on B2 extend from X = -2.701 to X = -2.701 - ext = -5.701
    - Right Pair (B3 & B4):
      - Ribs on B3 extend from X = +2.701 to X = +2.701 + ext = +5.701
      - Ribs on B4 extend from X = +9.857 to X = +9.857 - ext = +6.857
    """
    b1_x_spine = -9.857
    b2_x_spine = -2.701
    b3_x_spine = 2.701
    b4_x_spine = 9.857
    
    rib_polys = []
    
    for y in y_positions:
        y_min = y - rib_thick / 2.0
        y_max = y + rib_thick / 2.0
        
        # Left pair ribs (B1 side & B2 side)
        r_b1 = box(b1_x_spine, y_min, b1_x_spine + ext, y_max)
        r_b2 = box(b2_x_spine - ext, y_min, b2_x_spine, y_max)
        
        # Right pair ribs (B3 side & B4 side)
        r_b3 = box(b3_x_spine, y_min, b3_x_spine + ext, y_max)
        r_b4 = box(b4_x_spine - ext, y_min, b4_x_spine, y_max)
        
        rib_polys.extend([r_b1, r_b2, r_b3, r_b4])
        
    return unary_union(rib_polys)

def run_analysis():
    print("=== TESTING BRACKET SEATING RIBS (1.48mm Tall) ===")
    ribs_poly = create_bracket_seating_ribs_poly()
    
    print(f"Number of rib geometries: {len(ribs_poly.geoms) if hasattr(ribs_poly, 'geoms') else 1}")
    print(f"Seating Rib Height above Floor: {BRACKET_SEATING_RIB_HEIGHT:.2f} mm (Z in [1.00, {1.00 + BRACKET_SEATING_RIB_HEIGHT:.2f}] mm)")
    print(f"Extension into Channel: {BRACKET_SEATING_RIB_EXT:.2f} mm")
    print(f"Left Pair Spine Span: X in [{-9.857:.3f}, {-2.701:.3f}] (Total Width: {7.156:.3f} mm)")
    print(f"  - B1 Rib: X in [{-9.857:.3f}, {-9.857 + 3.0:.3f}] mm (3.0mm extension)")
    print(f"  - B2 Rib: X in [{-2.701 - 3.0:.3f}, {-2.701:.3f}] mm (3.0mm extension)")
    print(f"  - Central Slot Gap between B1 & B2 ribs: {-2.701 - 3.0 - (-9.857 + 3.0):.3f} mm")
    
    print(f"\nRight Pair Spine Span: X in [{2.701:.3f}, {9.857:.3f}] (Total Width: {7.156:.3f} mm)")
    print(f"  - B3 Rib: X in [{2.701:.3f}, {2.701 + 3.0:.3f}] mm (3.0mm extension)")
    print(f"  - B4 Rib: X in [{9.857 - 3.0:.3f}, {9.857:.3f}] mm (3.0mm extension)")
    print(f"  - Central Slot Gap between B3 & B4 ribs: {9.857 - 3.0 - (2.701 + 3.0):.3f} mm")
    
    # Let's plot and visualize
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)
    
    # Left Pair
    ax1 = axes[0]
    p1 = Polygon(b1_looser_pts)
    p2 = Polygon(b2_looser_pts)
    ax1.plot(*p1.exterior.xy, color='#0d47a1', lw=2.5, label='Bracket 1 (Outer)')
    ax1.plot(*p2.exterior.xy, color='#1b5e20', lw=2.5, label='Bracket 2 (Inner)')
    ax1.fill(*p1.exterior.xy, color='#1976d2', alpha=0.15)
    ax1.fill(*p2.exterior.xy, color='#388e3c', alpha=0.15)
    
    # Draw Seating Ribs
    for geom in (ribs_poly.geoms if hasattr(ribs_poly, 'geoms') else [ribs_poly]):
        gx, gy = geom.exterior.xy
        if max(gx) < 0:
            ax1.fill(gx, gy, color='#d32f2f', alpha=0.85, edgecolor='#b71c1c', lw=1.2, label='1.48mm Tall Seating Rib' if min(gy) < -3.0 else "")
            
    # Overlay Brass Footprint
    brass_left_rect = patches.Rectangle((-6.28 - 3.37, -5.80), 6.74, 11.80,
                                        facecolor='#ffd54f', alpha=0.3, edgecolor='#f57f17', lw=1.8, ls='--', label='Brass Contact (6.74mm W)')
    ax1.add_patch(brass_left_rect)
    
    ax1.set_xlim(-12.5, 0.0)
    ax1.set_ylim(-8.5, 8.5)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('Left Bracket Pair: 4 Sets of 1.48mm Tall Brass Seating Ribs', fontsize=12, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='lower left', fontsize=8.5)
    
    # Right Pair
    ax2 = axes[1]
    p3 = Polygon(b3_looser_pts)
    p4 = Polygon(b4_looser_pts)
    ax2.plot(*p3.exterior.xy, color='#1b5e20', lw=2.5, label='Bracket 3 (Inner)')
    ax2.plot(*p4.exterior.xy, color='#0d47a1', lw=2.5, label='Bracket 4 (Outer)')
    ax2.fill(*p3.exterior.xy, color='#388e3c', alpha=0.15)
    ax2.fill(*p4.exterior.xy, color='#1976d2', alpha=0.15)
    
    # Draw Seating Ribs
    for geom in (ribs_poly.geoms if hasattr(ribs_poly, 'geoms') else [ribs_poly]):
        gx, gy = geom.exterior.xy
        if min(gx) > 0:
            ax2.fill(gx, gy, color='#d32f2f', alpha=0.85, edgecolor='#b71c1c', lw=1.2, label='1.48mm Tall Seating Rib' if min(gy) < -3.0 else "")
            
    # Overlay Brass Footprint
    brass_right_rect = patches.Rectangle((6.28 - 3.37, -5.80), 6.74, 11.80,
                                         facecolor='#ffd54f', alpha=0.3, edgecolor='#f57f17', lw=1.8, ls='--', label='Brass Contact (6.74mm W)')
    ax2.add_patch(brass_right_rect)
    
    ax2.set_xlim(0.0, 12.5)
    ax2.set_ylim(-8.5, 8.5)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('Right Bracket Pair: 4 Sets of 1.48mm Tall Brass Seating Ribs', fontsize=12, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.legend(loc='lower right', fontsize=8.5)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'bracket_seating_ribs_preview.png')
    plt.savefig(out_path, dpi=180)
    print(f"Saved seating ribs preview to: {out_path}")

if __name__ == '__main__':
    run_analysis()
