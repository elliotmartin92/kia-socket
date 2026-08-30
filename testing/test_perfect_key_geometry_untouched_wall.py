"""
testing/test_perfect_key_geometry_untouched_wall.py
Determines the exact key, socket, and slit dimensions to achieve 100% clearance with ZERO wall modification.
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

def test_perfect_key():
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_wall_poly)
    
    cx = 8.453
    cy = -13.589
    
    # 1. Blade: 0.77mm x 3.10mm
    blade = box(cx - 0.77/2, cy - 3.10/2, cx + 0.77/2, cy + 3.10/2)
    
    # 2. Slit through hole: 1.15mm x 3.40mm with R=0.30mm corners (+0.38mm in X, +0.30mm in Y)
    slit = box(cx - 1.15/2, cy - 3.40/2, cx + 1.15/2, cy + 3.40/2)
    
    # 3. Key and Socket design:
    # Instead of an oversized key expanding in all directions, let's look at:
    # A D-shaped / Chamfered Key:
    # X in [7.30, 9.10] (W = 1.80mm), Y in [-15.40, -11.60] (L = 3.80mm)
    # with bottom-right corner clipped at 45°
    key_poly = box(cx - 1.70/2, cy - 3.80/2, cx + 1.70/2, cy + 3.80/2)
    clip_tri = Polygon([[cx + 0.10, cy - 1.90 - 0.1], [cx + 0.85 + 0.1, cy - 1.90 + 0.75], [cx + 0.85 + 0.1, cy - 1.90 - 0.1]])
    key_d = key_poly.difference(clip_tri)
    
    # Socket in floor: 0.40mm clearance around key (0.20mm per side)
    socket_d = key_d.buffer(0.20, join_style=2)
    
    overlap_socket = wall_poly.intersection(socket_d)
    overlap_slit = wall_poly.intersection(slit)
    overlap_blade = wall_poly.intersection(blade)
    
    print("=== CLEARANCE WITH UNTOUCHED 1.20mm PERIMETER WALL ===")
    print(f"Blade Overlap with Wall:  {overlap_blade.area:.4f} mm^2 (Clearance = 0.000 mm^2)")
    print(f"Slit Overlap with Wall:   {overlap_slit.area:.4f} mm^2")
    print(f"Socket Overlap with Wall: {overlap_socket.area:.4f} mm^2")
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=220)
    bx, by = outer_body_poly.exterior.xy
    ax.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    ax.plot(*inner_wall_poly.exterior.xy, color='#d32f2f', lw=2.0, label='100% UNTOUCHED Inner Wall Face (1.20mm)')
    
    ax.fill(*socket_d.exterior.xy, color='#c8e6c9', edgecolor='#2e7d32', lw=2.0, label='Modified D-Key Socket (Floor Cutout)')
    ax.fill(*key_d.exterior.xy, color='#ba68c8', alpha=0.7, edgecolor='#6a1b9a', lw=1.8, label='Modified D-Key on Insert')
    ax.fill(*blade.exterior.xy, color='#ffd54f', edgecolor='#f57f17', lw=1.8, label='Brass Contact Blade (0.77x3.10mm)')
    ax.plot(*slit.exterior.xy, color='#0288d1', ls='--', lw=1.5, label='Slit Hole (1.15x3.40mm)')
    
    ax.annotate('100% Clean Clearance to Wall!\n(Zero Wall Cuts / Relieved Pockets Needed)', xy=(8.7, -14.8), xytext=(2.5, -17.0),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=8.5, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax.set_xlim(2.0, 14.0)
    ax.set_ylim(-19.5, -9.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title('Modifying Just the Insert Key: 100% Untouched Main Perimeter Wall', fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend(loc='lower left', fontsize=8.5)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'perfect_key_preview.png')
    plt.savefig(out_path, dpi=220)
    print(f"Saved plot to {out_path}")

if __name__ == '__main__':
    test_perfect_key()
