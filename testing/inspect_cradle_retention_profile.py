"""
testing/inspect_cradle_retention_profile.py
Plot and compare cradle retention profiles for various throat constrictions.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

Y_SHAFT = 9.279
Z_CRADLE = 12.590
R_SHAFT = 1.50
R_PIN = 1.40
Z_BASE = 1.00
Z_TOP = 14.09

fig, axes = plt.subplots(1, 3, figsize=(18, 7), dpi=180)

options = [
    {"name": "1. Current Throat (2.45mm)\nInterference = 0.35mm (Too Loose)", "throat_w": 2.45, "color": "#e53935"},
    {"name": "2. High-Retention Lock (2.05mm)\nInterference = 0.75mm (2.1x Deeper Lip)", "throat_w": 2.05, "color": "#43a047"},
    {"name": "3. Ultra-Lock Heavy-Duty (1.95mm)\nInterference = 0.85mm (2.4x Deeper Lip)", "throat_w": 1.95, "color": "#1e88e5"}
]

for ax, opt in zip(axes, options):
    throat_w = opt["throat_w"]
    half_w = throat_w / 2.0
    alpha = np.arcsin(half_w / R_SHAFT)
    
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(Y_SHAFT + R_SHAFT * np.cos(p), Z_CRADLE + R_SHAFT * np.sin(p)) for p in phi]
    
    y_min_base = 6.250
    y_max_base = 12.850
    y_min_top = 6.550
    y_max_top = 12.180
    
    # 45 deg funnel bevel
    y_left_top = Y_SHAFT - half_w - (Z_TOP - (Z_CRADLE + R_SHAFT*np.cos(alpha))) * 0.7
    y_right_top = Y_SHAFT + half_w + (Z_TOP - (Z_CRADLE + R_SHAFT*np.cos(alpha))) * 0.7
    
    profile_yz = [
        (y_min_base, Z_BASE),
        (y_max_base, Z_BASE),
        (y_max_top, Z_TOP),
        (y_right_top, Z_TOP),
    ] + cradle_arc_pts + [
        (y_left_top, Z_TOP),
        (y_min_top, Z_TOP)
    ]
    poly = Polygon(profile_yz)
    
    # Fill tower body
    px, py = poly.exterior.xy
    ax.fill(px, py, color='#cfd8dc', alpha=0.8, ec='#37474f', lw=2)
    
    # Draw shaft pin inside cradle
    phi_pin = np.linspace(0, 2*np.pi, 64)
    ax.fill(Y_SHAFT + R_PIN*np.cos(phi_pin), Z_CRADLE + R_PIN*np.sin(phi_pin),
            color='#ff9800', alpha=0.85, ec='#e65100', lw=2, label=f'Shaft Pin (Ø{2*R_PIN:.2f}mm)')
    
    # Draw retention tips and throat gap
    z_tip = Z_CRADLE + R_SHAFT * np.cos(alpha)
    ax.plot([Y_SHAFT - half_w, Y_SHAFT + half_w], [z_tip, z_tip], 'r-', lw=2.5)
    ax.plot(Y_SHAFT - half_w, z_tip, 'ro', markersize=6)
    ax.plot(Y_SHAFT + half_w, z_tip, 'ro', markersize=6)
    
    wrap_deg = 180.0 + 2.0 * (90.0 - np.degrees(alpha))
    interference = 2*R_PIN - throat_w
    
    ax.annotate(f'Throat = {throat_w:.2f}mm\nInterference = {interference:.2f}mm\nWrap = {wrap_deg:.1f}°',
                xy=(Y_SHAFT, z_tip), xytext=(Y_SHAFT - 2.8, Z_TOP + 0.6),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=opt["color"]),
                fontsize=9.5, fontweight='bold', color=opt["color"],
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec=opt["color"]))
    
    ax.set_xlim(5.5, 13.5)
    ax.set_ylim(8.0, 16.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title(opt["name"], fontsize=10.5, fontweight='bold')
    ax.set_xlabel('Y (mm)')
    ax.set_ylabel('Z (mm)')
    ax.legend(loc='lower left', fontsize=8)

plt.tight_layout()
out_png = 'testing/cradle_retention_comparison.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
