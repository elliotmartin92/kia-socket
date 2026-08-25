"""
testing/analyze_blade_cam_contact.py
Analyze the kinematic contact between the straight inserted plug blade and the rocker input cam tab:
- Blade insertion trajectory (moving in -Z or +Y)
- Cam surface angle vs blade face
- Contact line / patch throughout rotation (0° to 10° actuation)
- Cam width and profile options (flat vs crowned vs widened paddle)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box

from build_shaft import (
    Y_AXLE, Z_AXLE, CAM_WIDTH_X, CAM_X_CENTER,
    HUB_DIAMETER, TOTAL_AXLE_LEN, HUB_WIDTH
)

y_axle = Y_AXLE  # 9.279 mm
z_axle = Z_AXLE  # 12.590 mm
r_hub = HUB_DIAMETER / 2.0  # 2.10 mm

# Current cam definition
theta_cam = np.radians(-161.40)
u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)])
u_perp_up = np.array([u_dir[1], -u_dir[0]])
if u_perp_up[1] < 0:
    u_perp_up = -u_perp_up

cam_reach = 6.80
cam_thick = 2.80

p_tangent_top = np.array([y_axle, z_axle]) + u_perp_up * r_hub
p_top_tip = p_tangent_top + u_dir * cam_reach

print("=== Current Input Cam Geometry ===")
print(f"Shaft Center: (Y={y_axle:.3f}, Z={z_axle:.3f})")
print(f"Cam top tangent start: (Y={p_tangent_top[0]:.3f}, Z={p_tangent_top[1]:.3f})")
print(f"Cam top tip: (Y={p_top_tip[0]:.3f}, Z={p_top_tip[1]:.3f})")
print(f"Cam angle from horizontal: {np.degrees(theta_cam):.2f}° (Slope = {u_dir[1]/u_dir[0]:.3f})")
print(f"Cam reach: {cam_reach:.2f} mm, Width in X: {CAM_WIDTH_X:.2f} mm")

# Kinematic stroke analysis (0° to 10° rotation)
print("\n=== Kinematic Stroke (Straight Blade Moving in -Z) ===")
angles = [0, 2, 4, 6, 8, 10]
for deg in angles:
    rad = np.radians(deg)
    # Rotate cam around shaft axis
    # Rotation matrix for CW rotation
    rot = np.array([[np.cos(rad), np.sin(rad)], [-np.sin(rad), np.cos(rad)]])
    p_tip_rot = np.array([y_axle, z_axle]) + rot @ (p_top_tip - np.array([y_axle, z_axle]))
    cam_angle_rot = np.degrees(theta_cam) + deg
    print(f"Rotation {deg:2d}° CW: Cam Tip = (Y={p_tip_rot[0]:.2f}, Z={p_tip_rot[1]:.2f}), Surface Slope = {cam_angle_rot:.2f}°")

# Plot 2D Kinematic Contact Simulation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=180)

# Left: Current Flat Cam with Straight Blade
phi = np.linspace(0, 2*np.pi, 64)
ax1.plot(y_axle + r_hub*np.cos(phi), z_axle + r_hub*np.sin(phi), 'b-', lw=1.5, label='Shaft Hub (Ø4.2mm)')

# Draw cam at 0 deg, 5 deg, 10 deg
for deg, col, style in [(0, '#ff9800', '-'), (5, '#f57c00', '--'), (10, '#e65100', ':')]:
    rad = np.radians(deg)
    rot = np.array([[np.cos(rad), np.sin(rad)], [-np.sin(rad), np.cos(rad)]])
    p_start = np.array([y_axle, z_axle]) + rot @ (p_tangent_top - np.array([y_axle, z_axle]))
    p_end = np.array([y_axle, z_axle]) + rot @ (p_top_tip - np.array([y_axle, z_axle]))
    ax1.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]], color=col, linestyle=style, lw=3, label=f'Cam at {deg}° rotation')

# Draw straight vertical plug blade (inserted along -Z at Y = 5.0mm)
blade_y = 5.0
ax1.fill([blade_y - 0.75, blade_y + 0.75, blade_y + 0.75, blade_y - 0.75], [10.0, 10.0, 18.0, 18.0],
         color='#78909c', alpha=0.7, ec='#37474f', lw=1.5, label='Plug Blade (1.5mm thick, straight -Z insertion)')
ax1.annotate('Straight Plug Blade Insertion\n(Pushes down in -Z)', xy=(blade_y, 11.5), xytext=(blade_y - 4.5, 15.5),
             arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', width=2, headwidth=6),
             fontweight='bold', color='#b71c1c', fontsize=9, bbox=dict(boxstyle='round,pad=0.3', fc='#ffebee', ec='#b71c1c'))

ax1.set_xlim(-1.0, 14.0)
ax1.set_ylim(8.0, 19.0)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title("1. Current Straight Ramp Contact Kinematics", fontsize=11, fontweight='bold')
ax1.set_xlabel("Y (mm)")
ax1.set_ylabel("Z (mm)")
ax1.legend(loc='lower right', fontsize=8)

# Right: Comparison of Contact Surface Tweaks
ax2.plot(y_axle + r_hub*np.cos(phi), z_axle + r_hub*np.sin(phi), 'b-', lw=1.5)

# Option A: Current Flat Ramp
ax2.plot([p_tangent_top[0], p_top_tip[0]], [p_tangent_top[1], p_top_tip[1]], 'r--', lw=2, label='Current: Flat Linear Ramp (Edge Contact)')

# Option B: Crowned / Convex Curved Cam (Continuous Tangency)
# A gentle convex arc R=15-20mm on top face
t_pts = np.linspace(0, 1, 33)
# Bezier or circular arc with 0.40mm crown
curve_y = (1-t_pts)*p_tangent_top[0] + t_pts*p_top_tip[0] + 4*t_pts*(1-t_pts)*u_perp_up[0]*0.50
curve_z = (1-t_pts)*p_tangent_top[1] + t_pts*p_top_tip[1] + 4*t_pts*(1-t_pts)*u_perp_up[1]*0.50
ax2.plot(curve_y, curve_z, 'g-', lw=3, label='Option A: Crowned Convex Arc (+0.5mm Crown / Tangent Contact)')

# Option C: Optimized Angle + Dual-Facet Sled (Lead-in + Flat Strike Platform)
p_mid = (p_tangent_top + p_top_tip) / 2.0
# Horizontal / angled landing pad
p_plat_start = p_tangent_top
p_plat_end = p_tangent_top + u_dir * 4.0 - u_perp_up * 0.10
p_leadin_tip = p_plat_end + np.array([-2.5, -1.8]) # steeper lead-in ramp
ax2.plot([p_plat_start[0], p_plat_end[0], p_leadin_tip[0]], [p_plat_start[1], p_plat_end[1], p_leadin_tip[1]],
         'm-', lw=3, label='Option B: Strike Platform + Guided Lead-in Sled')

ax2.set_xlim(-1.0, 14.0)
ax2.set_ylim(8.0, 19.0)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_title("2. Cam Contact Optimization Options", fontsize=11, fontweight='bold')
ax2.set_xlabel("Y (mm)")
ax2.set_ylabel("Z (mm)")
ax2.legend(loc='lower right', fontsize=8)

plt.tight_layout()
plt.savefig('testing/blade_cam_contact_analysis.png', dpi=180)
print("Saved testing/blade_cam_contact_analysis.png")
