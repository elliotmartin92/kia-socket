"""
testing/test_105deg_cam_direct_off_shaft.py
Test and verify 105 degree input cam coming directly off the shaft cylinder.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt

Y_AXLE = 10.200
Z_AXLE = 12.590
PIN_D = 2.80
HUB_D = 4.20
R_HUB = HUB_D / 2.0  # 2.10mm

# Plunger centerline angle
v_p = np.array([11.40 - Y_AXLE, -6.50 - Z_AXLE])
theta_p = np.degrees(np.arctan2(v_p[1], v_p[0])) # -86.40 deg

# 105 degree bellcrank angle:
# Angle between plunger axis and cam axis = 105.0 deg
# theta_cam = theta_p - 105.0 = -191.40 deg = +168.60 deg
# Or if theta_p is along the vertical -90 deg: theta_cam = -90 - 105 = -195 deg = +165 deg
# Let's test exact 105 deg from plunger:
theta_cam_deg = theta_p - 105.0  # -191.40 deg
rad_cam = np.radians(theta_cam_deg)
dir_cam = np.array([np.cos(rad_cam), np.sin(rad_cam)]) # [-0.980, 0.198]
normal_cam = np.array([-dir_cam[1], dir_cam[0]])       # [-0.198, -0.980]

# Arm parameters
arm_length = 7.00 # Reach from shaft center along 105 deg direction
arm_thick = 2.80  # 2.80mm arm thickness
half_t = arm_thick / 2.0

# 4 corners of the rectangular arm extending directly from the shaft center to the tip
p_tip_center = np.array([Y_AXLE, Z_AXLE]) + dir_cam * arm_length
p1 = np.array([Y_AXLE, Z_AXLE]) + normal_cam * half_t
p2 = p_tip_center + normal_cam * half_t
# Rounded / filleted tip
tip_pts = []
for a in np.linspace(np.pi/2, -np.pi/2, 17):
    # Tip semicircle of radius half_t
    pt = p_tip_center + dir_cam * (half_t * np.cos(a)) + normal_cam * (half_t * np.sin(a))
    tip_pts.append((pt[0], pt[1]))

p3 = p_tip_center - normal_cam * half_t
p4 = np.array([Y_AXLE, Z_AXLE]) - normal_cam * half_t

poly_arm = Polygon([p1] + tip_pts + [p4, p1])
poly_hub = Point(Y_AXLE, Z_AXLE).buffer(R_HUB)
poly_cam_direct = unary_union([poly_hub, poly_arm])

fig, ax = plt.subplots(figsize=(10, 8), dpi=180)

# Hub
phi = np.linspace(0, 2*np.pi, 100)
ax.plot(Y_AXLE + R_HUB*np.cos(phi), Z_AXLE + R_HUB*np.sin(phi), 'b--', lw=1.5, label=f'Shaft Hub (Ø{HUB_D}mm)')
ax.plot(Y_AXLE, Z_AXLE, 'ro', markersize=6, label='Pivot Center')

# Direct 105 deg cam
cx, cy = poly_cam_direct.exterior.xy
ax.fill(cx, cy, color='#4caf50', alpha=0.7, edgecolor='#2e7d32', lw=2, label='105° Input Cam (Direct off Shaft)')

# Draw centerline
ax.plot([Y_AXLE, p_tip_center[0]], [Z_AXLE, p_tip_center[1]], 'r-.', lw=2, label=f'Cam Axis (105° from Plunger)')
ax.plot([Y_AXLE, Y_AXLE + v_p[0]], [Z_AXLE, Z_AXLE + v_p[1]], 'm-.', lw=2, label=f'Plunger Axis')

# Annotations
angle_actual = np.degrees(np.arccos(np.dot(dir_cam, v_p / np.linalg.norm(v_p))))
ax.annotate(f'Exact Angle: {angle_actual:.1f}°', xy=(Y_AXLE - 1.5, Z_AXLE - 1.5),
            fontsize=12, fontweight='bold', color='#1565c0',
            bbox=dict(boxstyle='round,pad=0.3', fc='#e3f2fd', ec='#1565c0'))

ax.set_xlim(2, 14)
ax.set_ylim(-8, 16)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title("Direct 105° Input Cam Attached Directly to Shaft", fontsize=12, fontweight='bold')
ax.set_xlabel('Y (mm)')
ax.set_ylabel('Z (mm)')
ax.legend(loc='lower left', fontsize=8.5)

plt.tight_layout()
out_png = 'testing/direct_105deg_cam_preview.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
print(f"Angle between arms: {angle_actual:.2f}°")
print(f"Cam tip position: ({p_tip_center[0]:.3f}, {p_tip_center[1]:.3f})")
