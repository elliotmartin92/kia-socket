"""
testing/inspect_key_modification_option.py
Inspects what happens if we modify ONLY the insert key (and floor socket shape)
so that the perimeter wall of the main part remains 100% standard, untouched, and un-notched.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK, BASE_THICK
)

def inspect_key_only():
    print("=== INSPECTING INSERT KEY MODIFICATION OPTION ===")
    
    # Get raw base geometry without wall relief
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly_untouched = outer_body_poly.difference(inner_wall_poly)
    
    cx_right = 8.453
    cy_right = -13.589
    
    # 1. Slit through hole (1.35mm x 3.65mm)
    slit_w = 1.35
    slit_l = 3.65
    slit_box = box(cx_right - slit_w/2, cy_right - slit_l/2, cx_right + slit_w/2, cy_right + slit_l/2)
    
    # Check distance between slit and untouched inner wall:
    slit_inter_wall = wall_poly_untouched.intersection(slit_box)
    dist_slit_to_wall = inner_wall_poly.exterior.distance(slit_box)
    
    print(f"Slit Box (1.35mm x 3.65mm at X=+8.453, Y=-13.589):")
    print(f"  Overlap with untouched inner wall: {slit_inter_wall.area:.4f} mm^2")
    if not slit_inter_wall.is_empty:
        b = slit_inter_wall.bounds
        print(f"  WARNING: Slit hole itself intersects the 1.20mm wall by X in [{b[0]:.3f}, {b[2]:.3f}], Y in [{b[1]:.3f}, {b[3]:.3f}]")
        print(f"  Intersecting width in X = {b[2]-b[0]:.3f} mm, length in Y = {b[3]-b[1]:.3f} mm")
    
    # Check with 1.20mm x 3.50mm slit
    slit_box_narrow = box(cx_right - 1.20/2, cy_right - 3.50/2, cx_right + 1.20/2, cy_right + 3.50/2)
    slit_narrow_inter = wall_poly_untouched.intersection(slit_box_narrow)
    print(f"\nNarrower Slit Box (1.20mm x 3.50mm):")
    print(f"  Overlap with untouched inner wall: {slit_narrow_inter.area:.4f} mm^2")
    if not slit_narrow_inter.is_empty:
        b = slit_narrow_inter.bounds
        print(f"  Intersecting width in X = {b[2]-b[0]:.3f} mm, length in Y = {b[3]-b[1]:.3f} mm")
        
    # Check blade itself (0.77mm x 3.10mm)
    blade_box = box(cx_right - 0.77/2, cy_right - 3.10/2, cx_right + 0.77/2, cy_right + 3.10/2)
    blade_inter = wall_poly_untouched.intersection(blade_box)
    print(f"\nOEM Blade itself (0.77mm x 3.10mm centered at X=+8.453, Y=-13.589):")
    print(f"  Overlap with untouched inner wall: {blade_inter.area:.4f} mm^2")
    if not blade_inter.is_empty:
        b = blade_inter.bounds
        print(f"  Intersecting width in X = {b[2]-b[0]:.3f} mm, length in Y = {b[3]-b[1]:.3f} mm")

    # Generate detailed visual plot
    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
    bx, by = outer_body_poly.exterior.xy
    ax.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    ax.plot(*inner_wall_poly.exterior.xy, color='#d32f2f', lw=2.0, label='Perimeter Inner Wall Face (1.20mm thick)')
    
    ax.fill(*blade_box.exterior.xy, color='#ffd54f', edgecolor='#f57f17', lw=1.8, label='Brass Contact Blade (0.77x3.10mm)')
    ax.plot(*slit_box.exterior.xy, color='#0288d1', ls='--', lw=1.8, label='Slit Hole (1.35x3.65mm)')
    
    # Detent socket without modification vs modified key
    ax.set_xlim(5.0, 12.0)
    ax.set_ylim(-18.0, -10.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title('Clearance Analysis: Untouched 1.20mm Wall vs Slit & Blade at X = +8.453mm', fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend(loc='lower left', fontsize=8.5)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'inspect_key_modification.png')
    plt.savefig(out_path, dpi=200)
    print(f"Saved plot to {out_path}")

if __name__ == '__main__':
    inspect_key_only()
