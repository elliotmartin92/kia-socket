"""
testing/simulate_blade_10_5mm_kinematics.py
Simulate kinematics with user's measured 10.5mm blade penetration.
"""

import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, HUB_DIAMETER, PLUNGER_REACH_BELOW_Z,
    build_shaft_rocker_mesh
)
import build_part as bp

print("=" * 80)
print("KINEMATICS SIMULATION: 10.5mm BLADE PENETRATION VS ROCKER CAM")
print("=" * 80)

# The current cam polygon at rest:
r_hub = HUB_DIAMETER / 2.0 # 2.10
DZ_CAM = 0.90
poly_pts_cam = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + r_hub),                  # (9.279, 14.690)
    (6.80, 11.50),
    (5.00, 9.80 - DZ_CAM),                     # (5.00, 8.90)
    (1.50, 7.20 - DZ_CAM),                     # (1.50, 6.30)
    (1.80, 5.00 - DZ_CAM),                     # (1.80, 4.10)
    (4.50, 5.20 - DZ_CAM),                     # (4.50, 4.30)
    (Y_AXLE - 1.50, Z_AXLE - 2.50)             # (7.779, 10.090)
]

# Previous cam polygon before DZ_CAM was lowered:
poly_pts_cam_prev = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + r_hub + 0.5),            # (9.279, 15.190)
    (5.00, 9.80),
    (1.50, 7.20),
    (1.80, 5.00),
    (4.50, 5.20),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
]

# Plunger parameters
dy_p = 10.479 - Y_AXLE  # +1.20
dz_p = -6.50 - Z_AXLE   # -19.09
Y_SWITCH_THRESHOLD = 12.40

# Plug blade bounds:
# Center of Hot Blade slot:
# In Y, standard blade width is 6.35mm.
# The pinch throat center of the brass clip in Brackets 3 & 4 is at Y = 0.30mm (or 0.00mm to 2.50mm).
# Let's test blade centered at Y = 0.30mm: Y in [-2.875, 3.475]mm.
# Or blade centered at Y = 1.00mm: Y in [-2.175, 4.175]mm.
# Or blade centered at Y = 2.00mm: Y in [-1.175, 5.175]mm.

for y_blade_c in [0.30, 1.00, 2.00]:
    y_b_min = y_blade_c - 6.35 / 2.0
    y_b_max = y_blade_c + 6.35 / 2.0
    print(f"\n--- BLADE CENTERED AT Y = {y_blade_c:.2f} mm (Y span: [{y_b_min:.2f}, {y_b_max:.2f}]) ---")
    
    # Check contact points on active cam ramp (from (1.50, 6.30) to (5.00, 8.90))
    # At rest:
    p_ramp_bot = np.array([1.50, 6.30])
    p_ramp_top = np.array([5.00, 8.90])
    
    # Overlap along Y between blade and ramp:
    y_over_min = max(y_b_min, 1.50)
    y_over_max = min(y_b_max, 5.00)
    print(f"  Overlap Y with ramp: [{y_over_min:.2f}, {y_over_max:.2f}] mm")
    
    # At rest, Z of ramp at y_over_max:
    t = (y_over_max - 1.50) / (5.00 - 1.50)
    z_at_rest_max = 6.30 + t * (8.90 - 6.30)
    print(f"  Highest point of contact at rest: Y = {y_over_max:.2f} mm, Z = {z_at_rest_max:.2f} mm")
    
    # Check for various blade tip Z elevations:
    # Where does the switch trip?
    # We need Y_plunger >= 12.40 mm:
    # y_plunger = Y_AXLE + cos(theta)*dy_p - sin(theta)*dz_p
    # Let's find theta_trip:
    thetas = np.linspace(0, 15, 1500)
    rads = np.radians(thetas)
    y_plungers = Y_AXLE + np.cos(rads)*dy_p - np.sin(rads)*dz_p
    idx_trip = np.where(y_plungers >= Y_SWITCH_THRESHOLD)[0][0]
    theta_trip = thetas[idx_trip]
    print(f"  Rotation required to trip switch: theta = {theta_trip:.2f}°")
    
    # At theta = theta_trip, where does the ramp move to?
    c_t = np.cos(np.radians(theta_trip))
    s_t = np.sin(np.radians(theta_trip))
    
    # Rotated ramp points:
    def rot_pt(pt, c, s):
        dy = pt[0] - Y_AXLE
        dz = pt[1] - Z_AXLE
        yr = Y_AXLE + c * dy - s * dz
        zr = Z_AXLE + s * dy + c * dz
        return np.array([yr, zr])
    
    p_bot_rot = rot_pt(p_ramp_bot, c_t, s_t)
    p_top_rot = rot_pt(p_ramp_top, c_t, s_t)
    
    # At theta_trip, what is the highest Z of the ramp within the blade Y span?
    # Note: under rotation, Y and Z of ramp both shift!
    print(f"  At switch trip (theta = {theta_trip:.2f}°):")
    print(f"    Ramp bottom moved from (1.50, 6.30) to ({p_bot_rot[0]:.2f}, {p_bot_rot[1]:.2f})")
    print(f"    Ramp top moved from (5.00, 8.90) to ({p_top_rot[0]:.2f}, {p_top_rot[1]:.2f})")
    
    # What Z must the blade tip reach to push the ramp to theta_trip?
    # The blade pushes from above in -Z.
    # The blade's bottom tip must penetrate DOWN TO AT LEAST the rotated ramp elevation!
    # If the blade tip stops at Z_tip, the cam cannot rotate past where the ramp clears Z_tip.
    # At theta_trip, the top of the ramp inside the blade footprint is at:
    t_rot = (min(y_b_max, p_top_rot[0]) - p_bot_rot[0]) / (p_top_rot[0] - p_bot_rot[0])
    z_required_for_trip = p_bot_rot[1] + t_rot * (p_top_rot[1] - p_bot_rot[1])
    print(f"    -> Blade tip MUST reach Z <= {z_required_for_trip:.2f} mm to trip the switch!")
    
    # What if DZ_CAM = 0 (the previous higher cam)?
    p_ramp_top_prev = np.array([5.00, 9.80])
    p_ramp_bot_prev = np.array([1.50, 7.20])
    p_bot_rot_p = rot_pt(p_ramp_bot_prev, c_t, s_t)
    p_top_rot_p = rot_pt(p_ramp_top_prev, c_t, s_t)
    t_rot_p = (min(y_b_max, p_top_rot_p[0]) - p_bot_rot_p[0]) / (p_top_rot_p[0] - p_bot_rot_p[0])
    z_trip_prev = p_bot_rot_p[1] + t_rot_p * (p_top_rot_p[1] - p_bot_rot_p[1])
    print(f"    (With previous higher cam, blade tip only needed Z <= {z_trip_prev:.2f} mm: +{z_trip_prev - z_required_for_trip:.2f} mm higher margin!)")
