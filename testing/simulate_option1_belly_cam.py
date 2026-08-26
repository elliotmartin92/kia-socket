"""
testing/simulate_option1_belly_cam.py
Kinematic simulation, geometry solver, and clearance check for Option 1 (Direct Belly Cam).
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

BLADE_WIDTH_HOT = 4.30
BLADE_THICKNESS = 1.52
BLADE_LENGTH = 16.50

Z_SWITCH = -6.50
Y_SWITCH_STEM_REST = 12.40

def get_option1_cam_poly_detailed():
    r_hub = HUB_DIAMETER / 2.0
    # Solid 2.80mm thick straight beam directly connecting hub barrel into 5.0mm belly
    pts = [
        (Y_AXLE, Z_AXLE + r_hub),          # (9.28, 14.69)
        (Y_AXLE + 1.20, Z_AXLE + 1.00),    # Top hub blend
        (4.00, 9.00),                      # Top straight crowned ramp
        (1.50, 7.20),                      # Active contact tip inside 5.0mm belly (under throat Z=9.4mm)
        (2.00, 4.80),                      # Rounded nose bottom inside belly
        (4.50, 5.20),                      # Beam underside
        (Y_AXLE - 0.50, Z_AXLE - 2.50),    # Bottom hub blend
        (Y_AXLE - 1.50, Z_AXLE)
    ]
    return np.array(pts)

def simulate_option1(z_tip_range=np.linspace(10.0, 3.0, 141)):
    cam_poly_home = get_option1_cam_poly_detailed()
    top_cam_spine = np.array([cam_poly_home[2], cam_poly_home[3]]) # Contact ramp
    
    plunger_y_home = 10.479
    plunger_z_home = -6.50
    dy_p = plunger_y_home - Y_AXLE
    dz_p = plunger_z_home - Z_AXLE
    
    thetas_deg = np.linspace(0.0, 15.0, 301)
    rads = np.radians(thetas_deg)
    cos_v = np.cos(rads)[:, None]
    sin_v = np.sin(rads)[:, None]
    
    cam_vecs = top_cam_spine - np.array([Y_AXLE, Z_AXLE])
    all_rot_y = Y_AXLE + cos_v * cam_vecs[None, :, 0] - sin_v * cam_vecs[None, :, 1]
    all_rot_z = Z_AXLE + sin_v * cam_vecs[None, :, 0] + cos_v * cam_vecs[None, :, 1]
    
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    w_blade_y = BLADE_WIDTH_HOT
    y_b_min = y_blade_c - w_blade_y / 2.0
    y_b_max = y_blade_c + w_blade_y / 2.0
    
    results = []
    
    for z_tip in z_tip_range:
        z_blade_top = z_tip + BLADE_LENGTH
        in_y = (all_rot_y >= y_b_min) & (all_rot_y <= y_b_max)
        
        # Blade penetration check
        penetration = in_y & (all_rot_z > z_tip) & (all_rot_z < z_blade_top)
        angle_has_penetration = np.any(penetration, axis=1)
        
        valid_indices = np.where(~angle_has_penetration)[0]
        if len(valid_indices) > 0:
            best_idx = valid_indices[0]
        else:
            best_idx = len(thetas_deg) - 1
            
        found_theta = thetas_deg[best_idx]
        best_cam_pts = np.column_stack([all_rot_y[best_idx], all_rot_z[best_idx]])
        
        rad_f = np.radians(found_theta)
        c_f, s_f = np.cos(rad_f), np.sin(rad_f)
        
        y_plunger = Y_AXLE + c_f * dy_p - s_f * dz_p
        z_plunger = Z_AXLE + s_f * dy_p + c_f * dz_p
        
        switch_actuated = (y_plunger >= Y_SWITCH_STEM_REST)
        
        cam_poly_vecs = cam_poly_home - np.array([Y_AXLE, Z_AXLE])
        poly_rot = np.zeros_like(cam_poly_home)
        poly_rot[:, 0] = Y_AXLE + c_f * cam_poly_vecs[:, 0] - s_f * cam_poly_vecs[:, 1]
        poly_rot[:, 1] = Z_AXLE + s_f * cam_poly_vecs[:, 0] + c_f * cam_poly_vecs[:, 1]
        
        results.append({
            'z_tip': z_tip,
            'theta_deg': found_theta,
            'cam_poly_rot': poly_rot,
            'y_plunger': y_plunger,
            'z_plunger': z_plunger,
            'switch_actuated': switch_actuated
        })
        
    return results

def run():
    print("Simulating Option 1 (Direct Belly Cam)...")
    results = simulate_option1()
    
    contact_init = [r for r in results if r['theta_deg'] > 0.01]
    r_init = contact_init[0] if len(contact_init) > 0 else results[0]
    
    trip_events = [r for r in results if r['switch_actuated']]
    r_trip = trip_events[0] if len(trip_events) > 0 else results[-1]
    r_final = results[-1]
    
    print(f"  Contact Init:   Z_tip = {r_init['z_tip']:.2f} mm (Plug blade emerges from pinch throat)")
    print(f"  Switch Trigger: Z_tip = {r_trip['z_tip']:.2f} mm (theta = {r_trip['theta_deg']:.2f} deg, Plunger Y = {r_trip['y_plunger']:.2f} mm)")
    print(f"  Full Seated:    Z_tip = {r_final['z_tip']:.2f} mm (theta = {r_final['theta_deg']:.2f} deg, Plunger Y = {r_final['y_plunger']:.2f} mm)")
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), facecolor='#1a1a1a', dpi=180)
    front_pts, rear_pts, y_b_c = get_brass_contact_2d_profile()
    t_half = SHEET_THICK / 2.0
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    
    # Panel 1: Kinematic Snapshots
    ax1 = axes[0]
    ax1.set_facecolor('#222222')
    ax1.set_title("1. Option 1 Motion Snapshots in 5.0mm Belly Cavity", color='white', fontsize=12, weight='bold')
    ax1.add_patch(patches.Rectangle((-4, 0), 18, 1.0, facecolor='#666666', alpha=0.4))
    ax1.add_patch(patches.Polygon(f_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.5, label='Brass Contact'))
    ax1.add_patch(patches.Polygon(r_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.5))
    ax1.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.4, edgecolor='#d35400', lw=1.5))
    
    milestones = [
        (r_init, '#00d2ff', f'1. Contact Init (Z_tip={r_init["z_tip"]:.1f}mm, 0.0°)'),
        (r_trip, '#f1c40f', f'2. Switch Trip (Z_tip={r_trip["z_tip"]:.1f}mm, {r_trip["theta_deg"]:.1f}°)'),
        (r_final, '#e74c3c', f'3. Seated (Z_tip=3.0mm, {r_final["theta_deg"]:.1f}°)')
    ]
    for r, col, lbl in milestones:
        ax1.add_patch(patches.Polygon(r['cam_poly_rot'], facecolor=col, alpha=0.45, edgecolor=col, lw=2, label=lbl))
        z_tip = r['z_tip']
        ax1.add_patch(patches.Rectangle((y_b_c - BLADE_WIDTH_HOT/2, z_tip), BLADE_WIDTH_HOT, BLADE_LENGTH,
                                        fill=False, edgecolor=col, linestyle='--', lw=1.5))
        
    ax1.set_xlim(-4, 14)
    ax1.set_ylim(0, 18)
    ax1.set_xlabel('Y (mm)', color='white')
    ax1.set_ylabel('Z (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # Panel 2: Stroke Curve
    ax2 = axes[1]
    ax2.set_facecolor('#222222')
    ax2.set_title("2. Kinematic Stroke Curve: Shaft Rotation θ vs Plug Depth", color='white', fontsize=12, weight='bold')
    z_tips_all = [r['z_tip'] for r in results]
    thetas_all = [r['theta_deg'] for r in results]
    ax2.plot(z_tips_all, thetas_all, color='#00d2ff', lw=2.5, label='Shaft Rotation θ (deg)')
    ax2.axvline(r_trip['z_tip'], color='#f1c40f', linestyle='--', lw=1.5, label=f'Switch Trip (Z_tip = {r_trip["z_tip"]:.2f} mm)')
    ax2.axvline(4.60, color='#e74c3c', linestyle=':', lw=1.5, label='Busbar Seated Elevation (Z = 4.60 mm)')
    
    ax2.set_xlim(10, 2)
    ax2.set_ylim(0, 16)
    ax2.set_xlabel('Plug Blade Tip Elevation Z (mm)', color='white')
    ax2.set_ylabel('Rocker Shaft Rotation θ (deg)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    ax2.legend(loc='upper right', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "option1_belly_cam_simulation.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved Option 1 simulation diagram to: {out_png}")

if __name__ == '__main__':
    run()
