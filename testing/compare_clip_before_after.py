"""
Compare snap clip geometry Before vs After:
- Before: CLIP_HOOK_HEIGHT = 1.80mm (Shelf Z = 4.97mm), CLIP_HOOK_DEPTH = 1.85mm
- After:  CLIP_HOOK_HEIGHT = 2.05mm (Shelf Z = 4.72mm), CLIP_HOOK_DEPTH = 1.75mm
Saves diagnostic comparison diagram in testing/clip_before_after_comparison.png
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, FancyArrowPatch
from shapely.geometry import LineString
import trimesh

import build_part

def generate_comparison_diagram():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5), dpi=300)
    
    # -------------------------------------------------------------
    # Panel 1: R-Z Cross-Section Overlay (Before vs After)
    # -------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_title("Panel A: Radial Cross-Section Overlay (R-Z)", fontsize=11, fontweight='bold', pad=12)
    
    wall_t = 1.20 # mm
    wall_top_z = 6.77 # mm
    blunt_h = 0.53 # mm
    
    # Before parameters
    shelf_z_before = 4.97
    depth_before = 1.85
    ramp_bot_z_before = shelf_z_before + blunt_h # 5.50 mm
    
    # After parameters
    shelf_z_after = 4.72
    depth_after = 1.75
    ramp_bot_z_after = shelf_z_after + blunt_h # 5.25 mm
    
    # Wall stem outline: from Z=2.0 to Z=6.77
    stem_inner_r = -wall_t
    stem_outer_r = 0.0
    
    # Draw Wall beam
    ax1.fill_between([stem_inner_r, stem_outer_r], 2.0, wall_top_z, color='#cfd8dc', alpha=0.6, label='Outer Wall Stem (t=1.20mm)')
    ax1.plot([stem_inner_r, stem_inner_r], [2.0, wall_top_z], 'k-', lw=1.5)
    ax1.plot([stem_outer_r, stem_outer_r], [2.0, wall_top_z], 'k--', lw=1.0)
    
    # Before Hook Profile (Red dashed)
    # Profile: (0, 4.97) -> (1.85, 4.97) -> (1.85, 5.50) -> (0, 6.77)
    pts_before = np.array([
        [stem_outer_r, shelf_z_before],
        [depth_before, shelf_z_before],
        [depth_before, ramp_bot_z_before],
        [stem_outer_r, wall_top_z]
    ])
    poly_before = MplPolygon(pts_before, closed=True, facecolor='#ffcdd2', edgecolor='#d32f2f', linestyle='--', lw=2.0, alpha=0.45, label='BEFORE: Shelf Z=4.97mm, Depth=1.85mm')
    ax1.add_patch(poly_before)
    
    # After Hook Profile (Green solid)
    # Profile: (0, 4.72) -> (1.75, 4.72) -> (1.75, 5.25) -> (0, 6.77)
    pts_after = np.array([
        [stem_outer_r, shelf_z_after],
        [depth_after, shelf_z_after],
        [depth_after, ramp_bot_z_after],
        [stem_outer_r, wall_top_z]
    ])
    poly_after = MplPolygon(pts_after, closed=True, facecolor='#c8e6c9', edgecolor='#2e7d32', linestyle='-', lw=2.5, alpha=0.65, label='AFTER: Shelf Z=4.72mm, Depth=1.75mm')
    ax1.add_patch(poly_after)
    
    # Dimension Callouts
    # 1. Under-shelf material addition (+0.25mm)
    ax1.annotate('', xy=(-0.15, shelf_z_after), xytext=(-0.15, shelf_z_before),
                 arrowprops=dict(arrowstyle='<->', color='#b71c1c', lw=1.5))
    ax1.text(-0.65, (shelf_z_before + shelf_z_after)/2.0, "+0.25mm\nUnder Shelf", color='#b71c1c', fontsize=8.5, fontweight='bold', va='center', ha='center', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#b71c1c', lw=1.0))
    
    # 2. Shelf Z lines
    ax1.axhline(shelf_z_before, color='#d32f2f', linestyle=':', lw=1.2, xmin=0.35, xmax=0.85)
    ax1.text(depth_before + 0.1, shelf_z_before, f"Z = {shelf_z_before:.2f}mm", color='#d32f2f', fontsize=8, va='center', fontweight='bold')
    
    ax1.axhline(shelf_z_after, color='#2e7d32', linestyle=':', lw=1.2, xmin=0.35, xmax=0.82)
    ax1.text(depth_after + 0.1, shelf_z_after, f"Z = {shelf_z_after:.2f}mm", color='#2e7d32', fontsize=8, va='center', fontweight='bold')
    
    # 3. Face trimming (-0.10mm)
    ax1.annotate('', xy=(depth_after, 5.37), xytext=(depth_before, 5.37),
                 arrowprops=dict(arrowstyle='<->', color='#1565c0', lw=1.5))
    ax1.text((depth_before + depth_after)/2.0, 5.75, "-0.10mm\nFace Trim", color='#1565c0', fontsize=8.5, fontweight='bold', va='bottom', ha='center', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1565c0', lw=1.0))
    
    # 4. Lead-in Ramp Angle Callouts
    # Before ramp angle: atan(1.85 / 1.27) = 55.5 deg from vertical
    # After ramp angle: atan(1.75 / 1.52) = 49.0 deg from vertical
    ax1.text(0.70, 6.25, "Ramp Angle:\nBefore: 55.5°\nAfter: 49.0° (-6.5°)\nSmoother Entry!", fontsize=8.5, fontweight='bold', color='#004d40', bbox=dict(boxstyle='round,pad=0.3', fc='#e0f2f1', ec='#00796b'))
    
    # 5. Mating Catch Ledge depiction
    mating_z = 4.47 # hypothetical fully seated catch ledge showing the gap
    ax1.fill_between([0.2, 2.3], 3.8, mating_z, color='#fff9c4', edgecolor='#f57f17', linestyle='--', lw=1.2, alpha=0.5, label='Mating Housing Catch Ledge')
    ax1.annotate(f'Remaining Play: ~0.25mm\n(Eliminated half of ~0.5mm gap)', xy=(1.0, (shelf_z_after + mating_z)/2.0), xytext=(1.2, 3.2),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='#e65100'),
                 fontsize=8, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#e65100'))
    
    ax1.set_xlim(-1.6, 2.6)
    ax1.set_ylim(2.5, 7.3)
    ax1.set_xlabel("Radial Position R (mm) [0 = Stem Outer Face]", fontsize=9, fontweight='bold')
    ax1.set_ylabel("Elevation Z (mm)", fontsize=9, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=7.5)
    
    # -------------------------------------------------------------
    # Panel 2: Top-Down Hook Crown Profile (XY Plane)
    # -------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_title("Panel B: Top-Down Crowned Hook Edge (XY Plane)", fontsize=11, fontweight='bold', pad=12)
    
    w_arm = 4.20
    t_tang = np.linspace(-w_arm/2.0, w_arm/2.0, 100)
    ease = 0.20
    
    depth_profile_before = depth_before - ease * ((abs(t_tang) / (w_arm / 2.0)) ** 2.0)
    depth_profile_after  = depth_after  - ease * ((abs(t_tang) / (w_arm / 2.0)) ** 2.0)
    
    ax2.plot(t_tang, np.zeros_like(t_tang), 'k-', lw=2.0, label='Clip Wall Beam Outer Face (R=0)')
    ax2.fill_between(t_tang, -1.2, 0, color='#cfd8dc', alpha=0.6, label='Beam Wall (t=1.20mm)')
    
    ax2.plot(t_tang, depth_profile_before, color='#d32f2f', linestyle='--', lw=2.0, label=f'BEFORE: Center={depth_before:.2f}mm, Edge={depth_before-ease:.2f}mm')
    ax2.fill_between(t_tang, 0, depth_profile_before, color='#ffcdd2', alpha=0.35)
    
    ax2.plot(t_tang, depth_profile_after, color='#2e7d32', linestyle='-', lw=2.5, label=f'AFTER: Center={depth_after:.2f}mm, Edge={depth_after-ease:.2f}mm')
    ax2.fill_between(t_tang, 0, depth_profile_after, color='#c8e6c9', alpha=0.55)
    
    # Annotation on apex and corners
    ax2.annotate(f'Center Apex:\n1.85mm → 1.75mm\n(-0.10mm)', xy=(0.0, depth_after), xytext=(0.0, 1.0),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='#1b5e20'),
                 fontsize=8.5, fontweight='bold', color='#1b5e20', ha='center', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#2e7d32'))
    
    ax2.annotate(f'Edge Relief:\n1.65mm → 1.55mm', xy=(1.9, depth_after - ease*0.8), xytext=(1.2, 0.4),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='#1b5e20'),
                 fontsize=8, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#2e7d32'))
    
    ax2.set_xlim(-2.5, 2.5)
    ax2.set_ylim(-1.5, 2.4)
    ax2.set_xlabel("Tangential Width Along Beam (mm)", fontsize=9, fontweight='bold')
    ax2.set_ylabel("Radial Overhang Beyond Wall (mm)", fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='lower left', fontsize=7.5)
    
    # -------------------------------------------------------------
    # Panel 3: Key Engineering Metrics Table & Summary
    # -------------------------------------------------------------
    ax3 = axes[2]
    ax3.axis('off')
    ax3.set_title("Panel C: Comprehensive Engineering Specification", fontsize=11, fontweight='bold', pad=12)
    
    table_data = [
        ["Parameter", "Before", "After (New)", "Delta / Functional Impact"],
        ["Shelf Elevation (stem_h)", "4.97 mm", "4.72 mm", "-0.25 mm (adds +0.25mm material under clip)"],
        ["Under-Clip Clearance Gap", "~0.50 mm", "~0.25 mm", "50% gap reduction; positive switch engagement"],
        ["Radial Hook Depth (Center)", "1.85 mm", "1.75 mm", "-0.10 mm (-5.4% deflection & insertion force)"],
        ["Radial Hook Depth (Corners)", "1.65 mm", "1.55 mm", "-0.10 mm (smooth non-binding entry)"],
        ["Hook Height in Z", "1.80 mm", "2.05 mm", "+0.25 mm (sturdier undercut retention ledge)"],
        ["Vertical Blunt Apex Land", "0.53 mm", "0.53 mm", "0.00 mm (preserved anti-fragility face)"],
        ["Lead-in Ramp Z Span", "1.27 mm", "1.52 mm", "+0.25 mm (+19.7% longer lead-in slope)"],
        ["Lead-in Ramp Angle", "55.5°", "49.0°", "-6.5° (shallower angle = easier entry)"],
        ["Flex Slot Depth (CLIP_GAP_DEPTH)", "3.70 mm", "3.70 mm", "Option A preserved (2.07mm hoop ring)"],
        ["Free Stem Below Hook", "1.90 mm", "1.65 mm", "Balanced flex with reduced required strain"],
        ["45° Support Top Datum", "Z = 4.69 mm", "Z = 4.44 mm", "Preserves calibrated 0.28mm release gap"]
    ]
    
    tbl = ax3.table(cellText=table_data, loc='center', cellLoc='left', colWidths=[0.32, 0.16, 0.18, 0.34])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1.0, 1.55)
    
    # Style header row
    for col in range(4):
        tbl[(0, col)].set_facecolor('#37474f')
        tbl[(0, col)].get_text().set_color('white')
        tbl[(0, col)].get_text().set_fontweight('bold')
        
    # Style alternating rows
    for row in range(1, len(table_data)):
        bg = '#f5f5f5' if row % 2 == 1 else '#ffffff'
        if row == 1:
            bg = '#e8f5e9' # Highlight shelf change
        elif row == 3:
            bg = '#e1f5fe' # Highlight depth change
        elif row == 8:
            bg = '#fff3e0' # Highlight ramp angle
        for col in range(4):
            tbl[(row, col)].set_facecolor(bg)
            
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), 'clip_before_after_comparison.png')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Saved direct comparison diagram to: {output_path}")

if __name__ == '__main__':
    generate_comparison_diagram()
