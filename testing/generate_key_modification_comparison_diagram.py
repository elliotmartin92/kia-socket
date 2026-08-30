"""
testing/generate_key_modification_comparison_diagram.py
Generates a side-by-side comparison diagram of:
Approach A: Partial-Height Wall Pocket Relief (Full top rim, symmetric key)
Approach B: Modifying Just the Insert Key (Top-biased / Polarized key, 100% untouched wall)
"""
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK, BASE_THICK
)

def generate_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(20, 8.5), dpi=220, facecolor='#ffffff')
    
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly_untouched = outer_body_poly.difference(inner_wall_poly)
    
    cx = 8.453
    cy = -13.589
    bx, by = outer_body_poly.exterior.xy
    
    # --------------------------------------------------------------------------
    # Panel 1: Approach A - Partial-Height Wall Pocket Relief (Currently Implemented)
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    
    # Relieved wall on bottom Z in [1.0, 2.5mm]
    sock_a = box(cx - 2.40/2, cy - 4.70/2, cx + 2.40/2, cy + 4.70/2)
    socket_relief_zone = sock_a.buffer(0.35)
    wall_relieved = wall_poly_untouched.difference(socket_relief_zone)
    for geom in (wall_relieved.geoms if hasattr(wall_relieved, 'geoms') else [wall_relieved]):
        ax1.plot(*geom.exterior.xy, color='#2e7d32', lw=2.0, label='Bottom Wall Face (Z=1.0-2.5mm)' if geom == (wall_relieved.geoms[0] if hasattr(wall_relieved, 'geoms') else wall_relieved) else '')
        
    ax1.plot(*inner_wall_poly.exterior.xy, color='#e65100', ls='--', lw=2.0, label='Solid Top Rim Face (Z=2.5-6.77mm)')
    ax1.fill(*sock_a.exterior.xy, color='#ffcdd2', edgecolor='#d32f2f', lw=1.8, label='Symmetric Socket (2.40x4.70mm)')
    
    key_a = box(cx - 1.90/2, cy - 4.20/2, cx + 1.90/2, cy + 4.20/2)
    ax1.fill(*key_a.exterior.xy, color='#ba68c8', alpha=0.6, edgecolor='#6a1b9a', lw=1.5, label='Symmetric Key (1.90x4.20mm)')
    
    blade = box(cx - 0.77/2, cy - 3.10/2, cx + 0.77/2, cy + 3.10/2)
    ax1.fill(*blade.exterior.xy, color='#ffd54f', edgecolor='#f57f17', lw=1.8, label='Brass Contact Blade')
    
    ax1.annotate('Clearance Pocket (Z=1.0-2.5mm)\nFull Solid Rim Above (Z=2.5-6.77mm)', xy=(8.453, -15.5), xytext=(2.2, -17.2),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=8.0, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax1.set_xlim(1.5, 14.5)
    ax1.set_ylim(-19.5, -9.0)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('Approach A: Partial-Height Wall Relief\n(Symmetric Key + Pocket at Z=1.0-2.5mm)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='lower left', fontsize=7.5)
    
    # --------------------------------------------------------------------------
    # Panel 2: Approach B - Top-Biased Key (100% Untouched Wall)
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    ax2.plot(*inner_wall_poly.exterior.xy, color='#d32f2f', lw=2.2, label='100% UNTOUCHED Inner Wall (1.20mm everywhere)')
    
    socket_b = box(cx - 2.50/2, -13.80 - 0.25, cx + 2.50/2, -11.40 + 0.25)
    key_b = box(cx - 2.00/2, -13.80, cx + 2.00/2, -11.40)
    slit_b = box(cx - 1.20/2, cy - 3.20/2, cx + 1.20/2, cy + 3.20/2)
    
    ax2.fill(*socket_b.exterior.xy, color='#c8e6c9', edgecolor='#2e7d32', lw=2.0, label='Top-Biased Socket (2.50x2.90mm)')
    ax2.fill(*key_b.exterior.xy, color='#ba68c8', alpha=0.65, edgecolor='#6a1b9a', lw=1.8, label='Top-Biased Key (2.00x2.40mm)')
    ax2.fill(*blade.exterior.xy, color='#ffd54f', edgecolor='#f57f17', lw=1.8, label='Brass Contact Blade (0.77x3.10mm)')
    ax2.plot(*slit_b.exterior.xy, color='#0288d1', ls='--', lw=1.5, label='Slit Hole (1.20x3.20mm)')
    
    ax2.annotate('Key on Open Floor (Y >= -13.8mm)\nZero Wall Cuts Needed Anywhere!', xy=(8.453, -12.4), xytext=(1.8, -11.0),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=8.0, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax2.annotate('1-Way Polarization:\nInsert cannot be installed backwards!', xy=(cx, -11.6), xytext=(10.0, -10.5),
                 arrowprops=dict(arrowstyle='->', color='#6a1b9a', lw=1.4), fontsize=7.5, fontweight='bold', color='#6a1b9a',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#6a1b9a'))
                 
    ax2.set_xlim(1.5, 14.5)
    ax2.set_ylim(-19.5, -9.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('Approach B: Modify ONLY Insert Key\n(100% Untouched Wall + Polarized Key)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.legend(loc='lower left', fontsize=7.5)
    
    plt.tight_layout()
    out_testing = os.path.join(os.path.dirname(__file__), 'key_modification_comparison.png')
    plt.savefig(out_testing, dpi=220)
    print(f"Saved comparison to: {out_testing}")
    
    artifact_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\f3d4a0c2-757f-4d9a-9b44-08845cae7d7f"
    if os.path.exists(artifact_dir):
        out_artifact = os.path.join(artifact_dir, 'key_modification_comparison.png')
        shutil.copy(out_testing, out_artifact)
        print(f"Copied to artifact directory: {out_artifact}")

if __name__ == '__main__':
    generate_comparison()
