"""
testing/simulate_blade_contact_options.py
Simulate and visualize 3 distinct cam profile tweaks to maximize contact area with a straight inserted blade.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER, CAM_WIDTH_X, CAM_X_CENTER

y_axle = Y_AXLE  # 9.279 mm
z_axle = Z_AXLE  # 12.590 mm
r_hub = HUB_DIAMETER / 2.0  # 2.10 mm

# Current straight cam
theta_cam = np.radians(-161.40)
u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)])
u_perp_up = np.array([u_dir[1], -u_dir[0]])
if u_perp_up[1] < 0:
    u_perp_up = -u_perp_up

p_tangent_top = np.array([y_axle, z_axle]) + u_perp_up * r_hub
p_top_tip = p_tangent_top + u_dir * 6.80

fig, axes = plt.subplots(1, 3, figsize=(21, 7), dpi=180)

# Setup blade definition (Straight downward insertion at Y in [4.5, 6.0], moving in -Z)
blade_w_y = 1.50 # 1.5mm blade thickness in Y
blade_y_center = 5.25

options = [
    {
        "title": "Option 1: Widened Strike Paddle (+33% Width in X)\n(Flat 105° Kinematic Ramp)",
        "desc": "Keeps the 105° kinematic slope, but widens cam in X from 2.70mm to 3.60mm.\nIncreases total surface contact area across the 6.35mm blade width.",
        "color": "#1565c0"
    },
    {
        "title": "Option 2: Flat Landing Platform + Lead-In Sled (Dual-Angle)\n(Maximum Planar Surface Contact)",
        "desc": "Creates a flat horizontal seating platform (Y: 4.5-8.6mm) parallel to the flat blade bottom,\nwith an angled 35° entry ramp (Y: 2.0-4.5mm) to catch and guide the blade.",
        "color": "#2e7d32"
    },
    {
        "title": "Option 3: Convex Crowned Cam (R=25mm Tangent Arc)\n(Continuous Line-to-Surface Tangency)",
        "desc": "Gently crowns the top face with an R=25mm convex arc (+0.4mm apex).\nMaintains smooth continuous tangency with the blade across all 0°-10° rotation angles.",
        "color": "#e65100"
    }
]

for ax, opt in zip(axes, options):
    # Draw hub
    phi = np.linspace(0, 2*np.pi, 64)
    ax.plot(y_axle + r_hub*np.cos(phi), z_axle + r_hub*np.sin(phi), color='#546e7a', lw=1.5)
    ax.fill(y_axle + r_hub*np.cos(phi), z_axle + r_hub*np.sin(phi), color='#cfd8dc', alpha=0.5)
    
    # Draw blade
    ax.fill([blade_y_center - blade_w_y/2, blade_y_center + blade_w_y/2, blade_y_center + blade_w_y/2, blade_y_center - blade_w_y/2],
            [13.40, 13.40, 18.50, 18.50], color='#b0bec5', ec='#37474f', lw=1.5, label='Plug Blade (1.5mm thick)')
    ax.plot([blade_y_center - blade_w_y/2, blade_y_center + blade_w_y/2], [13.40, 13.40], 'r-', lw=3, label='Blade Contact Face')
    
    # Draw Cam Profile
    if "Option 1" in opt["title"]:
        # Current linear profile
        ax.plot([p_tangent_top[0], p_top_tip[0]], [p_tangent_top[1], p_top_tip[1]], color=opt["color"], lw=4, label='105° Linear Ramp')
        # Contact line
        ax.plot([4.5, 6.0], [13.4, 13.4], 'go', markersize=6)
        ax.annotate('Line / Edge Contact on Angle\n(Wider 3.60mm span in X)', xy=(5.25, 13.4), xytext=(0.5, 15.5),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color=opt["color"]),
                    fontsize=8.5, fontweight='bold', color=opt["color"], bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=opt["color"]))
        
    elif "Option 2" in opt["title"]:
        # Dual-angle sled
        # Platform: from p_tangent_top (Y=8.6, Z=14.58) to (Y=4.5, Z=13.40) -> horizontal/near-horizontal landing pad
        p_plat_end = np.array([4.50, 13.40])
        p_sled_tip = np.array([2.00, 11.60]) # 35° entry ramp
        
        ax.plot([p_tangent_top[0], p_plat_end[0], p_sled_tip[0]], [p_tangent_top[1], p_plat_end[1], p_sled_tip[1]],
                color=opt["color"], lw=4, label='Flat Platform + Lead-in Sled')
        ax.fill([p_plat_end[0], blade_y_center + blade_w_y/2, blade_y_center - blade_w_y/2, p_plat_end[0]],
                [13.40, 13.40, 13.40, 13.40], color='#81c784', alpha=0.9)
        ax.annotate('Full Planar Face-to-Face Contact\n(Flat seated blade rest)', xy=(5.25, 13.4), xytext=(0.5, 15.5),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color=opt["color"]),
                    fontsize=8.5, fontweight='bold', color=opt["color"], bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=opt["color"]))
        
    elif "Option 3" in opt["title"]:
        # Crowned convex arc
        t = np.linspace(0, 1, 40)
        cy = (1-t)*p_tangent_top[0] + t*p_top_tip[0] + 4*t*(1-t)*u_perp_up[0]*0.55
        cz = (1-t)*p_tangent_top[1] + t*p_top_tip[1] + 4*t*(1-t)*u_perp_up[1]*0.55
        ax.plot(cy, cz, color=opt["color"], lw=4, label='Crowned R=25mm Convex Arc')
        ax.annotate('Smooth Tangent Rolling Contact\n(Zero edge-gouge / low friction)', xy=(5.25, 13.4), xytext=(0.5, 15.5),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color=opt["color"]),
                    fontsize=8.5, fontweight='bold', color=opt["color"], bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=opt["color"]))
        
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(9.0, 19.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title(opt["title"], fontsize=10, fontweight='bold')
    ax.set_xlabel("Y (mm)")
    ax.set_ylabel("Z (mm)")
    ax.legend(loc='lower left', fontsize=8)

plt.tight_layout()
plt.savefig('testing/blade_contact_options_comparison.png', dpi=180)
print("Saved testing/blade_contact_options_comparison.png")
