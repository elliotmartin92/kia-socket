"""
testing/inspect_exact_assembly_alignment.py
Plots exact CAD alignment of Baseplate, Bracket 3 & 4, Left/Right Towers, Through Hole,
Shaft Rocker, and the Brass Insert in both Top-Down (X-Y) and Side (Y-Z) views.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, PIN_LEN,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    X_TOWER_CENTER, HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    TOWER_HEIGHT, BASE_THICK
)
from testing.model_exact_brass_part import get_brass_contact_2d_profile, D1A, D1B, D2, D4, D5, D3, SHEET_THICK

def run():
    print("Inspecting exact CAD alignment...")
    
    b3_poly = to_mm_poly(bracket_3_raw_pts)
    b4_poly = to_mm_poly(bracket_4_raw_pts)
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10), facecolor='#1a1a1a', dpi=180)
    
    # --------------------------------------------------------------------------
    # Panel 1: Top-Down Plan View (X-Y Plane)
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_facecolor('#222222')
    ax1.set_title("1. Top-Down Plan View (X-Y Plane): Brackets, Towers, Through-Hole, Rocker", color='white', fontsize=12, weight='bold')
    
    # Draw Bracket 3 and 4
    ax1.add_patch(patches.Polygon(bracket_3_raw_pts, facecolor='#27ae60', alpha=0.5, edgecolor='#2ecc71', lw=1.5, label='Bracket 3 (Left)'))
    ax1.add_patch(patches.Polygon(bracket_4_raw_pts, facecolor='#27ae60', alpha=0.5, edgecolor='#2ecc71', lw=1.5, label='Bracket 4 (Right)'))
    
    # Draw Left Tower & Right Tower base bounds
    # Left Tower: X in [3.90, 5.40], Y in [6.25, 12.85]
    # Right Tower: X in [13.10, 14.60], Y in [6.25, 12.85]
    ax1.add_patch(patches.Rectangle((X_LEFT_TOWER_OUTER, 6.25), X_LEFT_TOWER_INNER - X_LEFT_TOWER_OUTER, 6.60,
                                    facecolor='#3498db', alpha=0.4, edgecolor='#2980b9', lw=1.5, label='Left Tower (X: 3.90-5.40)'))
    ax1.add_patch(patches.Rectangle((X_RIGHT_TOWER_INNER, 6.25), X_RIGHT_TOWER_OUTER - X_RIGHT_TOWER_INNER, 6.60,
                                    facecolor='#3498db', alpha=0.4, edgecolor='#2980b9', lw=1.5, label='Right Tower (X: 13.10-14.60)'))
    
    # Draw Through-Hole: X in [7.61, 12.96], Y in [8.57, 13.08]
    ax1.add_patch(patches.Rectangle((HOLE_X_CENTER - HOLE_X_WIDTH/2, HOLE_Y_CENTER - HOLE_Y_LEN/2),
                                    HOLE_X_WIDTH, HOLE_Y_LEN, facecolor='#e74c3c', alpha=0.3, edgecolor='#c0392b', lw=2, linestyle='--', label='Through-Hole Cutout'))
    
    # Draw Shaft Axle & Hub: Hub X in [5.50, 13.00], Y = Y_AXLE = 9.279 mm
    ax1.plot([X_TOWER_CENTER - TOTAL_AXLE_LEN/2, X_TOWER_CENTER + TOTAL_AXLE_LEN/2], [Y_AXLE, Y_AXLE], color='cyan', lw=3, label=f'Shaft Axle Axis (Y = {Y_AXLE:.2f}mm)')
    ax1.add_patch(patches.Rectangle((X_TOWER_CENTER - HUB_WIDTH/2, Y_AXLE - HUB_DIAMETER/2), HUB_WIDTH, HUB_DIAMETER,
                                    facecolor='#e67e22', alpha=0.4, edgecolor='#d35400', lw=1.5, label='Hub Barrel (Ø4.20mm)'))
    
    # Draw Plunger Blade: X in [8.08, 12.48], Y in [Y_AXLE, 12.50]
    ax1.add_patch(patches.Rectangle((HOLE_X_CENTER - PLUNGER_WIDTH_X/2, Y_AXLE - 1.0), PLUNGER_WIDTH_X, 3.5,
                                    facecolor='#f1c40f', alpha=0.7, edgecolor='#f39c12', lw=1.5, label='Plunger Arm (Over Through-Hole)'))
    
    # Draw Brass Insert Footprint in Bracket 3 & 4:
    # Width across X: D3 = 6.74mm (X in [2.91, 9.65])
    # Depth in Y: Front leaf to Rear leaf
    front_pts, rear_pts, y_c = get_brass_contact_2d_profile()
    y_rear_top = rear_pts[-1][0] + SHEET_THICK/2.0
    y_front_top = front_pts[-1][0] - SHEET_THICK/2.0
    ax1.add_patch(patches.Rectangle((CAM_X_CENTER - D3/2, y_front_top), D3, y_rear_top - y_front_top,
                                    facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=2, linestyle='-', label=f'Brass Insert Footprint ({D3:.2f}mm x {y_rear_top - y_front_top:.2f}mm)'))
    
    # Draw Cam Tab: X in [CAM_X_CENTER - 1.35, CAM_X_CENTER + 1.35]
    ax1.add_patch(patches.Rectangle((CAM_X_CENTER - CAM_WIDTH_X/2, 1.5), CAM_WIDTH_X, Y_AXLE - 1.5,
                                    facecolor='#00d2ff', alpha=0.7, edgecolor='#0984e3', lw=2, label=f'Rocker Cam Tab (W = {CAM_WIDTH_X:.2f}mm)'))
    
    ax1.set_xlim(-1, 17)
    ax1.set_ylim(-10, 16)
    ax1.set_xlabel('X (mm)', color='white')
    ax1.set_ylabel('Y (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='lower left', fontsize=7.5, facecolor='#1a1a1a', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 2: Side Section View (Y-Z Plane along X = 6.28mm & X = 10.28mm)
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_facecolor('#222222')
    ax2.set_title("2. Side Profile Alignment (Y-Z Plane)", color='white', fontsize=12, weight='bold')
    
    # Base Floor & Through-Hole in Y
    ax2.add_patch(patches.Rectangle((-8, 0), 24, 1.0, facecolor='#888888', alpha=0.5))
    ax2.add_patch(patches.Rectangle((HOLE_Y_CENTER - HOLE_Y_LEN/2, 0), HOLE_Y_LEN, 1.0, facecolor='#e74c3c', alpha=0.4, hatch='//', label='Through-Hole in Floor (Z: 0 to 1mm)'))
    
    # Bracket 3&4 Y span (Y in [-7.17, 7.17], Z in [1.0, 4.6])
    ax2.add_patch(patches.Rectangle((-7.17, 1.0), 14.34, 3.6, facecolor='#27ae60', alpha=0.25, edgecolor='#2ecc71', lw=1.5, label='Bracket 3&4 Y Span (Z=4.6mm)'))
    
    # Left Tower Y-Z Profile
    tower_yz = [(6.25, 1.0), (12.85, 1.0), (12.18, 14.09), (6.55, 14.09)]
    ax2.add_patch(patches.Polygon(tower_yz, facecolor='#3498db', alpha=0.3, edgecolor='#2980b9', lw=1.5, label='Tower Y-Z Profile'))
    
    # Brass Insert Y-Z Profile
    t_half = SHEET_THICK / 2.0
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    ax2.add_patch(patches.Polygon(f_poly_pts, facecolor='#f39c12', alpha=0.6, edgecolor='#d68910', lw=2, label='Brass Front Arm'))
    ax2.add_patch(patches.Polygon(r_poly_pts, facecolor='#f39c12', alpha=0.6, edgecolor='#d68910', lw=2, label='Brass Rear Arm'))
    
    # Shaft Hub & Axle
    ax2.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.5, edgecolor='#d35400', lw=1.5, label='Shaft Hub (Y=9.28, Z=12.59)'))
    
    # Plunger
    z_tip = -6.50
    r_tip = 1.00
    plunger_y_center = 10.479
    N = 25
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (Y_AXLE + HUB_DIAMETER/2) + 2*(1-t)*t * (Y_AXLE + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (Z_AXLE - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    belly_y = (1-t)**2 * (Y_AXLE - HUB_DIAMETER/2) + 2*(1-t)*t * (Y_AXLE + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (Z_AXLE - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    ax2.add_patch(patches.Polygon(pts_plunger, facecolor='#f1c40f', alpha=0.4, edgecolor='#f39c12', lw=1.5, label='Plunger (Swings through hole)'))
    
    # Option 1 Cam
    poly_pts_cam = [
        (Y_AXLE, Z_AXLE),
        (Y_AXLE, Z_AXLE + HUB_DIAMETER/2 + 0.5),
        (5.00, 9.80),
        (1.50, 7.20),
        (1.80, 5.00),
        (4.50, 5.20),
        (Y_AXLE - 1.50, Z_AXLE - 2.50)
    ]
    ax2.add_patch(patches.Polygon(poly_pts_cam, facecolor='#00d2ff', alpha=0.6, edgecolor='#0984e3', lw=2, label='Current Cam (Option 1)'))
    
    ax2.set_xlim(-9, 16)
    ax2.set_ylim(-8, 18)
    ax2.set_xlabel('Y (mm)', color='white')
    ax2.set_ylabel('Z (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    ax2.legend(loc='lower left', fontsize=7.5, facecolor='#1a1a1a', labelcolor='white')
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "exact_assembly_alignment.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved exact assembly alignment plot to: {out_png}")

if __name__ == '__main__':
    run()
