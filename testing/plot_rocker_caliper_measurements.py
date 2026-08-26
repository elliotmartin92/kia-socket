"""
testing/plot_rocker_caliper_measurements.py
Visualizes the exact nominal 2D profile of the shaft rocker / cam / lever assembly,
annotating all caliper measurement candidates around the 10.7 mm dimension.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh
)

def run():
    # Load 2D profile of plunger and cam
    y_axle = Y_AXLE  # 9.279
    z_axle = Z_AXLE  # 12.590
    r_hub = HUB_DIAMETER / 2.0  # 2.10
    
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#1a1a1a', dpi=180)
    ax.set_facecolor('#222222')
    ax.set_title("Nominal Rocker & Lever Dimensions (Y-Z Profile)", color='white', fontsize=13, weight='bold', pad=15)
    
    # 1. Axle & Hub circle
    circle = patches.Circle((y_axle, z_axle), r_hub, color='#e67e22', alpha=0.3, edgecolor='#d35400', lw=1.5, label='Hub Barrel (Ø4.20mm)')
    ax.add_patch(circle)
    ax.plot([y_axle], [z_axle], 'o', color='cyan', markersize=6, label='Pivot Axis (9.28, 12.59)')
    
    # 2. Plunger contour
    z_tip = -6.50
    r_tip = 1.00
    plunger_y_center = 10.479
    N = 50
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + r_hub) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - r_hub) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger = patches.Polygon(pts_plunger, color='#f1c40f', alpha=0.35, edgecolor='#f39c12', lw=2, label='Plunger Blade')
    ax.add_patch(poly_plunger)
    
    # 3. Cam tab contour
    theta_cam = np.radians(-161.40)
    u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)])
    u_perp_up = np.array([u_dir[1], -u_dir[0]])
    if u_perp_up[1] < 0:
        u_perp_up = -u_perp_up
    cam_reach = 6.80
    cam_arm_thick = 2.80
    
    p_tangent_top = np.array([y_axle, z_axle]) + u_perp_up * r_hub
    p_top_tip = p_tangent_top + u_dir * cam_reach
    p_bot_tip = p_top_tip - u_perp_up * cam_arm_thick
    p_tangent_bot = p_tangent_top - u_perp_up * cam_arm_thick
    
    t_crown = np.linspace(0, 1, 33)
    cam_top_crowned = []
    crown_height = 0.45
    for tc in t_crown:
        pt = (1-tc)*p_tangent_top + tc*p_top_tip + 4*tc*(1-tc)*u_perp_up*crown_height
        cam_top_crowned.append((pt[0], pt[1]))
        
    half_t = cam_arm_thick / 2.0
    p_tip_mid = (p_top_tip + p_bot_tip) / 2.0
    cam_tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_tip_mid + u_dir * (half_t * np.cos(a)) + u_perp_up * (half_t * np.sin(a))
        cam_tip_pts.append((pt[0], pt[1]))
        
    poly_cam_arm_pts = cam_top_crowned + cam_tip_pts + [p_tangent_bot, p_tangent_top]
    poly_cam = patches.Polygon(poly_cam_arm_pts, color='#e74c3c', alpha=0.5, edgecolor='#c0392b', lw=2, label='Input Cam Tab')
    ax.add_patch(poly_cam)
    
    # 4. Caliper Measurements & Dimensions:
    # A. Cam top apex to opposite plunger spine (10.65 mm):
    p_cam_apex = np.array(cam_top_crowned[16]) # mid-crown apex: ~ (5.72, 12.60)
    p_cam_tip_top = np.array(cam_top_crowned[-1]) # (2.83, 10.42)
    p_plunger_spine = np.array([spine_y[25], spine_z[25]]) # (13.08, 7.50) where lever emerges
    
    # Dimension line 1: Tip to plunger spine = 10.65 mm
    ax.plot([p_cam_tip_top[0], p_plunger_spine[0]], [p_cam_tip_top[1], p_plunger_spine[1]], 'y--', lw=2, marker='o', markersize=6)
    ax.annotate(f'Nominal Dimension: 10.65 mm\n(Cam Tip to Opposite Lever Spine)',
                xy=((p_cam_tip_top[0] + p_plunger_spine[0])/2, (p_cam_tip_top[1] + p_plunger_spine[1])/2),
                xytext=(2.0, 4.0),
                color='yellow', fontsize=10, weight='bold',
                arrowprops=dict(arrowstyle='->', color='yellow', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#332200', edgecolor='yellow'))
    
    # Dimension line 2: Perpendicular caliper measurement from cam top face to plunger neck = 10.21 mm
    p_plunger_belly = np.array([belly_y[25], belly_z[25]]) # (10.48, 7.50)
    
    # Annotate landmark points
    ax.plot([p_cam_tip_top[0]], [p_cam_tip_top[1]], 'ro', markersize=8)
    ax.text(p_cam_tip_top[0] - 2.5, p_cam_tip_top[1], f'Cam Tip\n({p_cam_tip_top[0]:.2f}, {p_cam_tip_top[1]:.2f})', color='white', fontsize=8)
    
    ax.plot([p_tangent_top[0]], [p_tangent_top[1]], 'go', markersize=8)
    ax.text(p_tangent_top[0] - 1.0, p_tangent_top[1] + 0.8, f'Hub Tangent Top\n({p_tangent_top[0]:.2f}, {p_tangent_top[1]:.2f})', color='white', fontsize=8)
    
    ax.plot([p_plunger_spine[0]], [p_plunger_spine[1]], 'mo', markersize=8)
    ax.text(p_plunger_spine[0] + 0.4, p_plunger_spine[1], f'Lever Spine (Neck)\n({p_plunger_spine[0]:.2f}, {p_plunger_spine[1]:.2f})', color='white', fontsize=8)
    
    # Datum reference lines
    ax.axhline(0.0, color='#888888', linestyle=':', lw=1.2, label='Baseplate Bottom (Z=0.0)')
    ax.axhline(-6.50, color='red', linestyle='--', lw=1.2, label='PCB Switch Contact (Z=-6.5)')
    
    ax.set_xlim(-1, 17)
    ax.set_ylim(-8, 17)
    ax.set_xlabel('Y (mm)', color='white')
    ax.set_ylabel('Z (mm)', color='white')
    ax.tick_params(colors='white')
    ax.grid(True, color='#444444', linestyle=':')
    ax.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    out_png = os.path.join(os.path.dirname(__file__), "rocker_caliper_measurement_diagram.png")
    plt.savefig(out_png, dpi=180)
    print(f"Saved diagram to: {out_png}")

if __name__ == '__main__':
    run()
