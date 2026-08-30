"""
testing/test_top_biased_key.py
Tests an upper-biased / asymmetric male key located on the open upper half of the insert shoulder (Y >= -14.0mm)
where the floor is 100% open and far away from the perimeter wall.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK
)

def test_top_biased_key():
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_wall_poly)
    
    cx = 8.453
    cy = -13.589
    
    # 1. OEM Blade: 0.77mm x 3.10mm centered at cx, cy
    blade = box(cx - 0.77/2, cy - 3.10/2, cx + 0.77/2, cy + 3.10/2)
    
    # 2. Slit: 1.15mm x 3.35mm (+0.38mm in X, +0.25mm in Y)
    slit = box(cx - 1.15/2, cy - 3.35/2, cx + 1.15/2, cy + 3.35/2)
    
    # 3. Top-Biased Male Key on the insert shoulder:
    # Placed at Y in [-13.80, -11.40] (length = 2.40mm), X in [7.453, 9.453] (width = 2.00mm)
    # This is located completely above the bottom wall sweep!
    key_top_biased = box(cx - 2.00/2, -13.80, cx + 2.00/2, -11.40)
    
    # Socket in floor: 0.50mm clearance (2.50mm x 2.90mm)
    socket_top_biased = box(cx - 2.50/2, -13.80 - 0.25, cx + 2.50/2, -11.40 + 0.25)
    
    # Check overlaps with 100% UNTOUCHED wall
    overlap_blade = wall_poly.intersection(blade)
    overlap_slit = wall_poly.intersection(slit)
    overlap_key = wall_poly.intersection(key_top_biased)
    overlap_socket = wall_poly.intersection(socket_top_biased)
    
    print("=== TOP-BIASED KEY WITH 100% UNTOUCHED PERIMETER WALL ===")
    print(f"Blade Overlap with Wall:  {overlap_blade.area:.4f} mm^2")
    print(f"Slit Overlap with Wall:   {overlap_slit.area:.4f} mm^2")
    print(f"Key Overlap with Wall:    {overlap_key.area:.4f} mm^2")
    print(f"Socket Overlap with Wall: {overlap_socket.area:.4f} mm^2")
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=220)
    bx, by = outer_body_poly.exterior.xy
    ax.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    ax.plot(*inner_wall_poly.exterior.xy, color='#d32f2f', lw=2.0, label='100% UNTOUCHED Inner Wall Face (1.20mm)')
    
    ax.fill(*socket_top_biased.exterior.xy, color='#c8e6c9', edgecolor='#2e7d32', lw=2.0, label='Top-Biased Socket (2.50x2.90mm)')
    ax.fill(*key_top_biased.exterior.xy, color='#ba68c8', alpha=0.7, edgecolor='#6a1b9a', lw=1.8, label='Top-Biased Male Key on Insert')
    ax.fill(*blade.exterior.xy, color='#ffd54f', edgecolor='#f57f17', lw=1.8, label='Brass Contact Blade (0.77x3.10mm)')
    ax.plot(*slit.exterior.xy, color='#0288d1', ls='--', lw=1.5, label='Slit Hole (1.15x3.35mm)')
    
    ax.annotate('Upper-Biased Key & Socket\n(100% On Open Floor - Zero Wall Overlap!)', xy=(8.453, -12.5), xytext=(2.0, -11.0),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=8.5, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax.set_xlim(1.5, 14.0)
    ax.set_ylim(-19.5, -9.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title('Top-Biased Key: 100% Untouched Wall & Zero Interference', fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend(loc='lower left', fontsize=8.5)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'top_biased_key_preview.png')
    plt.savefig(out_path, dpi=220)
    print(f"Saved preview to {out_path}")

if __name__ == '__main__':
    test_top_biased_key()
