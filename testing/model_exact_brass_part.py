"""
testing/model_exact_brass_part.py
Constructs exact 3D parametric geometry of the OEM brass pinching contact from the user's caliper dimensions:
- D1a = 5.0 mm (internal gap at widest belly)
- D1b = 1.0 mm (throat gap at pinch contact)
- D2 = 14.4 mm (total height from base seating shelf to top tips)
- D4 = 8.4 mm (height from base to pinch throat)
- D5 = 4.3 mm (flare opening at top tips)
- D3 = 6.74 mm (strip width in X)
- Horizontal gap: 2.7 mm from Left Tower top front (Y = 6.55 mm) -> Rear flare at Y = 3.85 mm
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER
)
from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    TOWER_HEIGHT, BASE_THICK
)

# Caliper Dimensions from User
D1A = 5.00   # Wide internal gap in Y
D1B = 1.00   # Pinch throat gap in Y
D2  = 14.40  # Total height in Z above seating shelf
D4  = 8.40   # Throat elevation in Z above seating shelf
D5  = 4.30   # Top flare opening in Y
D3  = 6.74   # Strip width in X

SHEET_THICK = 0.50  # Standard automotive contact spring brass thickness (~0.50 mm)

def get_brass_contact_2d_profile():
    """
    Constructs the exact 2D centerline profile of the brass contact in (Y, Z).
    Seating shelf is at Z = BASE_THICK = 1.00 mm.
    Rear flare edge at top (Z = 1.0 + 14.4 = 15.40 mm) is at Y = 6.550 - 2.700 = 3.850 mm.
    """
    z_base = BASE_THICK # 1.00 mm
    z_top = z_base + D2 # 15.40 mm
    z_throat = z_base + D4 # 9.40 mm
    z_belly = z_base + D4 * 0.50 # ~5.20 mm
    
    y_rear_top = 6.550 - 2.700 # 3.850 mm (outer face of rear flare)
    # If D5 is inner opening (4.30mm) -> center is y_rear_top - SHEET_THICK - D5/2 = 3.85 - 0.5 - 2.15 = 1.20 mm
    y_center = y_rear_top - SHEET_THICK/2.0 - D5/2.0 # 1.45 mm
    
    # Coordinates of Front Arm (centerline)
    # At top (Z = 15.40): Y = y_center - D5/2 = -0.70 mm
    # At throat (Z = 9.40): Y = y_center - D1b/2 = 1.45 - 0.50 = 0.95 mm
    # At belly (Z = 5.20): Y = y_center - D1a/2 = 1.45 - 2.50 = -1.05 mm
    # At base (Z = 1.00): Y = y_center - D1a/2 = -1.05 mm
    
    # Coordinates of Rear Arm (centerline)
    # At top (Z = 15.40): Y = y_center + D5/2 = 3.60 mm (outer face = 3.85 mm)
    # At throat (Z = 9.40): Y = y_center + D1b/2 = 1.45 + 0.50 = 1.95 mm
    # At belly (Z = 5.20): Y = y_center + D1a/2 = 1.45 + 2.50 = 3.95 mm
    # At base (Z = 1.00): Y = y_center + D1a/2 = 3.95 mm
    
    front_arm_pts = [
        (y_center - D1A/2.0, z_base),
        (y_center - D1A/2.0, z_belly),
        (y_center - D1B/2.0, z_throat),
        (y_center - D5/2.0, z_top)
    ]
    
    rear_arm_pts = [
        (y_center + D1A/2.0, z_base),
        (y_center + D1A/2.0, z_belly),
        (y_center + D1B/2.0, z_throat),
        (y_center + D5/2.0, z_top)
    ]
    
    return front_arm_pts, rear_arm_pts, y_center

def run():
    print("=== EXACT BRASS CONTACT MODELING & INTERACTION ANALYSIS ===")
    front_pts, rear_pts, y_c = get_brass_contact_2d_profile()
    
    print(f"Brass Contact Dimensions:")
    print(f"  Width in X:       {D3:.2f} mm (Spanning X in [{6.28 - D3/2:.2f}, {6.28 + D3/2:.2f}] mm)")
    print(f"  Total Height:     {D2:.2f} mm (Z in [{BASE_THICK:.2f}, {BASE_THICK + D2:.2f}] mm)")
    print(f"  Throat Height:    {D4:.2f} mm (Z = {BASE_THICK + D4:.2f} mm)")
    print(f"  Internal Belly:   {D1A:.2f} mm in Y (Z in [{BASE_THICK:.2f}, {BASE_THICK + D4*0.5:.2f}] mm)")
    print(f"  Throat Pinch Gap: {D1B:.2f} mm in Y (Z = {BASE_THICK + D4:.2f} mm)")
    print(f"  Top Flare Width:  {D5:.2f} mm in Y (Z = {BASE_THICK + D2:.2f} mm)")
    print(f"  Rear Flare Apex:  Y = {rear_pts[-1][0] + SHEET_THICK/2:.3f} mm")
    print(f"  Front Flare Apex: Y = {front_pts[-1][0] - SHEET_THICK/2:.3f} mm")
    
    # Now let's analyze the Rocker Cam inside this gap:
    # Cam tab in build_shaft.py:
    # Axis: Y = 9.279 mm, Z = 12.590 mm
    # Angle: -161.40 deg, Reach = 6.80 mm
    # Cam top tip: Y ~ 2.834 mm, Z ~ 10.422 mm (plus 0.45mm crown -> Y ~ 2.70, Z ~ 10.85 mm)
    # Cam bottom tip: Y ~ 3.73 mm, Z ~ 7.76 mm
    
    print("\n--- CAM TAB LOCATION VS BRASS GAP ---")
    print(f"  Shaft Axle:     Y = {Y_AXLE:.3f} mm, Z = {Z_AXLE:.3f} mm")
    print(f"  Cam Tip:        Y ~ 2.83 mm, Z ~ 10.42 mm (reaches into Z = 7.76 to 10.85 mm)")
    print(f"  Brass Rear Arm: At Z = 10.42 mm, Y_rear ~ 2.50 mm")
    print(f"  Brass Throat:   At Z = 9.40 mm, Y_throat = {rear_pts[2][0]:.2f} mm")
    print(f"  Brass Belly:    At Z = 5.20 mm, Y_belly = {rear_pts[1][0]:.2f} mm")
    
    # Plot detailed 2D profile
    fig, ax = plt.subplots(figsize=(14, 11), facecolor='#1a1a1a', dpi=180)
    ax.set_facecolor('#222222')
    ax.set_title("Exact OEM Brass Contact & Safety Rocker Assembly Profile (Y-Z Plane)", color='white', fontsize=13, weight='bold', pad=15)
    
    # 1. Floor & Brackets
    ax.add_patch(patches.Rectangle((-10, 0), 28, 1.0, color='#888888', alpha=0.5, label='Baseplate Floor (Z=1.00mm)'))
    ax.add_patch(patches.Rectangle((-7.17, 1.0), 14.34, 3.60, color='#2ecc71', alpha=0.25, edgecolor='#27ae60', lw=1.5, label='Bracket Walls (Z=4.60mm)'))
    
    # 2. Left Tower Profile (Z_top = 14.09 mm, Top Y in [6.55, 12.18])
    tower_yz = [(6.25, 1.0), (12.85, 1.0), (12.18, 14.09), (6.55, 14.09)]
    ax.add_patch(patches.Polygon(tower_yz, color='#3498db', alpha=0.3, edgecolor='#2980b9', lw=1.5, label='Left Tower (Z_top = 14.09mm)'))
    
    # 3. Exact Brass Contact Profile (Formed Sheet Metal)
    t_half = SHEET_THICK / 2.0
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    
    ax.add_patch(patches.Polygon(f_poly_pts, color='#f39c12', alpha=0.8, edgecolor='#d68910', lw=2, label='Brass Front Spring Arm'))
    ax.add_patch(patches.Polygon(r_poly_pts, color='#f39c12', alpha=0.8, edgecolor='#d68910', lw=2, label='Brass Rear Spring Arm'))
    
    # Connecting bottom base plate of brass part
    ax.add_patch(patches.Rectangle((front_pts[0][0] - t_half, 1.0), (rear_pts[0][0] - front_pts[0][0]) + SHEET_THICK, 1.0, color='#f39c12', alpha=0.8))
    
    # 4. Rocker Lever: Hub, Cam Tab, Plunger
    r_hub = HUB_DIAMETER / 2.0 # 2.10 mm
    ax.add_patch(patches.Circle((Y_AXLE, Z_AXLE), r_hub, color='#e67e22', alpha=0.6, edgecolor='#d35400', lw=2, label='Hub Barrel (Ø4.20mm)'))
    ax.plot([Y_AXLE], [Z_AXLE], 'o', color='cyan', markersize=6, label='Shaft Axis (9.28, 12.59)')
    
    # Plunger
    z_tip = -6.50
    r_tip = 1.00
    plunger_y_center = 10.479
    N = 50
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (Y_AXLE + r_hub) + 2*(1-t)*t * (Y_AXLE + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (Z_AXLE - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    belly_y = (1-t)**2 * (Y_AXLE - r_hub) + 2*(1-t)*t * (Y_AXLE + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (Z_AXLE - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    ax.add_patch(patches.Polygon(pts_plunger, color='#f1c40f', alpha=0.4, edgecolor='#f39c12', lw=1.5, label='Plunger (Z ≤ -6.50mm)'))
    
    # Current Cam Tab
    theta_cam = np.radians(-161.40)
    u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)])
    u_perp_up = np.array([u_dir[1], -u_dir[0]])
    if u_perp_up[1] < 0:
        u_perp_up = -u_perp_up
    cam_reach = 6.80
    cam_arm_thick = 2.80
    p_tangent_top = np.array([Y_AXLE, Z_AXLE]) + u_perp_up * r_hub
    p_top_tip = p_tangent_top + u_dir * cam_reach
    p_bot_tip = p_top_tip - u_perp_up * cam_arm_thick
    p_tangent_bot = p_tangent_top - u_perp_up * cam_arm_thick
    t_crown = np.linspace(0, 1, 33)
    cam_top_crowned = []
    for tc in t_crown:
        pt = (1-tc)*p_tangent_top + tc*p_top_tip + 4*tc*(1-tc)*u_perp_up*0.45
        cam_top_crowned.append((pt[0], pt[1]))
    half_t = cam_arm_thick / 2.0
    p_tip_mid = (p_top_tip + p_bot_tip) / 2.0
    cam_tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_tip_mid + u_dir * (half_t * np.cos(a)) + u_perp_up * (half_t * np.sin(a))
        cam_tip_pts.append((pt[0], pt[1]))
    poly_cam_arm_pts = cam_top_crowned + cam_tip_pts + [p_tangent_bot, p_tangent_top]
    ax.add_patch(patches.Polygon(poly_cam_arm_pts, color='#e74c3c', alpha=0.6, edgecolor='#c0392b', lw=2, label='Current Cam Tab'))
    
    # 5. Dimension Annotations
    # D2 = 14.4 mm total height
    ax.annotate('', xy=(-3.5, 1.0), xytext=(-3.5, 1.0 + D2),
                arrowprops=dict(arrowstyle='<->', color='#f39c12', lw=2))
    ax.text(-3.8, 1.0 + D2/2, f'D2 = {D2:.1f} mm\n(Total Height)', color='#f39c12', fontsize=9, weight='bold', ha='right', va='center')
    
    # D4 = 8.4 mm throat height
    ax.annotate('', xy=(-2.0, 1.0), xytext=(-2.0, 1.0 + D4),
                arrowprops=dict(arrowstyle='<->', color='#f39c12', lw=1.5))
    ax.text(-1.8, 1.0 + D4/2, f'D4 = {D4:.1f} mm\n(Throat Height)', color='#f39c12', fontsize=8, weight='bold', ha='left', va='center')
    
    # D1a = 5.0 mm wide belly gap
    ax.annotate('', xy=(front_pts[1][0], 5.2), xytext=(rear_pts[1][0], 5.2),
                arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
    ax.text((front_pts[1][0] + rear_pts[1][0])/2, 5.7, f'D1a = {D1A:.1f} mm\n(Internal Gap)', color='yellow', fontsize=9, weight='bold', ha='center')
    
    # D1b = 1.0 mm throat gap
    ax.annotate('', xy=(front_pts[2][0], 9.4), xytext=(rear_pts[2][0], 9.4),
                arrowprops=dict(arrowstyle='<->', color='yellow', lw=1.5))
    ax.text((front_pts[2][0] + rear_pts[2][0])/2, 10.0, f'D1b = {D1B:.1f} mm', color='yellow', fontsize=8, weight='bold', ha='center')
    
    # D5 = 4.3 mm top flare
    ax.annotate('', xy=(front_pts[3][0], 15.4), xytext=(rear_pts[3][0], 15.4),
                arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
    ax.text((front_pts[3][0] + rear_pts[3][0])/2, 16.0, f'D5 = {D5:.1f} mm (Flare)', color='yellow', fontsize=9, weight='bold', ha='center')
    
    # 2.7 mm gap to Left Tower
    ax.plot([rear_pts[3][0] + t_half, 6.550], [14.09, 14.09], color='cyan', lw=2.5, marker='|', markersize=10)
    ax.text((rear_pts[3][0] + t_half + 6.55)/2, 14.5, '2.70 mm Gap', color='cyan', fontsize=9, weight='bold', ha='center')
    
    ax.set_xlim(-6, 17)
    ax.set_ylim(-8, 18)
    ax.set_xlabel('Y (mm)', color='white')
    ax.set_ylabel('Z (mm)', color='white')
    ax.tick_params(colors='white')
    ax.grid(True, color='#444444', linestyle=':')
    ax.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "exact_brass_and_cam_profile.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved exact analysis plot to: {out_png}")

if __name__ == '__main__':
    run()
