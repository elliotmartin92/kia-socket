"""
testing/compare_straight_cam_options.py
Models and compares Option 1 (Direct Belly Entry, Z ~ 7mm) vs Option 2 (Upper Throat Direct Ramp, Z ~ 11mm)
Both use 100% direct, straight, thick heavy-duty beams (zero arched flimsy necks).
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, PIN_LEN,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    RIB_FLANK_THICK, HOLE_X_CENTER, X_TOWER_CENTER
)
from testing.model_exact_brass_part import get_brass_contact_2d_profile, D1A, D1B, D2, D4, D5, D3, SHEET_THICK

def get_option1_belly_cam_poly():
    """Option 1: Direct straight thick beam sloping down into the 5.0mm belly cavity (Z in [4.5, 7.5] mm)."""
    r_hub = HUB_DIAMETER / 2.0
    # From hub (9.28, 12.59) sloping down to belly (2.50, 7.00)
    # 2.80 mm thick solid beam
    pts = [
        (Y_AXLE, Z_AXLE + r_hub),          # (9.28, 14.69)
        (Y_AXLE + 1.20, Z_AXLE + 1.00),
        (3.50, 8.80),                      # Top ramp
        (1.50, 7.00),                      # Contact tip inside 5.0mm belly
        (2.00, 5.00),                      # Bottom nose inside belly
        (4.50, 5.50),                      # Underside
        (Y_AXLE - 0.50, Z_AXLE - 2.50),
        (Y_AXLE - 1.50, Z_AXLE)
    ]
    return np.array(pts)

def get_option2_upper_throat_cam_poly():
    """Option 2: Direct straight thick beam reaching forward into upper funnel (Z in [10.5, 13.0] mm)."""
    r_hub = HUB_DIAMETER / 2.0
    # From hub (9.28, 12.59) reaching directly forward to (2.50, 11.50)
    # 3.00 mm thick solid beam
    pts = [
        (Y_AXLE, Z_AXLE + r_hub),          # (9.28, 14.69)
        (7.00, 14.50),
        (3.00, 13.20),                     # Top ramp
        (1.80, 11.50),                     # Contact nose in upper funnel
        (2.20, 9.80),                      # Bottom nose above throat (Z=9.4mm)
        (5.00, 10.20),                     # Underside
        (Y_AXLE - 1.00, Z_AXLE - 1.50),
        (Y_AXLE - 1.50, Z_AXLE)
    ]
    return np.array(pts)

def run():
    print("=== DIRECT STRAIGHT CAM DESIGN: OPTION 1 VS OPTION 2 ===")
    
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    t_half = SHEET_THICK / 2.0
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    
    poly_opt1 = get_option1_belly_cam_poly()
    poly_opt2 = get_option2_upper_throat_cam_poly()
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 10), facecolor='#1a1a1a', dpi=180)
    
    # -------------------------------------------------------------
    # Option 1: Direct Belly-Entry Cam
    # -------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_facecolor('#222222')
    ax1.set_title("Option 1: Direct Straight Cam into 5.0mm Belly Cavity", color='#00d2ff', fontsize=12, weight='bold')
    
    ax1.add_patch(patches.Rectangle((-4, 0), 18, 1.0, facecolor='#666666', alpha=0.4, label='Floor (Z=1.00mm)'))
    ax1.add_patch(patches.Polygon(f_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.5, label='Brass Contact'))
    ax1.add_patch(patches.Polygon(r_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.5))
    ax1.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.4, edgecolor='#d35400', lw=1.5, label='Hub (Ø4.20mm)'))
    
    # Draw Option 1 Poly
    ax1.add_patch(patches.Polygon(poly_opt1, facecolor='#00d2ff', alpha=0.7, edgecolor='#0984e3', lw=2, label='Option 1 Cam (Solid 2.8mm Beam)'))
    
    # Draw Blade
    ax1.add_patch(patches.Rectangle((y_blade_c - 0.76, 7.0), 1.52, 12.0, color='#ffffff', alpha=0.3, edgecolor='white', linestyle='--', label='Plug Blade Path'))
    
    ax1.annotate('Direct Straight Beam\n(Solid 2.80 mm thick)\nZero flimsy arches!',
                 xy=(5.5, 9.5), xytext=(8.0, 6.0),
                 color='#00d2ff', fontsize=9, weight='bold', ha='center',
                 arrowprops=dict(arrowstyle='->', color='#00d2ff', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#002233', edgecolor='#00d2ff'))
    
    ax1.annotate('Cam tip sits inside\n5.0 mm wide Belly Cavity\n(Below Z=9.4mm throat)',
                 xy=(1.5, 7.0), xytext=(-2.0, 9.0),
                 color='#00d2ff', fontsize=9, weight='bold', ha='center',
                 arrowprops=dict(arrowstyle='->', color='#00d2ff', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#002233', edgecolor='#00d2ff'))
    
    ax1.set_xlim(-4, 14)
    ax1.set_ylim(0, 18)
    ax1.set_xlabel('Y (mm)', color='white')
    ax1.set_ylabel('Z (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # -------------------------------------------------------------
    # Option 2: Direct Upper-Throat Cam
    # -------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_facecolor('#222222')
    ax2.set_title("Option 2: Direct Straight Cam in Upper Lead-In Funnel", color='#2ecc71', fontsize=12, weight='bold')
    
    ax2.add_patch(patches.Rectangle((-4, 0), 18, 1.0, facecolor='#666666', alpha=0.4, label='Floor (Z=1.00mm)'))
    ax2.add_patch(patches.Polygon(f_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.5, label='Brass Contact'))
    ax2.add_patch(patches.Polygon(r_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.5))
    ax2.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.4, edgecolor='#d35400', lw=1.5, label='Hub (Ø4.20mm)'))
    
    # Draw Option 2 Poly
    ax2.add_patch(patches.Polygon(poly_opt2, facecolor='#2ecc71', alpha=0.7, edgecolor='#27ae60', lw=2, label='Option 2 Cam (Solid 3.0mm Beam)'))
    
    # Draw Blade
    ax2.add_patch(patches.Rectangle((y_blade_c - 0.76, 11.5), 1.52, 12.0, color='#ffffff', alpha=0.3, edgecolor='white', linestyle='--', label='Plug Blade Path'))
    
    ax2.annotate('Short, Ultra-Rigid Straight Beam\n(Solid 3.00 mm thick)\nMaximum torsional stiffness!',
                 xy=(5.5, 13.0), xytext=(8.0, 16.0),
                 color='#2ecc71', fontsize=9, weight='bold', ha='center',
                 arrowprops=dict(arrowstyle='->', color='#2ecc71', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#003311', edgecolor='#2ecc71'))
    
    ax2.annotate('Hits cam in Upper Funnel\nBEFORE entering pinch throat\n(Early switch activation)',
                 xy=(1.8, 11.5), xytext=(-2.0, 13.5),
                 color='#2ecc71', fontsize=9, weight='bold', ha='center',
                 arrowprops=dict(arrowstyle='->', color='#2ecc71', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#003311', edgecolor='#2ecc71'))
    
    ax2.set_xlim(-4, 14)
    ax2.set_ylim(0, 18)
    ax2.set_xlabel('Y (mm)', color='white')
    ax2.set_ylabel('Z (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    ax2.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "direct_straight_cam_comparison.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved direct straight cam comparison diagram to: {out_png}")

if __name__ == '__main__':
    run()
