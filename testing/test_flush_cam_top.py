"""
testing/test_flush_cam_top.py
Test making the input cam flush with the top apex of the shaft cylinder.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import matplotlib.pyplot as plt

Y_AXLE = 10.200
Z_AXLE = 12.590
HUB_D = 4.20
R_HUB = HUB_D / 2.0  # 2.10 mm

# Top apex of shaft cylinder
Z_TOP_SHAFT = Z_AXLE + R_HUB  # 14.690 mm

# Plunger centerline angle
v_p = np.array([11.40 - Y_AXLE, -6.50 - Z_AXLE]) # [1.20, -19.09]
theta_p = np.degrees(np.arctan2(v_p[1], v_p[0])) # -86.40 deg

# We want:
# 1. Top face of input cam is FLUSH with top of shaft (Z = Z_TOP_SHAFT = 14.690 mm at Y = Y_AXLE)
# 2. Arm extends forward/downward at 105° bellcrank angle relative to plunger
# 3. Smooth tangential blend into the top of the cylinder (0 step, 100% flush!)

# Let's explore geometric constructions for flush top:
# Option 1: Tangent from top of cylinder (Y_AXLE, Z_AXLE + R_HUB)
# Angle of cam direction: theta_cam = -161.40° (105° bellcrank angle from plunger)
# Or slope of upper surface:
# If top surface starts at (Y_AXLE, Z_AXLE + R_HUB) = (10.200, 14.690)
# and slopes down along the 105° angle direction:
# dir_cam = [cos(-161.4°), sin(-161.4°)] = [-0.948, -0.319]
# Upper surface: P_top(s) = (Y_AXLE, Z_AXLE + R_HUB) + dir_cam * s
# Cam tip at s = 6.80mm -> Y_tip = 10.200 - 0.948 * 6.80 = 3.75mm
# Z_tip = 14.690 - 0.319 * 6.80 = 12.52mm (or dropping towards contact nose)

# Let's check how the polygon should be built:
# Let's test a continuous polygon that includes:
# - Circle at (Y_AXLE, Z_AXLE) with radius R_HUB
# - Top line starting at (Y_AXLE + R_HUB*cos(alpha_top), Z_AXLE + R_HUB*sin(alpha_top)) where alpha_top = 90° (top apex) or tangent
# - Contact tip nose at (Y_tip, Z_tip)
# - Bottom line connecting back tangentially to the cylinder at bottom

# Let's write a function to construct the flush polygon and plot it
def create_flush_cam_poly(cam_angle_deg=-161.4, cam_reach=6.80, cam_thick=2.80):
    rad = np.radians(cam_angle_deg)
    u_dir = np.array([np.cos(rad), np.sin(rad)]) # direction along arm
    u_norm = np.array([-u_dir[1], u_dir[0]])     # normal pointing towards top surface
    
    # We want top surface of arm to be tangent to or flush with top of cylinder at Z = Z_AXLE + R_HUB
    # The top surface line equation: Point on line is (Y_AXLE, Z_AXLE) + u_norm * R_HUB
    # Notice: u_norm * R_HUB is on the cylinder circumference!
    # At theta = -161.4°, u_norm is [0.319, -0.948] -> wait! u_norm points in +Y, -Z if not flipped.
    # Let's make sure u_norm points upward (+Z, -Y):
    # u_dir is [-0.948, -0.319] (pointing -Y, -Z)
    # Perpendicular pointing upward: u_perp_up = [u_dir[1], -u_dir[0]] = [-0.319, 0.948] (points +Z, -Y)
    u_perp_up = np.array([u_dir[1], -u_dir[0]])
    if u_perp_up[1] < 0:
        u_perp_up = -u_perp_up
        
    # Tangent contact point on cylinder top:
    p_tangent_top = np.array([Y_AXLE, Z_AXLE]) + u_perp_up * R_HUB
    # Top line extends from p_tangent_top along u_dir:
    p_top_tip = p_tangent_top + u_dir * cam_reach
    
    # Bottom line is offset by cam_thick:
    p_bot_tip = p_top_tip - u_perp_up * cam_thick
    p_tangent_bot = p_tangent_top - u_perp_up * cam_thick
    
    # Rounded tip between p_top_tip and p_bot_tip
    half_t = cam_thick / 2.0
    p_tip_mid = (p_top_tip + p_bot_tip) / 2.0
    tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_tip_mid + u_dir * (half_t * np.cos(a)) + u_perp_up * (half_t * np.sin(a))
        tip_pts.append((pt[0], pt[1]))
        
    # Also include cylinder arc on rear/top from p_tangent_bot around to p_tangent_top
    # Or unary_union with cylinder circle:
    poly_arm = Polygon([p_tangent_top] + tip_pts + [p_tangent_bot, p_tangent_top])
    poly_hub = Point(Y_AXLE, Z_AXLE).buffer(R_HUB)
    poly_cam = unary_union([poly_hub, poly_arm])
    
    return poly_cam, p_tangent_top, p_top_tip, p_tip_mid

fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=180)

# Compare main (non-flush) vs new flush design
for ax, mode in zip(axes, ["Non-Flush (Previous)", "100% Flush with Shaft Top (New)"]):
    phi = np.linspace(0, 2*np.pi, 100)
    ax.plot(Y_AXLE + R_HUB*np.cos(phi), Z_AXLE + R_HUB*np.sin(phi), 'b-', lw=2, label=f'Shaft Hub (Ø{HUB_D}mm)')
    ax.axhline(Z_TOP_SHAFT, color='#d32f2f', linestyle='--', lw=1.5, label=f'Shaft Top Apex (Z={Z_TOP_SHAFT:.2f}mm)')
    ax.plot(Y_AXLE, Z_AXLE, 'ro', markersize=6)
    
    if mode.startswith("Non-Flush"):
        # Previous cam
        theta_cam = np.radians(-161.40)
        dir_cam = np.array([np.cos(theta_cam), np.sin(theta_cam)])
        norm_cam = np.array([-dir_cam[1], dir_cam[0]])
        p_c = np.array([Y_AXLE, Z_AXLE]) + dir_cam * 6.80
        p1 = np.array([Y_AXLE, Z_AXLE]) + norm_cam * 1.40
        p2 = p_c + norm_cam * 1.40
        p3 = p_c - norm_cam * 1.40
        p4 = np.array([Y_AXLE, Z_AXLE]) - norm_cam * 1.40
        poly_old = unary_union([Point(Y_AXLE, Z_AXLE).buffer(R_HUB), Polygon([p1, p2, p3, p4, p1])])
        cx, cy = poly_old.exterior.xy
        ax.fill(cx, cy, color='#ff9800', alpha=0.6, ec='#e65100', lw=2, label='Cam on Main (Gap/Step below top)')
        ax.annotate(f'Step down: {Z_TOP_SHAFT - p1[1]:.2f}mm gap!', xy=(p1[0], p1[1]), xytext=(p1[0] + 1.5, p1[1] + 1.5),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2), fontweight='bold', color='red')
    else:
        poly_flush, p_tan_top, p_top_tip, p_mid = create_flush_cam_poly(-161.4, 6.80, 2.80)
        cx, cy = poly_flush.exterior.xy
        ax.fill(cx, cy, color='#4caf50', alpha=0.7, ec='#2e7d32', lw=2, label='100% Flush Top Cam (New)')
        ax.annotate('100% Flush with Shaft Top!\n(Zero step, continuous top surface)', xy=(p_tan_top[0], p_tan_top[1]),
                    xytext=(p_tan_top[0] - 3.5, p_tan_top[1] + 1.2),
                    arrowprops=dict(arrowstyle='->', color='#1b5e20', lw=2), fontweight='bold', color='#1b5e20',
                    bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
        
    ax.set_xlim(2, 14)
    ax.set_ylim(6, 17)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title(mode, fontsize=11, fontweight='bold')
    ax.set_xlabel('Y (mm)')
    ax.set_ylabel('Z (mm)')
    ax.legend(loc='lower left', fontsize=8.5)

plt.tight_layout()
out_png = 'testing/flush_cam_top_comparison.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
