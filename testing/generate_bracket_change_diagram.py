"""
testing/generate_bracket_change_diagram.py
Generates a polished, high-resolution visual comparison diagram of all bracket tolerance changes:
- Panel 1: Full Housing Overview with Highlighted Bracket Envelopes
- Panel 2: Left Bracket Pair (Brackets 1 & 2) Before vs After with Overlaid Brass Part
- Panel 3: Right Bracket Pair (Brackets 3 & 4) Before vs After with Overlaid Brass Part
"""
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK, create_arch_wall_poly,
    create_center_curved_feature_poly
)

# Proposed Looser Coordinates
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

def generate_diagram():
    fig, axes = plt.subplots(1, 3, figsize=(25, 9.5), dpi=200, facecolor='#ffffff')
    plt.subplots_adjust(left=0.04, right=0.97, top=0.90, bottom=0.08, wspace=0.22)
    
    # --------------------------------------------------------------------------
    # Panel 1: Full Baseplate Housing Context
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_facecolor('#fafafa')
    
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    bx, by = outer_body_poly.exterior.xy
    ax1.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Wall (6.77mm H)')
    
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        ax1.plot(ix, iy, color='#d32f2f', lw=1.5)
        
    arch_poly = create_arch_wall_poly()
    ax1.plot(*arch_poly.exterior.xy, color='#0d47a1', lw=1.8, label='Center U-Arch Wall')
    
    curved_poly = create_center_curved_feature_poly()
    for geom in (curved_poly.geoms if hasattr(curved_poly, 'geoms') else [curved_poly]):
        ax1.fill(*geom.exterior.xy, color='#ce93d8', alpha=0.5)
        ax1.plot(*geom.exterior.xy, color='#8e24aa', lw=1.5, label='Center Curved Feature')
        
    p1_new = Polygon(b1_looser_pts)
    p2_new = Polygon(b2_looser_pts)
    p3_new = Polygon(b3_looser_pts)
    p4_new = Polygon(b4_looser_pts)
    
    ax1.fill(*p1_new.exterior.xy, color='#1976d2', alpha=0.35)
    ax1.plot(*p1_new.exterior.xy, color='#0d47a1', lw=2)
    
    ax1.fill(*p2_new.exterior.xy, color='#388e3c', alpha=0.35)
    ax1.plot(*p2_new.exterior.xy, color='#1b5e20', lw=2)
    
    ax1.fill(*p3_new.exterior.xy, color='#388e3c', alpha=0.35)
    ax1.plot(*p3_new.exterior.xy, color='#1b5e20', lw=2)
    
    ax1.fill(*p4_new.exterior.xy, color='#1976d2', alpha=0.35)
    ax1.plot(*p4_new.exterior.xy, color='#0d47a1', lw=2)
    
    # Highlight Zoom Envelopes
    rect_left = patches.Rectangle((-11.5, -8.0), 10.5, 16.0, fill=False, ec='#e65100', lw=2.2, ls='--')
    rect_right = patches.Rectangle((1.0, -8.0), 10.5, 16.0, fill=False, ec='#e65100', lw=2.2, ls='--')
    ax1.add_patch(rect_left)
    ax1.add_patch(rect_right)
    
    ax1.text(-6.28, 9.0, 'Left Bracket Pair\n(Panel 2 Zoom)', color='#e65100', fontweight='bold', ha='center', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.25', fc='#fff3e0', ec='#e65100', lw=1))
    ax1.text(6.28, 9.0, 'Right Bracket Pair\n(Panel 3 Zoom)', color='#e65100', fontweight='bold', ha='center', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.25', fc='#fff3e0', ec='#e65100', lw=1))
    
    ax1.set_xlim(-24, 24)
    ax1.set_ylim(-22, 23)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('1. Housing Overview & Bracket Envelopes', fontsize=12.5, fontweight='bold', pad=10)
    ax1.set_xlabel('X (mm)', fontsize=10.5)
    ax1.set_ylabel('Y (mm)', fontsize=10.5)
    ax1.legend(loc='lower left', fontsize=8.5)
    
    # --------------------------------------------------------------------------
    # Panel 2: Left Bracket Pair (Brackets 1 & 2) Detailed Tolerance Comparison
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_facecolor('#ffffff')
    
    p1_orig = Polygon(bracket_1_raw_pts)
    p2_orig = Polygon(bracket_2_raw_pts)
    
    # 1. Overlay OEM Brass Part Nominal Envelope (Gold)
    brass_left_rect = patches.Rectangle((-6.28 - 3.37, -5.80), 6.74, 11.80,
                                        facecolor='#ffd54f', alpha=0.35, edgecolor='#f57f17', lw=2.0, ls='-', label='OEM Brass Contact (6.74mm W)')
    ax2.add_patch(brass_left_rect)
    
    # 2. Previous geometry (dashed red)
    ax2.plot(*p1_orig.exterior.xy, color='#d32f2f', ls='--', lw=2.0, alpha=0.8, label='Previous Tight Bracket (6.86mm Gap)')
    ax2.plot(*p2_orig.exterior.xy, color='#d32f2f', ls='--', lw=2.0, alpha=0.8)
    
    # 3. New looser geometry (solid green/blue fill)
    ax2.fill(*p1_new.exterior.xy, color='#1976d2', alpha=0.18)
    ax2.plot(*p1_new.exterior.xy, color='#0d47a1', lw=2.5, label='Updated Looser Bracket (7.16mm Gap)')
    
    ax2.fill(*p2_new.exterior.xy, color='#388e3c', alpha=0.18)
    ax2.plot(*p2_new.exterior.xy, color='#1b5e20', lw=2.5)
    
    # Dimension Callouts:
    # A. Spine width delta
    ax2.annotate('', xy=(-9.857, 0.5), xytext=(-2.701, 0.5),
                 arrowprops=dict(arrowstyle='<->', color='#0d47a1', lw=2.2))
    ax2.text((-9.857 + -2.701)/2, 0.8, 'Spine Channel: 6.86mm → 7.16mm (+0.30mm)\n[+0.42mm Clearance vs 6.74mm Brass]',
             ha='center', va='bottom', color='#0d47a1', fontweight='bold', fontsize=8.5,
             bbox=dict(boxstyle='round,pad=0.25', fc='#e3f2fd', ec='#0d47a1', lw=1))
    
    # B. Top entrance throat delta
    ax2.annotate('', xy=(-8.000, 4.95), xytext=(-4.500, 4.95),
                 arrowprops=dict(arrowstyle='<->', color='#e65100', lw=2.0))
    ax2.text((-8.000 + -4.500)/2, 5.3, 'Top Throat: 3.18mm → 3.50mm (+0.32mm)',
             ha='center', va='bottom', color='#e65100', fontweight='bold', fontsize=8,
             bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100', lw=0.8))
    
    # C. Pocket top delta
    ax2.annotate('Pocket Ceiling:\nY=6.25 → 6.40mm (+0.15mm)', xy=(-9.4, 6.4), xytext=(-12.3, 7.5),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5),
                 fontsize=8, fontweight='bold', color='#1b5e20',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32', lw=0.8))
    
    # D. Bottom step delta
    ax2.annotate('Bottom Ledge: Y=-6.09 → -6.20mm\nOpening: 3.46mm → 3.80mm (+0.34mm)', xy=(-4.35, -6.20), xytext=(-8.0, -7.5),
                 arrowprops=dict(arrowstyle='->', color='#c2185b', lw=1.5),
                 fontsize=8, fontweight='bold', color='#880e4f',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#fce4ec', ec='#c2185b', lw=0.8))
    
    ax2.set_xlim(-12.8, 0.2)
    ax2.set_ylim(-9.8, 9.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('2. Left Bracket Pair (Brackets 1 & 2): Neutral Contact', fontsize=12.5, fontweight='bold', pad=10)
    ax2.set_xlabel('X (mm)', fontsize=10.5)
    ax2.set_ylabel('Y (mm)', fontsize=10.5)
    ax2.legend(loc='lower left', fontsize=8.0)
    
    # --------------------------------------------------------------------------
    # Panel 3: Right Bracket Pair (Brackets 3 & 4) Detailed Tolerance Comparison
    # --------------------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_facecolor('#ffffff')
    
    p3_orig = Polygon(bracket_3_raw_pts)
    p4_orig = Polygon(bracket_4_raw_pts)
    
    # 1. Overlay OEM Brass Part Nominal Envelope (Gold)
    brass_right_rect = patches.Rectangle((6.28 - 3.37, -5.80), 6.74, 11.80,
                                         facecolor='#ffd54f', alpha=0.35, edgecolor='#f57f17', lw=2.0, ls='-', label='OEM Brass Contact (6.74mm W)')
    ax3.add_patch(brass_right_rect)
    
    # 2. Previous geometry (dashed red)
    ax3.plot(*p3_orig.exterior.xy, color='#d32f2f', ls='--', lw=2.0, alpha=0.8, label='Previous Tight Bracket (6.86mm Gap)')
    ax3.plot(*p4_orig.exterior.xy, color='#d32f2f', ls='--', lw=2.0, alpha=0.8)
    
    # 3. New looser geometry (solid green/blue fill)
    ax3.fill(*p3_new.exterior.xy, color='#388e3c', alpha=0.18)
    ax3.plot(*p3_new.exterior.xy, color='#1b5e20', lw=2.5, label='Updated Looser Bracket (7.16mm Gap)')
    
    ax3.fill(*p4_new.exterior.xy, color='#1976d2', alpha=0.18)
    ax3.plot(*p4_new.exterior.xy, color='#0d47a1', lw=2.5)
    
    # Dimension Callouts:
    # A. Spine width delta
    ax3.annotate('', xy=(2.701, 0.5), xytext=(9.857, 0.5),
                 arrowprops=dict(arrowstyle='<->', color='#0d47a1', lw=2.2))
    ax3.text((2.701 + 9.857)/2, 0.8, 'Spine Channel: 6.86mm → 7.16mm (+0.30mm)\n[+0.42mm Clearance vs 6.74mm Brass]',
             ha='center', va='bottom', color='#0d47a1', fontweight='bold', fontsize=8.5,
             bbox=dict(boxstyle='round,pad=0.25', fc='#e3f2fd', ec='#0d47a1', lw=1))
    
    # B. Top entrance throat delta
    ax3.annotate('', xy=(4.500, 4.95), xytext=(8.000, 4.95),
                 arrowprops=dict(arrowstyle='<->', color='#e65100', lw=2.0))
    ax3.text((4.500 + 8.000)/2, 5.3, 'Top Throat: 3.15mm → 3.50mm (+0.35mm)',
             ha='center', va='bottom', color='#e65100', fontweight='bold', fontsize=8,
             bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100', lw=0.8))
    
    # C. Pocket top delta
    ax3.annotate('Pocket Ceiling:\nY=6.25 → 6.40mm (+0.15mm)', xy=(3.15, 6.4), xytext=(0.5, 7.5),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5),
                 fontsize=8, fontweight='bold', color='#1b5e20',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32', lw=0.8))
    
    # D. Bottom step delta
    ax3.annotate('Bottom Ledge: Y=-6.09 → -6.20mm\nOpening: 3.46mm → 3.80mm (+0.34mm)', xy=(8.15, -6.20), xytext=(3.8, -7.5),
                 arrowprops=dict(arrowstyle='->', color='#c2185b', lw=1.5),
                 fontsize=8, fontweight='bold', color='#880e4f',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#fce4ec', ec='#c2185b', lw=0.8))
    
    ax3.set_xlim(-0.2, 12.8)
    ax3.set_ylim(-9.8, 9.0)
    ax3.set_aspect('equal')
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.set_title('3. Right Bracket Pair (Brackets 3 & 4): Hot Contact', fontsize=12.5, fontweight='bold', pad=10)
    ax3.set_xlabel('X (mm)', fontsize=10.5)
    ax3.set_ylabel('Y (mm)', fontsize=10.5)
    ax3.legend(loc='lower right', fontsize=8.0)
    
    out_testing = os.path.join(os.path.dirname(__file__), 'bracket_change_diagram.png')
    plt.savefig(out_testing, dpi=200)
    print(f"Saved diagram to: {out_testing}")
    
    # Copy to artifact directory
    artifact_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\f3d4a0c2-757f-4d9a-9b44-08845cae7d7f"
    if os.path.exists(artifact_dir):
        out_artifact = os.path.join(artifact_dir, 'bracket_change_diagram.png')
        shutil.copy(out_testing, out_artifact)
        print(f"Copied diagram to artifact directory: {out_artifact}")

if __name__ == '__main__':
    generate_diagram()
