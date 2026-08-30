"""
testing/simulate_horizontal_insertion.py
Complete kinematic simulation of horizontal plug insertion in -Y direction
with the exact OEM brass insert orientation matching the physical photo.
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
    CAM_WIDTH_X, CAM_X_CENTER,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    X_TOWER_CENTER, HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    TOWER_HEIGHT, BASE_THICK
)
from testing.plot_user_oriented_brass_insert import get_user_oriented_brass_2d, D1A, D1B, D2, D4, D5, D3, SHEET_THICK

BLADE_THICKNESS = 1.52 # in Z
BLADE_WIDTH_Y   = 6.35 # in Y
BLADE_LENGTH_Y  = 16.50 # total plug blade reach in -Y
BLADE_WIDTH_X   = 4.30 # NEMA 5-15 hot blade width in X

Z_SWITCH = -6.50
Y_SWITCH_STEM_REST = 12.40

def simulate_horizontal_stroke():
    upper_jaw, lower_jaw, z_c, y_base, y_pin = get_user_oriented_brass_2d()
    
    # Cam profile in (Y, Z) at rest (theta = 0 deg)
    # The cam hangs down from the shaft axle (Y=9.28, Z=12.59) into the blade path at (Y ~ 4.0..6.0, Z ~ 7.0)
    r_hub = HUB_DIAMETER / 2.0
    cam_poly_home = np.array([
        (Y_AXLE, Z_AXLE),
        (Y_AXLE + 1.0, Z_AXLE + r_hub),
        (5.00, 9.50),
        (3.50, 7.00),
        (4.50, 6.00),
        (Y_AXLE - 1.0, Z_AXLE - r_hub)
    ])
    
    # Plunger dimensions from axle
    plunger_y_home = 10.479
    plunger_z_home = -6.50
    dy_p = plunger_y_home - Y_AXLE
    dz_p = plunger_z_home - Z_AXLE
    
    # Blade travel from Y_tip = 14.0 mm down to Y_tip = -4.0 mm (in -Y direction)
    y_tip_range = np.linspace(14.0, -4.0, 181)
    
    thetas_deg = np.linspace(0.0, 20.0, 401)
    rads = np.radians(thetas_deg)
    cos_v = np.cos(rads)[:, None]
    sin_v = np.sin(rads)[:, None]
    
    cam_vecs = cam_poly_home - np.array([Y_AXLE, Z_AXLE])
    
    results = []
    
    # Active cam contact point at rest: (Y ~ 3.50, Z ~ 7.00)
    cam_pt_home = np.array([3.50, 7.00])
    cam_pt_vec = cam_pt_home - np.array([Y_AXLE, Z_AXLE])
    
    # Rotated cam point Y coords for each theta
    rot_cam_pt_y = Y_AXLE + np.cos(rads) * cam_pt_vec[0] - np.sin(rads) * cam_pt_vec[1]
    rot_cam_pt_z = Z_AXLE + np.sin(rads) * cam_pt_vec[0] + np.cos(rads) * cam_pt_vec[1]
    
    for y_tip in y_tip_range:
        # Blade occupies Y in [y_tip, y_tip + BLADE_LENGTH_Y] and Z in [z_c - BLADE_THICKNESS/2, z_c + BLADE_THICKNESS/2]
        # When y_tip pushes past rot_cam_pt_y, it drives rotation
        
        # Find minimum theta where cam point is at or ahead of y_tip (in -Y direction)
        penetration = (rot_cam_pt_y > y_tip) & (rot_cam_pt_z >= z_c - 1.0) & (rot_cam_pt_z <= z_c + 1.0)
        
        valid_indices = np.where(~penetration)[0]
        if len(valid_indices) > 0:
            best_idx = valid_indices[0]
        else:
            best_idx = len(thetas_deg) - 1
            
        found_theta = thetas_deg[best_idx]
        rad_f = np.radians(found_theta)
        c_f, s_f = np.cos(rad_f), np.sin(rad_f)
        
        y_plunger = Y_AXLE + c_f * dy_p - s_f * dz_p
        z_plunger = Z_AXLE + s_f * dy_p + c_f * dz_p
        switch_actuated = (y_plunger >= Y_SWITCH_STEM_REST)
        
        poly_rot = np.zeros_like(cam_poly_home)
        poly_rot[:, 0] = Y_AXLE + c_f * cam_vecs[:, 0] - s_f * cam_vecs[:, 1]
        poly_rot[:, 1] = Z_AXLE + s_f * cam_vecs[:, 0] + c_f * cam_vecs[:, 1]
        
        results.append({
            'y_tip': y_tip,
            'theta_deg': found_theta,
            'cam_poly_rot': poly_rot,
            'y_plunger': y_plunger,
            'z_plunger': z_plunger,
            'switch_actuated': switch_actuated
        })
        
    return results

def run():
    print("Running horizontal stroke simulation with correct brass orientation...")
    results = simulate_horizontal_stroke()
    
    contact_init = [r for r in results if r['theta_deg'] > 0.01]
    r_init = contact_init[0] if len(contact_init) > 0 else results[0]
    
    trip_events = [r for r in results if r['switch_actuated']]
    r_trip = trip_events[0] if len(trip_events) > 0 else results[-1]
    r_final = results[-1]
    
    upper_jaw, lower_jaw, z_c, y_base, y_pin = get_user_oriented_brass_2d()
    t_h = SHEET_THICK / 2.0
    u_poly = [(p[0], p[1] - t_h) for p in upper_jaw] + [(p[0], p[1] + t_h) for p in reversed(upper_jaw)]
    l_poly = [(p[0], p[1] - t_h) for p in lower_jaw] + [(p[0], p[1] + t_h) for p in reversed(lower_jaw)]
    
    fig = plt.figure(figsize=(20, 14), facecolor='#1a1a1a', dpi=180)
    
    # --------------------------------------------------------------------------
    # Panel 1: 2D Dynamic Kinematic Snapshots in (Y-Z Plane)
    # --------------------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1, facecolor='#222222')
    ax1.set_title("1. Dynamic Plug Insertion Kinematics in -Y Direction", color='white', fontsize=12, weight='bold')
    
    # Baseplate Floor & Bracket Walls
    ax1.add_patch(patches.Rectangle((-16, 0), 32, 1.0, facecolor='#888888', alpha=0.5, label='Baseplate Floor (Z=1.0mm)'))
    ax1.add_patch(patches.Rectangle((-7.17, 1.0), 14.34, 3.6, facecolor='#27ae60', alpha=0.2, edgecolor='#2ecc71', linestyle=':', label='Bracket Guide Walls'))
    
    # Brass Insert Jaws
    ax1.add_patch(patches.Polygon(u_poly, facecolor='#f39c12', alpha=0.6, edgecolor='#d68910', lw=2, label='Brass Upper Jaw'))
    ax1.add_patch(patches.Polygon(l_poly, facecolor='#f39c12', alpha=0.6, edgecolor='#d68910', lw=2, label='Brass Lower Jaw'))
    ax1.add_patch(patches.Rectangle((y_base - SHEET_THICK, lower_jaw[0][1] - t_h), SHEET_THICK, (upper_jaw[0][1] - lower_jaw[0][1]) + 2*t_h, facecolor='#f39c12', alpha=0.8))
    ax1.add_patch(patches.Rectangle((y_pin, z_c - 0.4), y_base - y_pin, 0.8, facecolor='#f1c40f', alpha=0.8, label='Terminal Pin (-Y)'))
    
    # Hub Barrel & Left Tower
    ax1.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.4, edgecolor='#d35400', lw=1.5, label='Rocker Hub'))
    tower_yz = [(6.25, 1.0), (12.85, 1.0), (12.18, 14.09), (6.55, 14.09)]
    ax1.add_patch(patches.Polygon(tower_yz, facecolor='#3498db', alpha=0.2, edgecolor='#2980b9', lw=1.5, label='Tower Profile'))
    
    # Milestones
    stage_entry = results[0]
    milestones = [
        (stage_entry, '#9b59b6', '1. Approach (Y_tip=14.0mm, 0°)'),
        (r_init, '#00d2ff', f'2. Cam Contact (Y_tip={r_init["y_tip"]:.1f}mm, 0°)'),
        (r_trip, '#f1c40f', f'3. Switch Trip (Y_tip={r_trip["y_tip"]:.1f}mm, {r_trip["theta_deg"]:.1f}°)'),
        (r_final, '#e74c3c', f'4. Fully Seated (Y_tip=-4.0mm, {r_final["theta_deg"]:.1f}°)')
    ]
    for r, col, lbl in milestones:
        ax1.add_patch(patches.Polygon(r['cam_poly_rot'], facecolor=col, alpha=0.4, edgecolor=col, lw=2, label=lbl))
        y_tip = r['y_tip']
        ax1.add_patch(patches.Rectangle((y_tip, z_c - BLADE_THICKNESS/2), BLADE_LENGTH_Y, BLADE_THICKNESS,
                                        fill=False, edgecolor=col, linestyle='--', lw=1.5))
        
    ax1.set_xlim(-16, 16)
    ax1.set_ylim(-2, 18)
    ax1.set_xlabel('Y (mm)', color='white')
    ax1.set_ylabel('Z (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='upper right', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 2: Top-Down View (X-Y Plane)
    # --------------------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#222222')
    ax2.set_title("2. Top-Down Alignment (X-Y Plane): Strip Width D3 = 6.74mm", color='white', fontsize=12, weight='bold')
    
    ax2.add_patch(patches.Polygon(bracket_3_raw_pts, facecolor='#27ae60', alpha=0.4, edgecolor='#2ecc71', lw=1.5, label='Bracket 3'))
    ax2.add_patch(patches.Polygon(bracket_4_raw_pts, facecolor='#27ae60', alpha=0.4, edgecolor='#2ecc71', lw=1.5, label='Bracket 4'))
    
    x_c_blade = (4.705 + 7.853) / 2.0  # 6.28 mm
    ax2.add_patch(patches.Rectangle((x_c_blade - D3/2, y_base), D3, upper_jaw[-1][0] - y_base,
                                    facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=2, label=f'Brass Strip (D3 = {D3:.2f}mm)'))
    ax2.add_patch(patches.Rectangle((8.453 - 0.6, y_pin), 1.20, y_base - y_pin, facecolor='#f1c40f', alpha=0.8, label='Pin in Floor Slit'))
    
    ax2.plot([X_TOWER_CENTER - TOTAL_AXLE_LEN/2, X_TOWER_CENTER + TOTAL_AXLE_LEN/2], [Y_AXLE, Y_AXLE], color='cyan', lw=3, label='Shaft Axle')
    ax2.add_patch(patches.Rectangle((HOLE_X_CENTER - PLUNGER_WIDTH_X/2, Y_AXLE - 1.0), PLUNGER_WIDTH_X, 3.5,
                                    facecolor='#f1c40f', alpha=0.7, edgecolor='#f39c12', lw=1.5, label='Plunger Arm'))
    
    ax2.set_xlim(-1, 16)
    ax2.set_ylim(-16, 16)
    ax2.set_xlabel('X (mm)', color='white')
    ax2.set_ylabel('Y (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    ax2.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 3: Kinematic Curve
    # --------------------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3, facecolor='#222222')
    ax3.set_title("3. Kinematic Stroke: Shaft Rotation θ & Plunger vs Blade Tip Y Position", color='white', fontsize=12, weight='bold')
    
    y_tips_all = [r['y_tip'] for r in results]
    thetas_all = [r['theta_deg'] for r in results]
    y_plungers = [r['y_plunger'] for r in results]
    
    ax3.plot(y_tips_all, thetas_all, color='#00d2ff', lw=2.5, label='Shaft Rotation θ (deg)')
    ax3.plot(y_tips_all, y_plungers, color='#e67e22', lw=2.0, linestyle='-.', label='Plunger Y Position (mm)')
    
    ax3.axvline(r_init['y_tip'], color='#00d2ff', linestyle=':', lw=1.5, label=f'Cam Contact (Y_tip = {r_init["y_tip"]:.2f} mm)')
    ax3.axvline(r_trip['y_tip'], color='#f1c40f', linestyle='--', lw=1.5, label=f'Switch Trip (Y_tip = {r_trip["y_tip"]:.2f} mm)')
    ax3.axhline(Y_SWITCH_STEM_REST, color='#f1c40f', linestyle=':', lw=1.2, label=f'Switch Threshold (Y = {Y_SWITCH_STEM_REST:.2f} mm)')
    
    ax3.set_xlim(14, -4)
    ax3.set_ylim(0, 22)
    ax3.set_xlabel('Blade Tip Y Position (mm) [Moving Right to Left in -Y]', color='white')
    ax3.set_ylabel('Rotation θ (deg) / Plunger Y (mm)', color='white')
    ax3.tick_params(colors='white')
    ax3.grid(True, color='#444444', linestyle=':')
    ax3.legend(loc='upper right', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 4: Physical Integration Summary
    # --------------------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4, facecolor='#222222')
    ax4.set_title("4. Corrected Physical Alignment & Kinematic Summary", color='white', fontsize=12, weight='bold')
    ax4.axis('off')
    
    summary_text = (
        "CORRECTED PHYSICAL ALIGNMENT (BLADE INSERTS IN -Y DIRECTION):\n\n"
        "1. PHYSICAL ORIENTATION (MATCHING PHOTO):\n"
        "   - Horizontal Axis:  Y-axis (Right = +Y, Left = -Y)\n"
        "   - Vertical Axis:    Z-axis (Top = +Z, Bottom = -Z)\n"
        "   - Transverse Axis:  X-axis (Strip width D3 = 6.74 mm)\n"
        "   - Blade Insertion:  Moves from Right (+Y) to Left (-Y)\n\n"
        "2. BRASS JAW CAVITIES IN (Y, Z):\n"
        "   - Mouth Opening:    D5 = 4.30 mm in Z at Y = +6.00 mm\n"
        "   - Pinch Throat:     D1b = 1.00 mm in Z at Y = +3.50 mm\n"
        "   - Wide Belly:       D1a = 5.00 mm in Z at Y = -1.50 mm\n"
        "   - Base & Pin:       Extends to Y = -14.00 mm through floor slit\n\n"
        "3. KINEMATIC STROKE & SWITCH INTERLOCK:\n"
        f"   - Initial Contact:  Blade tip engages cam at Y_tip = {r_init['y_tip']:.2f} mm\n"
        f"   - Switch Actuation: Fully trips switch at Y_tip = {r_trip['y_tip']:.2f} mm (θ = {r_trip['theta_deg']:.2f}°)\n"
        f"   - Fully Seated:     Blade stops at Y_tip = -4.00 mm (θ = {r_final['theta_deg']:.2f}°)"
    )
    
    ax4.text(0.02, 0.98, summary_text, color='#ecf0f1', fontsize=9.2, fontfamily='monospace',
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e272e', edgecolor='#2ecc71', lw=1.5))
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "corrected_brass_kinematic_simulation.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved corrected simulation diagram to: {out_png}")

if __name__ == '__main__':
    run()
