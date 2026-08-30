"""
testing/deep_inspect_right_slit.py
Deep inspection of the right slit region using 2D Shapely geometry.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly, create_arch_wall_poly,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    OUTER_WALL_THICK, BASE_THICK, BRACKET_HEIGHT, OUTER_WALL_HEIGHT
)

def inspect_deep():
    print("=== DEEP INSPECTION OF RIGHT SLIT REGION ===")
    
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall = outer_body_poly.buffer(-OUTER_WALL_THICK)
    b_poly = create_all_brackets_poly()
    arch_poly = create_arch_wall_poly()
    
    # Let's inspect the detent sockets in base_poly
    # Sockets in base_poly:
    # Left: cx = -7.853, cy = -13.589
    # Right: cx = +8.453, cy = -13.589
    
    # Let's plot high-resolution 2D views
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=200)
    
    # Panel 1: Left Slit Region Close-Up
    ax1 = axes[0]
    bx, by = outer_body_poly.exterior.xy
    ax1.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Face')
    ax1.plot(*inner_wall.exterior.xy, color='#1976d2', ls='--', lw=1.5, label='Perimeter Inner Face (1.2mm wall)')
    
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        if max(ix) < 0:
            ax1.fill(ix, iy, color='#ffcdd2', edgecolor='#d32f2f', lw=2.0, label='Left Detent Socket (Floor Cutout)')
            
    # Left insert shroud footprint (3.80 x 5.60 at X = -7.853)
    shroud_left = box(-7.853 - 3.8/2, -13.589 - 5.6/2, -7.853 + 3.8/2, -13.589 + 5.6/2)
    ax1.fill(*shroud_left.exterior.xy, color='#e1bee7', alpha=0.5, edgecolor='#7b1fa2', lw=1.8, label='Left Shroud (3.8x5.6mm)')
    
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        gx, gy = g.exterior.xy
        if max(gx) < 0:
            ax1.plot(gx, gy, color='#2e7d32', lw=2.0, label='Bracket 1 / 2')
    ax1.plot(*arch_poly.exterior.xy, color='#0d47a1', lw=1.8)
    
    ax1.set_xlim(-16.0, -2.0)
    ax1.set_ylim(-19.5, -5.0)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('Left Slit Area (X = -7.853mm) - Ample Clearance', fontsize=11, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='lower left', fontsize=8)
    
    # Panel 2: Right Slit Region Close-Up
    ax2 = axes[1]
    ax2.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Face')
    ax2.plot(*inner_wall.exterior.xy, color='#1976d2', ls='--', lw=1.5, label='Perimeter Inner Face (1.2mm wall)')
    
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        if min(ix) > 0:
            ax2.fill(ix, iy, color='#ffcdd2', edgecolor='#d32f2f', lw=2.0, label='Right Detent Socket (Floor Cutout)')
            
    # Right insert shroud footprint (3.80 x 5.60 at X = +8.453)
    shroud_right = box(8.453 - 3.8/2, -13.589 - 5.6/2, 8.453 + 3.8/2, -13.589 + 5.6/2)
    ax2.fill(*shroud_right.exterior.xy, color='#e1bee7', alpha=0.5, edgecolor='#7b1fa2', lw=1.8, label='Right Shroud (3.8x5.6mm at X=8.453)')
    
    # Also draw proposed sloped insert with 2.20mm tip & slimmed base (3.60 x 5.40 at X = 8.453)
    shroud_right_slim = box(8.453 - 3.6/2, -13.589 - 5.4/2, 8.453 + 3.6/2, -13.589 + 5.4/2)
    ax2.plot(*shroud_right_slim.exterior.xy, color='#00796b', ls='--', lw=2.0, label='Slimmed Shroud Base (3.6x5.4mm at X=8.453)')
    
    tip_right = box(8.453 - 2.2/2, -13.589 - 4.4/2, 8.453 + 2.2/2, -13.589 + 4.4/2)
    ax2.plot(*tip_right.exterior.xy, color='#004d40', ls=':', lw=2.0, label='Sloped Tip End (2.2x4.4mm at X=8.453)')
    
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        gx, gy = g.exterior.xy
        if min(gx) > 0:
            ax2.plot(gx, gy, color='#2e7d32', lw=2.0, label='Bracket 3 / 4')
    ax2.plot(*arch_poly.exterior.xy, color='#0d47a1', lw=1.8)
    
    ax2.set_xlim(2.0, 16.0)
    ax2.set_ylim(-19.5, -5.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('Right Slit Area (X = +8.453mm) - Wall Collision Analysis', fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.legend(loc='lower left', fontsize=8)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'deep_inspect_right_slit.png')
    plt.savefig(out_path, dpi=200)
    print(f"Saved deep inspection plot to: {out_path}")

if __name__ == '__main__':
    inspect_deep()
