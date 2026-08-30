"""
testing/plot_user_oriented_brass_insert.py
Visualizes the brass insert with:
- Horizontal axis = Y (Right = +Y, Left = -Y)
- Vertical axis = Z (Top = +Z, Bottom = -Z)
- Width across X = D3 = 6.74 mm
- Blade insertion direction = -Y (from right to left)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

# Caliper Dimensions:
D1A = 5.00   # Wide internal gap (in Z)
D1B = 1.00   # Pinch throat gap (in Z)
D2  = 14.40  # Total height between outer tips (in Z)
D4  = 8.40   # Distance from base to pinch throat (along Y)
D5  = 4.30   # Flare opening at tips (in Z)
D3  = 6.74   # Strip width (in X)
SHEET_THICK = 0.50

def get_user_oriented_brass_2d():
    """
    Constructs the 2D profile in (Y, Z):
    - Base / body is at -Y (e.g. Y in [-7.0, 0.0] mm)
    - Jaws extend towards +Y (e.g. up to Y = +6.0 mm)
    - Upper jaw is at +Z, Lower jaw is at -Z (or centered on socket center Z_center)
    - Pinch throat is at D4 distance from base
    """
    z_center = 7.00 # Center elevation of the socket blade path
    
    # In Y:
    # Jaws open at +Y (Y_mouth = +6.0 mm)
    # Throat is at Y_throat = Y_mouth - (D2 - D4) or at Y_throat = 0.0 mm
    # Belly is at Y_belly = -4.0 mm
    # Base/Pin extends to -Y (Y = -12.0 mm)
    
    y_mouth = 6.00
    y_throat = y_mouth - 2.50 # Y = 3.50 mm
    y_belly = y_throat - 5.00 # Y = -1.50 mm
    y_base = -6.00
    y_pin_tip = -14.00
    
    # Upper Jaw Centerline in (Y, Z):
    upper_jaw = [
        (y_base, z_center + D1A/2.0),
        (y_belly, z_center + D1A/2.0),
        (y_throat, z_center + D1B/2.0),
        (y_mouth, z_center + D5/2.0)
    ]
    
    # Lower Jaw Centerline in (Y, Z):
    lower_jaw = [
        (y_base, z_center - D1A/2.0),
        (y_belly, z_center - D1A/2.0),
        (y_throat, z_center - D1B/2.0),
        (y_mouth, z_center - D5/2.0)
    ]
    
    return upper_jaw, lower_jaw, z_center, y_base, y_pin_tip

def run():
    print("Plotting user-oriented brass insert...")
    upper_jaw, lower_jaw, z_c, y_base, y_pin = get_user_oriented_brass_2d()
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 10), facecolor='#1a1a1a', dpi=180)
    
    # --------------------------------------------------------------------------
    # Panel 1: Side View (Y-Z Plane) - Direct match to photo
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_facecolor('#222222')
    ax1.set_title("1. Exact Photo Orientation in (Y-Z Plane): Blade Inserts in -Y Direction", color='white', fontsize=12, weight='bold')
    
    # Baseplate Floor & Bracket
    ax1.add_patch(patches.Rectangle((-16, 0), 32, 1.0, facecolor='#888888', alpha=0.5, label='Baseplate Floor (Z=1.0mm)'))
    ax1.add_patch(patches.Rectangle((-7.17, 1.0), 14.34, 3.6, facecolor='#27ae60', alpha=0.25, edgecolor='#2ecc71', lw=1.5, label='Bracket 3&4 Guide Walls'))
    
    # Draw Shaft Hub (Y=9.28, Z=12.59) & Left Tower (Z_top=14.09)
    ax1.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.5, edgecolor='#d35400', lw=2, label='Shaft Hub (Y=9.28, Z=12.59)'))
    tower_yz = [(6.25, 1.0), (12.85, 1.0), (12.18, 14.09), (6.55, 14.09)]
    ax1.add_patch(patches.Polygon(tower_yz, facecolor='#3498db', alpha=0.3, edgecolor='#2980b9', lw=1.5, label='Tower Profile'))
    
    # Draw Brass Insert Upper & Lower Jaws
    t_h = SHEET_THICK / 2.0
    u_poly = [(p[0], p[1] - t_h) for p in upper_jaw] + [(p[0], p[1] + t_h) for p in reversed(upper_jaw)]
    l_poly = [(p[0], p[1] - t_h) for p in lower_jaw] + [(p[0], p[1] + t_h) for p in reversed(lower_jaw)]
    
    ax1.add_patch(patches.Polygon(u_poly, facecolor='#f39c12', alpha=0.8, edgecolor='#d68910', lw=2, label='Brass Upper Spring Jaw'))
    ax1.add_patch(patches.Polygon(l_poly, facecolor='#f39c12', alpha=0.8, edgecolor='#d68910', lw=2, label='Brass Lower Spring Jaw'))
    
    # Base Body & Terminal Pin extending to -Y
    ax1.add_patch(patches.Rectangle((y_base - SHEET_THICK, lower_jaw[0][1] - t_h), SHEET_THICK, (upper_jaw[0][1] - lower_jaw[0][1]) + 2*t_h, facecolor='#f39c12', alpha=0.9))
    ax1.add_patch(patches.Rectangle((y_pin, z_c - 0.4), y_base - y_pin, 0.8, facecolor='#f1c40f', alpha=0.9, edgecolor='#f39c12', lw=1.5, label='Terminal Pin (-Y direction)'))
    
    # Incoming Plug Blade (moving from +Y to -Y)
    ax1.add_patch(patches.Rectangle((7.0, z_c - 0.76), 8.0, 1.52, facecolor='#ecf0f1', alpha=0.5, edgecolor='white', lw=2, linestyle='--', label='Plug Blade (Inserts in -Y direction)'))
    ax1.annotate('', xy=(3.0, z_c), xytext=(8.0, z_c),
                 arrowprops=dict(arrowstyle='->', color='white', lw=3))
    ax1.text(5.5, z_c + 1.2, 'Blade Insertion (-Y)', color='white', fontsize=10, weight='bold', ha='center')
    
    # Dimension Annotations
    # D1a = 5.0 mm gap
    ax1.annotate('', xy=(upper_jaw[1][0], lower_jaw[1][1]), xytext=(upper_jaw[1][0], upper_jaw[1][1]),
                 arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
    ax1.text(upper_jaw[1][0] - 0.5, z_c, f'D1a = {D1A:.1f} mm\n(Belly)', color='yellow', fontsize=8, weight='bold', ha='right', va='center')
    
    # D1b = 1.0 mm throat
    ax1.annotate('', xy=(upper_jaw[2][0], lower_jaw[2][1]), xytext=(upper_jaw[2][0], upper_jaw[2][1]),
                 arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
    ax1.text(upper_jaw[2][0], z_c - 1.8, f'D1b = {D1B:.1f} mm\n(Throat)', color='yellow', fontsize=8, weight='bold', ha='center')
    
    # D5 = 4.3 mm mouth
    ax1.annotate('', xy=(upper_jaw[3][0], lower_jaw[3][1]), xytext=(upper_jaw[3][0], upper_jaw[3][1]),
                 arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
    ax1.text(upper_jaw[3][0] + 0.5, z_c, f'D5 = {D5:.1f} mm\n(Mouth)', color='yellow', fontsize=8, weight='bold', ha='left', va='center')
    
    ax1.set_xlim(-16, 16)
    ax1.set_ylim(-4, 18)
    ax1.set_xlabel('Y (mm)', color='white')
    ax1.set_ylabel('Z (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='upper left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 2: Top-Down Plan View (X-Y Plane)
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_facecolor('#222222')
    ax2.set_title("2. Top-Down (X-Y Plane): Brass Strip Width D3 = 6.74mm", color='white', fontsize=12, weight='bold')
    
    # Brackets
    ax2.add_patch(patches.Polygon(bracket_3_raw_pts, facecolor='#27ae60', alpha=0.4, edgecolor='#2ecc71', lw=1.5, label='Bracket 3 (Left)'))
    ax2.add_patch(patches.Polygon(bracket_4_raw_pts, facecolor='#27ae60', alpha=0.4, edgecolor='#2ecc71', lw=1.5, label='Bracket 4 (Right)'))
    
    # Brass Strip Footprint
    x_c_blade = (4.705 + 7.853) / 2.0  # 6.28 mm
    ax2.add_patch(patches.Rectangle((x_c_blade - D3/2, y_base), D3, upper_jaw[-1][0] - y_base,
                                    facecolor='#f39c12', alpha=0.6, edgecolor='#d68910', lw=2, label=f'Brass Strip (D3 = {D3:.2f}mm wide in X)'))
    
    # Terminal Pin footprint
    ax2.add_patch(patches.Rectangle((8.453 - 0.6, y_pin), 1.20, y_base - y_pin, facecolor='#f1c40f', alpha=0.8, label='Terminal Pin in Floor Slit'))
    
    # Shaft Hub & Plunger
    ax2.plot([X_TOWER_CENTER - TOTAL_AXLE_LEN/2, X_TOWER_CENTER + TOTAL_AXLE_LEN/2], [Y_AXLE, Y_AXLE], color='cyan', lw=3, label='Shaft Axle Axis')
    ax2.add_patch(patches.Rectangle((HOLE_X_CENTER - PLUNGER_WIDTH_X/2, Y_AXLE - 1.0), PLUNGER_WIDTH_X, 3.5,
                                    facecolor='#f1c40f', alpha=0.7, edgecolor='#f39c12', lw=1.5, label='Plunger Arm'))
    
    ax2.set_xlim(-1, 16)
    ax2.set_ylim(-16, 16)
    ax2.set_xlabel('X (mm)', color='white')
    ax2.set_ylabel('Y (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    ax2.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "user_oriented_brass_insert.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved user-oriented diagram to: {out_png}")

if __name__ == '__main__':
    run()
