"""
Generates a detailed 3-panel engineering diagram:
Panel 1: Top Snap Clips (45°, 135°) R-Z cross-section showing shelf lowered to Z=3.97mm (-0.75mm SIM tool gap closure).
Panel 2: Bottom Snap Clips (211.3°, 327.5°) R-Z cross-section showing shelf lowered to Z=4.35mm (-0.37mm gap closure) and 1.85mm depth.
Panel 3: 3-Prong Trident Anti-Sag Support layout directly under the hook apex with 0.23mm release gap.
Saves to testing/clip_calibration_inspection.png.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

def generate_plot():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.2), dpi=300)
    
    wall_t = 1.20
    wall_top_z = 6.77
    blunt_h = 0.53
    
    # -------------------------------------------------------------
    # Panel 1: Top Clips (45°, 135°)
    # -------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_title("Panel A: Top Clips (45.0°, 135.0°)\nShelf Z: 4.72mm → 3.97mm (-0.75mm SIM Gap Closed)", fontsize=10.5, fontweight='bold', pad=10)
    
    # Stem wall
    ax1.fill_between([-wall_t, 0], 1.5, wall_top_z, color='#cfd8dc', alpha=0.6, label='Outer Wall Stem (t=1.20mm)')
    ax1.plot([-wall_t, -wall_t], [1.5, wall_top_z], 'k-', lw=1.5)
    ax1.plot([0, 0], [1.5, wall_top_z], 'k--', lw=1.0)
    
    # Before Hook (Z=4.72mm, depth=1.80mm)
    pts_before = np.array([
        [0.0, 4.72],
        [1.80, 4.72],
        [1.80, 4.72 + blunt_h],
        [0.0, wall_top_z]
    ])
    poly_before = MplPolygon(pts_before, closed=True, facecolor='#ffcdd2', edgecolor='#d32f2f', linestyle='--', lw=2.0, alpha=0.45, label='Previous: Shelf Z=4.72mm (SIM Gap)')
    ax1.add_patch(poly_before)
    
    # After Hook (Z=3.97mm, depth=1.80mm)
    pts_after_top = np.array([
        [0.0, 3.97],
        [1.80, 3.97],
        [1.80, 3.97 + blunt_h],
        [0.0, wall_top_z]
    ])
    poly_after_top = MplPolygon(pts_after_top, closed=True, facecolor='#c8e6c9', edgecolor='#2e7d32', linestyle='-', lw=2.5, alpha=0.65, label='Calibrated: Shelf Z=3.97mm (Tight Seating)')
    ax1.add_patch(poly_after_top)
    
    # Annotations
    ax1.annotate('', xy=(-0.15, 3.97), xytext=(-0.15, 4.72),
                 arrowprops=dict(arrowstyle='<->', color='#b71c1c', lw=1.5))
    ax1.text(-0.65, (3.97 + 4.72)/2.0, "-0.75mm\n(SIM Gap\nClosed)", color='#b71c1c', fontsize=8, fontweight='bold', va='center', ha='center', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#b71c1c'))
    
    ax1.axhline(4.72, color='#d32f2f', linestyle=':', lw=1.2, xmin=0.35, xmax=0.85)
    ax1.text(1.9, 4.72, "Z = 4.72mm", color='#d32f2f', fontsize=8, va='center', fontweight='bold')
    ax1.axhline(3.97, color='#2e7d32', linestyle=':', lw=1.2, xmin=0.35, xmax=0.85)
    ax1.text(1.9, 3.97, "Z = 3.97mm", color='#2e7d32', fontsize=8, va='center', fontweight='bold')
    
    ax1.set_xlim(-1.6, 2.7)
    ax1.set_ylim(2.0, 7.3)
    ax1.set_xlabel("Radial Position R (mm)", fontsize=9, fontweight='bold')
    ax1.set_ylabel("Elevation Z (mm)", fontsize=9, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=7.5)
    
    # -------------------------------------------------------------
    # Panel 2: Bottom Clips (211.3°, 327.5°)
    # -------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_title("Panel B: Bottom Clips (211.3°, 327.5°)\nShelf Z: 4.72mm → 4.35mm (-0.37mm Gap) | 327.5° Depth: 1.85mm", fontsize=10.5, fontweight='bold', pad=10)
    
    ax2.fill_between([-wall_t, 0], 1.5, wall_top_z, color='#cfd8dc', alpha=0.6, label='Outer Wall Stem (t=1.20mm)')
    ax2.plot([-wall_t, -wall_t], [1.5, wall_top_z], 'k-', lw=1.5)
    ax2.plot([0, 0], [1.5, wall_top_z], 'k--', lw=1.0)
    
    # Previous Hook
    ax2.add_patch(MplPolygon(pts_before, closed=True, facecolor='#ffcdd2', edgecolor='#d32f2f', linestyle='--', lw=2.0, alpha=0.45, label='Previous: Shelf Z=4.72mm'))
    
    # After Hook for 327.5° (Z=4.35mm, depth=1.85mm)
    pts_after_bot = np.array([
        [0.0, 4.35],
        [1.85, 4.35],
        [1.85, 4.35 + blunt_h],
        [0.0, wall_top_z]
    ])
    poly_after_bot = MplPolygon(pts_after_bot, closed=True, facecolor='#bbdefb', edgecolor='#1565c0', linestyle='-', lw=2.5, alpha=0.65, label='Calibrated 327.5°: Z=4.35mm, Reach=1.85mm')
    ax2.add_patch(poly_after_bot)
    
    # Support cross-section under shelf
    supp_top_z = 4.35 - 0.23 # 4.12 mm
    supp_pts = np.array([
        [-0.25, 4.35 - 1.85 - 0.35],
        [-0.25, 4.35 - 1.85 + 0.25],
        [0.0,   4.35 - 1.85 + 0.25],
        [1.85 - 0.55, supp_top_z],
        [1.85, supp_top_z],
        [1.85, supp_top_z - 0.25],
        [0.0,  4.35 - 1.85 - 0.35]
    ])
    poly_supp = MplPolygon(supp_pts, closed=True, facecolor='#fff9c4', edgecolor='#f57f17', linestyle='-', lw=1.8, alpha=0.75, label='45° Breakaway Support (Z_top=4.12mm)')
    ax2.add_patch(poly_supp)
    
    # Release gap callout
    ax2.annotate('0.23mm PC-FR\nRelease Gap', xy=(1.5, 4.235), xytext=(2.0, 3.5),
                 arrowprops=dict(arrowstyle='->', color='#e65100', lw=1.2),
                 fontsize=8, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#e65100'))
    
    ax2.annotate('-0.37mm Gap Closed\n+0.05mm Reach (1.85mm)', xy=(1.85, 4.35), xytext=(0.5, 5.5),
                 arrowprops=dict(arrowstyle='->', color='#1565c0', lw=1.2),
                 fontsize=8, fontweight='bold', color='#1565c0', bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#1565c0'))
    
    ax2.set_xlim(-1.6, 2.7)
    ax2.set_ylim(2.0, 7.3)
    ax2.set_xlabel("Radial Position R (mm)", fontsize=9, fontweight='bold')
    ax2.set_ylabel("Elevation Z (mm)", fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='lower left', fontsize=7.5)
    
    # -------------------------------------------------------------
    # Panel 3: 3-Prong Trident Anti-Sag Support Layout (Tangential View)
    # -------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_title("Panel C: Anti-Sag Trident Support Architecture\nDirect Center Apex Support Eliminates PC-FR Droop", fontsize=10.5, fontweight='bold', pad=10)
    
    half_w = bp.CLIP_ARM_WIDTH / 2.0 # 2.10mm
    t_vals = np.linspace(-half_w, half_w, 100)
    crown_profile = 1.85 - bp.CLIP_CROWN_EASE * ((abs(t_vals) / half_w) ** 2.0)
    
    # Draw hook shelf edge
    ax3.plot(t_vals, crown_profile, 'b-', lw=2.5, label='Hook Shelf Edge (Apex = 1.85mm)')
    ax3.fill_between(t_vals, 0, crown_profile, color='#bbdefb', alpha=0.35)
    ax3.axhline(0, color='k', lw=1.5, label='Outer Wall Stem Face (R=0)')
    
    # Prongs layout: Left (-1.25, 0.80), Center (0.00, 0.90), Right (1.25, 0.80)
    prongs = [
        (-1.25, 0.80, 'Left Prong\n(W=0.80mm)'),
        ( 0.00, 0.90, 'Center Apex Prong\n(W=0.90mm) [NEW]'),
        ( 1.25, 0.80, 'Right Prong\n(W=0.80mm)')
    ]
    for yo, pw, lbl in prongs:
        x_l = yo - pw/2.0
        x_r = yo + pw/2.0
        # support land depth
        depth_prong = 1.85 - bp.CLIP_CROWN_EASE * ((abs(yo) / half_w) ** 2.0)
        ax3.fill_between([x_l, x_r], depth_prong - 0.55, depth_prong, color='#ffe082', edgecolor='#f57f17', lw=1.5, alpha=0.85)
        ax3.text(yo, (depth_prong - 0.275), lbl, ha='center', va='center', fontsize=7, fontweight='bold', color='#e65100')
        
    ax3.annotate('Direct Support Under Apex!\n(Zero Sagging Across Center)', xy=(0.0, 1.85), xytext=(0.0, 1.0),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5),
                 ha='center', fontsize=8.5, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round,pad=0.25', fc='#e8f5e9', ec='#2e7d32'))
    
    ax3.set_xlim(-2.5, 2.5)
    ax3.set_ylim(-0.2, 2.2)
    ax3.set_xlabel("Tangential Width Along Beam (mm)", fontsize=9, fontweight='bold')
    ax3.set_ylabel("Radial Overhang Beyond Wall (mm)", fontsize=9, fontweight='bold')
    ax3.grid(True, linestyle=':', alpha=0.5)
    ax3.legend(loc='lower left', fontsize=7.5)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'clip_calibration_inspection.png')
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Saved calibration inspection diagram to: {out_path}")

if __name__ == '__main__':
    generate_plot()
