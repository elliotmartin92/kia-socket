"""
testing/plot_bellcrank_angle_options.py
Generate visual comparison of different bellcrank angle options between input cam and output plunger.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

Y_AXLE = 10.200
Z_AXLE = 12.590
HUB_D = 4.20
R_HUB = HUB_D / 2.0

fig, axes = plt.subplots(1, 3, figsize=(21, 7.5), dpi=180)

# Plunger profile (fixed reach to Z = -6.50mm inside through hole)
z_tip = -6.50
r_tip = 1.00
plunger_y_center = 11.40
N = 50
t = np.linspace(0, 1, N)
spine_y = (1-t)**2 * (Y_AXLE + R_HUB) + 2*(1-t)*t * (Y_AXLE + 3.80) + t**2 * (plunger_y_center + r_tip)
spine_z = (1-t)**2 * (Z_AXLE - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
belly_y = (1-t)**2 * (Y_AXLE - R_HUB) + 2*(1-t)*t * (Y_AXLE + 1.20) + t**2 * (plunger_y_center - r_tip)
belly_z = (1-t)**2 * (Z_AXLE - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
tip_angles = np.linspace(0, np.pi, 33)
tip_y = plunger_y_center + r_tip * np.cos(tip_angles)
tip_z = z_tip + r_tip * (1 - np.sin(tip_angles))

pts_plunger = np.column_stack([
    np.concatenate([spine_y, [plunger_y_center + r_tip], tip_y, [plunger_y_center - r_tip], belly_y[::-1]]),
    np.concatenate([spine_z, [z_tip + r_tip], tip_z, [z_tip + r_tip], belly_z[::-1]])
])

# Three Cam Angle Options:
# Option 1: Steeper / OEM branch angle (~105° relative to vertical, reaches Y=5.70, Z=6.79)
# Option 2: Flatter / More forward angle (~120° relative to vertical, reaches Y=4.80, Z=7.50)
# Option 3: Upright / Tighter angle (~90° relative to vertical, reaches Y=6.50, Z=6.00)

cam_configs = [
    {
        "title": "Option A: OEM Branch Angle (~105° bellcrank angle)\nReaches Y = 5.70mm, Z = 6.79mm (Drops -5.80mm below axle)",
        "tip_y": Y_AXLE - 4.50, "tip_z": Z_AXLE - 5.80,
        "upper_y": Y_AXLE - 4.50, "upper_z": Z_AXLE - 5.80 + 2.40,
        "lower_y": Y_AXLE - 4.50 + 3.00, "lower_z": Z_AXLE - 5.80,
        "desc": "Direct 1:1 match with OEM branch geometry. Deep engagement into slider pocket."
    },
    {
        "title": "Option B: Moderate Angle (~95° bellcrank angle)\nReaches Y = 6.20mm, Z = 5.80mm (Drops -6.79mm below axle)",
        "tip_y": Y_AXLE - 4.00, "tip_z": Z_AXLE - 6.79,
        "upper_y": Y_AXLE - 4.00, "upper_z": Z_AXLE - 6.79 + 2.40,
        "lower_y": Y_AXLE - 4.00 + 2.80, "lower_z": Z_AXLE - 6.79,
        "desc": "More downward-pointing cam tab. Shorter horizontal reach, deeper vertical stroke."
    },
    {
        "title": "Option C: Flatter Forward Angle (~115° bellcrank angle)\nReaches Y = 5.00mm, Z = 7.80mm (Drops -4.79mm below axle)",
        "tip_y": Y_AXLE - 5.20, "tip_z": Z_AXLE - 4.79,
        "upper_y": Y_AXLE - 5.20, "upper_z": Z_AXLE - 4.79 + 2.40,
        "lower_y": Y_AXLE - 5.20 + 3.20, "lower_z": Z_AXLE - 4.79,
        "desc": "More horizontal reach towards Bracket 3 / key entrance slider."
    }
]

for idx, (ax, cfg) in enumerate(zip(axes, cam_configs)):
    # Baseplate floor (Z=0 to 1.0)
    ax.fill([0, 18, 18, 0], [0, 0, 1.0, 1.0], color='#b0bec5', alpha=0.7, label='Base Floor (1.0mm)')
    # Through hole
    ax.fill([8.57, 13.08, 13.08, 8.57], [-0.05, -0.05, 1.05, 1.05], color='white', ec='#d32f2f', lw=1.5, label='Through Hole')
    
    # Axle circle
    phi = np.linspace(0, 2*np.pi, 64)
    ax.fill(Y_AXLE + R_HUB*np.cos(phi), Z_AXLE + R_HUB*np.sin(phi), color='#37474f', alpha=0.8)
    ax.plot(Y_AXLE, Z_AXLE, 'ro', markersize=6, label=f'Pivot Axis (Y={Y_AXLE:.2f}, Z={Z_AXLE:.2f})')
    
    # Plunger
    ax.fill(pts_plunger[:, 0], pts_plunger[:, 1], color='#e65100', alpha=0.8, label='Plunger Blade (Z=-6.50mm)')
    
    # Cam
    cam_pts = np.array([
        [Y_AXLE + 1.50, Z_AXLE + 1.50],
        [cfg["upper_y"], cfg["upper_z"]],
        [cfg["tip_y"], cfg["tip_z"]],
        [cfg["lower_y"], cfg["lower_z"]],
        [Y_AXLE + 0.20, Z_AXLE - 2.80]
    ])
    ax.fill(cam_pts[:, 0], cam_pts[:, 1], color='#4caf50', alpha=0.85, edgecolor='#2e7d32', lw=1.5, label='Input Cam Tab')
    
    # Slider key push bar representation
    ax.plot([cfg["tip_y"] - 2.0, cfg["tip_y"]], [cfg["tip_z"] + 1.0, cfg["tip_z"] + 1.0], 'r->', lw=2.5)
    ax.text(cfg["tip_y"] - 2.2, cfg["tip_z"] + 1.5, 'Key Push (+Y)', color='#d32f2f', fontsize=8, fontweight='bold', ha='right')
    
    # Switch representation
    ax.fill([5.5, 8.5, 8.5, 5.5], [-7.5, -7.5, -5.5, -5.5], color='#81c784', alpha=0.5)
    ax.fill([8.5, 9.2, 9.2, 8.5], [-6.8, -6.8, -6.2, -6.2], color='#2e7d32', alpha=0.9)
    ax.axhline(-6.50, color='#e53935', linestyle=':', lw=1.5)
    
    # Angle arc and annotation
    v_c = np.array([cfg["tip_y"] - Y_AXLE, cfg["tip_z"] - Z_AXLE])
    v_p = np.array([plunger_y_center - Y_AXLE, z_tip - Z_AXLE])
    angle_deg = np.degrees(np.arccos(np.dot(v_c, v_p) / (np.linalg.norm(v_c) * np.linalg.norm(v_p))))
    
    ax.annotate(f'Angle: {angle_deg:.1f}°', xy=(Y_AXLE - 1.5, Z_AXLE - 2.0),
                fontsize=10, fontweight='bold', color='#1565c0',
                bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#1565c0'))
    
    ax.set_xlim(1, 16)
    ax.set_ylim(-8.5, 16)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_title(cfg["title"], fontsize=10.5, fontweight='bold')
    ax.set_xlabel('Y (mm)')
    ax.set_ylabel('Z (mm)')
    ax.legend(loc='lower left', fontsize=7.5)

plt.tight_layout()
out_png = 'testing/bellcrank_angle_comparison.png'
plt.savefig(out_png, dpi=200)
print(f"Saved {out_png}")
