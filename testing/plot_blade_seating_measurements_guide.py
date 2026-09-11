"""
testing/plot_blade_seating_measurements_guide.py
Generates a clear, professional visual diagram illustrating all key caliper measurement
points and stackup clearances to diagnose blade seating interference with the rocker arm.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import BASE_THICK, TOWER_HEIGHT, OUTER_WALL_HEIGHT
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK

def generate_diagram():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9), facecolor='#1a1a1a', dpi=200)
    
    for ax in (ax1, ax2):
        ax.set_facecolor('#222222')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#555555')
            
    # =========================================================================
    # Panel 1: Side Profile (Y-Z Plane) - Kinematic Stackup & Measurement Points
    # =========================================================================
    ax1.set_title("1. SIDE PROFILE (Y-Z Plane): Blade Stroke, Cam Travel & Switch Stackup",
                  color='white', fontsize=12, weight='bold', pad=12)
    
    # 1. Baseplate floor
    ax1.add_patch(patches.Rectangle((-5, 0), 22, 1.0, facecolor='#444444', edgecolor='#666666', lw=1.5, label='Baseplate Floor (Z=0 to 1.0mm)'))
    
    # 2. Left Tower
    tower_yz = [(6.25, 1.0), (12.85, 1.0), (12.18, 14.09), (6.55, 14.09)]
    ax1.add_patch(patches.Polygon(tower_yz, facecolor='#2980b9', alpha=0.3, edgecolor='#3498db', lw=1.5, label='Shaft Towers (Z=14.09mm)'))
    
    # 3. Pivot Axle
    ax1.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#d35400', alpha=0.5, edgecolor='#e67e22', lw=2, label='Shaft Hub (Ø4.20mm)'))
    ax1.plot([Y_AXLE], [Z_AXLE], 'o', color='cyan', markersize=5)
    
    # 4. Brass Contact
    front_pts, rear_pts, y_b_c = get_brass_contact_2d_profile()
    t_half = SHEET_THICK / 2.0
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    ax1.add_patch(patches.Polygon(f_poly_pts, facecolor='#f39c12', alpha=0.35, edgecolor='#d68910', lw=1.5, label='Brass Contact Spring'))
    ax1.add_patch(patches.Polygon(r_poly_pts, facecolor='#f39c12', alpha=0.35, edgecolor='#d68910', lw=1.5))
    
    # 5. Cam at Rest (0 deg) and Rotated (10 deg)
    r_hub = HUB_DIAMETER / 2.0
    cam_pts_home = np.array([
        [Y_AXLE, Z_AXLE],
        [Y_AXLE, Z_AXLE + r_hub + 0.5],
        [5.00, 9.80],
        [1.50, 7.20],
        [1.80, 5.00],
        [4.50, 5.20],
        [Y_AXLE - 1.50, Z_AXLE - 2.50]
    ])
    ax1.add_patch(patches.Polygon(cam_pts_home, facecolor='#e74c3c', alpha=0.4, edgecolor='#c0392b', lw=1.5, label='Cam Tab at Rest (0°)'))
    
    # Cam rotated 10 deg
    rad10 = np.radians(10.0)
    c10, s10 = np.cos(rad10), np.sin(rad10)
    cam_rot10 = np.zeros_like(cam_pts_home)
    for i, (y, z) in enumerate(cam_pts_home):
        dy, dz = y - Y_AXLE, z - Z_AXLE
        cam_rot10[i, 0] = Y_AXLE + c10 * dy - s10 * dz
        cam_rot10[i, 1] = Z_AXLE + s10 * dy + c10 * dz
    ax1.add_patch(patches.Polygon(cam_rot10, facecolor='#2ecc71', alpha=0.5, edgecolor='#27ae60', lw=2, linestyle='--', label='Cam Tab Depressed (10°)'))
    
    # 6. Plug Blade
    blade_w = 6.35
    blade_len = 16.50
    # Fully seated plug blade (e.g. tip at Z = 1.5 mm)
    z_tip_seated = 1.50
    ax1.add_patch(patches.Rectangle((y_b_c - blade_w/2, z_tip_seated), blade_w, blade_len,
                                    facecolor='#ecf0f1', alpha=0.7, edgecolor='white', lw=1.5, label='Plug Blade (Fully Seated)'))
    
    # 7. PCB & Tactile Switch
    ax1.add_patch(patches.Rectangle((5, -8.0), 12, 1.0, facecolor='#27ae60', alpha=0.5, edgecolor='#2ecc71', lw=1.5, label='PCB Board'))
    ax1.add_patch(patches.Rectangle((10.0, -7.0), 4.5, 2.5, facecolor='#9b59b6', alpha=0.6, edgecolor='#8e44ad', lw=1.5, label='Tactile Microswitch'))
    ax1.plot([12.25], [-4.50], 's', color='#f1c40f', markersize=8, label='Switch Actuator Button')
    
    # Through-hole
    ax1.plot([8.57, 8.57], [0, 1.0], color='#e74c3c', lw=3)
    ax1.plot([13.08, 13.08], [0, 1.0], color='#e74c3c', lw=3)
    ax1.text(10.8, 0.5, "Through-Hole\n[8.57, 13.08]", color='white', fontsize=8, ha='center', va='center')
    
    # Callout Measurements
    # M1: Blade Seating Depth Gap
    ax1.annotate('', xy=(y_b_c, z_tip_seated), xytext=(y_b_c, z_tip_seated + 16.5),
                 arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
    ax1.text(y_b_c - 0.5, z_tip_seated + 8.0, "[M1] Blade Length\n(16.0-17.5mm)", color='yellow', fontsize=9, weight='bold', ha='right')
    
    # M2: Cam Tip Z at Full Stroke vs Blade Tip
    ax1.annotate('', xy=(1.5, 0), xytext=(1.5, 3.82),
                 arrowprops=dict(arrowstyle='<->', color='#00d2ff', lw=2))
    ax1.text(1.7, 2.0, "[M2] Cam Min Z\n(~3.8mm at 10°)", color='#00d2ff', fontsize=9, weight='bold')
    
    # M4: Plunger to Switch Gap
    ax1.annotate('', xy=(13.78, -6.0), xytext=(12.25, -4.5),
                 arrowprops=dict(arrowstyle='<->', color='#ff7675', lw=2))
    ax1.text(14.2, -5.2, "[M4] Plunger vs\nSwitch Solid Stop", color='#ff7675', fontsize=9, weight='bold')
    
    ax1.set_xlim(-4, 18)
    ax1.set_ylim(-9, 20)
    ax1.set_xlabel("Y Position (mm)", color='white', fontsize=10)
    ax1.set_ylabel("Z Elevation (mm)", color='white', fontsize=10)
    ax1.legend(loc='upper right', fontsize=8, facecolor='#333333', edgecolor='#555555', labelcolor='white')
    ax1.grid(True, linestyle=':', alpha=0.4)
    
    # =========================================================================
    # Panel 2: Caliper Measurement Checklist & Diagnostic Table
    # =========================================================================
    ax2.set_title("2. DIAGNOSTIC MEASUREMENT PROCEDURE & VERIFICATION CHECKLIST",
                  color='white', fontsize=12, weight='bold', pad=12)
    ax2.axis('off')
    
    checklist_text = """
Step-by-Step Caliper Measurements to Confirm Interference:

[M1] Plug Blade Length & Seating Shoulder Gap:
     - Measure hot prong length from plug body shoulder to tip:
       Expected: 16.00 mm - 17.50 mm.
     - Fully insert plug into outlet assembly and measure remaining gap at faceplate:
       If a gap of 1.0 - 2.5 mm remains and feels springy/solid -> INTERFERENCE CONFIRMED.

[M2] Differential Insertion Depth Test (A/B Test):
     - Test 1 (No Rocker): Insert plug into baseplate + brackets. Measure depth / flushness.
     - Test 2 (Rocker Only, No PCB): Insert plug. Does blade seat to same depth?
     - Test 3 (Full Assembly + PCB): Does blade seat to same depth?
     -> Pinpoints whether interference is at Cam (Test 2) or PCB Switch Stop (Test 3).

[M3] Cam Lowest Elevation vs Baseplate Floor:
     - Depress rocker arm fully with finger until plunger hits through-hole or stop.
     - Measure vertical distance from bracket top (Z=4.60mm) down to depressed cam face.
     - Check: Is depressed cam face higher than the fully seated blade tip?

[M4] Tactile Switch Height & Plunger Travel:
     - Measure distance from baseplate bottom face (Z=0.00mm) to switch button apex.
     - Expected: ~6.0 - 6.5 mm.
     - Check: If plunger hits switch solid base before rocker rotates ~8°-10°,
       the switch is acting as a rigid travel limiter for the blade.

[M5] Plunger Through-Hole Margin:
     - Check rear gap behind plunger at Z=0.00mm.
     - Baseplate through-hole rear edge is at Y = 13.08 mm.
     - Check if plunger back face binds against the through-hole perimeter.

[M6] Cam Lateral Fit in Brass Contact:
     - Measure cam tab width in X (Nominal: 2.70 mm, X in [4.93, 7.63] mm).
     - Check opening between brass contact leaves (Nominal belly opening: ~5.0 mm).
     - Verify cam does not rub or snag against brass leaf side edges.
"""
    ax2.text(0.02, 0.95, checklist_text, color='#ecf0f1', fontsize=9.5, family='monospace',
             va='top', ha='left', linespacing=1.35)
    
    plt.tight_layout()
    out_path = "testing/blade_seating_measurements_diagram.png"
    plt.savefig(out_path, dpi=200)
    print(f"Saved {out_path}")

if __name__ == '__main__':
    generate_diagram()
