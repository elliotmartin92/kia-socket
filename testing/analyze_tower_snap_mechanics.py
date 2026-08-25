"""
testing/analyze_tower_snap_mechanics.py
Inspection script to analyze tower clip cradle profile, snap throat interference,
lead-in chamfer, and deflection stress for different throat widths and socket geometries.
"""
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

Y_SHAFT = 9.279
Z_CRADLE = 12.590
R_PIN = 1.40   # 2.80mm diameter shaft pin
R_SOCKET = 1.50 # 3.00mm diameter cradle
Z_BASE = 1.00
Z_TOP = 14.09

Y_MIN_BASE = 6.250
Y_MAX_BASE = 12.850
Y_MIN_TOP = 6.550
Y_MAX_TOP = 12.180

throat_widths = [2.05, 2.40, 2.50, 2.55, 2.60, 2.65, 2.70]

print("=== Tower Snap Analysis for Ø2.80mm Pin in Ø3.00mm Socket ===")
print(f"Shaft pin diameter: {2*R_PIN:.2f} mm")
print(f"Socket diameter: {2*R_SOCKET:.2f} mm")
print(f"Z_cradle: {Z_CRADLE:.3f} mm, Z_top: {Z_TOP:.3f} mm (Height above axis: {Z_TOP - Z_CRADLE:.3f} mm)")
print("-" * 75)
print(f"{'Throat (mm)':<12} | {'Interference':<14} | {'Undercut/side':<14} | {'Wrap Angle':<12} | {'Tip Z (mm)':<10} | {'Funnel Top W':<12}")
print("-" * 75)

for tw in throat_widths:
    half_w = tw / 2.0
    sin_a = half_w / R_SOCKET
    if sin_a > 1.0:
        continue
    alpha = np.arcsin(sin_a)
    cos_a = np.cos(alpha)
    z_tip = Z_CRADLE + R_SOCKET * cos_a
    wrap_deg = 180.0 + 2.0 * (90.0 - np.degrees(alpha))
    interference = 2 * R_PIN - tw
    undercut = interference / 2.0
    
    bevel_dx = (Z_TOP - z_tip) * 0.75
    y_left_top = Y_SHAFT - half_w - bevel_dx
    y_right_top = Y_SHAFT + half_w + bevel_dx
    funnel_top_w = y_right_top - y_left_top
    
    print(f"{tw:<12.2f} | {interference:<14.3f} | {undercut:<14.3f} | {wrap_deg:<12.1f}° | {z_tip:<10.3f} | {funnel_top_w:<12.3f}")

# Plot comparison
fig, axes = plt.subplots(2, 3, figsize=(18, 11), dpi=180)
plot_cases = [
    (2.05, "Current: 2.05mm (0.75mm Interference - SNAPS)"),
    (2.40, "2.40mm (0.40mm Interference - High Strain)"),
    (2.50, "2.50mm (0.30mm Interference - Snug)"),
    (2.55, "2.55mm (0.25mm Interference - Optimal PLA/PETG)"),
    (2.60, "2.60mm (0.20mm Interference - Smooth Snap)"),
    (2.65, "2.65mm (0.15mm Interference - Low Insertion Force)")
]

for ax, (tw, title) in zip(axes.flatten(), plot_cases):
    half_w = tw / 2.0
    alpha = np.arcsin(half_w / R_SOCKET)
    z_tip = Z_CRADLE + R_SOCKET * np.cos(alpha)
    
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(Y_SHAFT + R_SOCKET * np.cos(p), Z_CRADLE + R_SOCKET * np.sin(p)) for p in phi]
    
    bevel_dx = (Z_TOP - z_tip) * 0.75
    y_left_top = Y_SHAFT - half_w - bevel_dx
    y_right_top = Y_SHAFT + half_w + bevel_dx
    
    profile_yz = [
        (Y_MIN_BASE, Z_BASE),
        (Y_MAX_BASE, Z_BASE),
        (Y_MAX_TOP, Z_TOP),
        (y_right_top, Z_TOP),
    ] + cradle_arc_pts + [
        (y_left_top, Z_TOP),
        (Y_MIN_TOP, Z_TOP)
    ]
    poly = Polygon(profile_yz)
    
    px, py = poly.exterior.xy
    ax.fill(px, py, color='#cfd8dc', alpha=0.8, ec='#37474f', lw=2)
    
    # Shaft pin seated
    phi_pin = np.linspace(0, 2*np.pi, 64)
    ax.fill(Y_SHAFT + R_PIN*np.cos(phi_pin), Z_CRADLE + R_PIN*np.sin(phi_pin),
            color='#ff9800', alpha=0.85, ec='#e65100', lw=2, label=f'Shaft Pin (Ø{2*R_PIN:.2f}mm)')
    
    # Throat line
    ax.plot([Y_SHAFT - half_w, Y_SHAFT + half_w], [z_tip, z_tip], 'r-', lw=2.5)
    ax.plot(Y_SHAFT - half_w, z_tip, 'ro', markersize=5)
    ax.plot(Y_SHAFT + half_w, z_tip, 'ro', markersize=5)
    
    interference = 2*R_PIN - tw
    wrap_deg = 180.0 + 2.0 * (90.0 - np.degrees(alpha))
    
    ax.annotate(f'Throat: {tw:.2f}mm\nInterference: {interference:.2f}mm\nUndercut: {interference/2:.3f}mm/side\nWrap: {wrap_deg:.1f}°',
                xy=(Y_SHAFT, z_tip), xytext=(Y_SHAFT - 2.6, Z_TOP + 0.4),
                fontsize=8.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1565c0', alpha=0.9))
    
    ax.set_xlim(5.5, 13.5)
    ax.set_ylim(8.0, 16.0)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title(title, fontsize=9.5, fontweight='bold')
    ax.set_xlabel('Y (mm)')
    ax.set_ylabel('Z (mm)')
    ax.legend(loc='lower left', fontsize=7.5)

plt.tight_layout()
plt.savefig('testing/tower_snap_options_comparison.png', dpi=180)
print("Saved testing/tower_snap_options_comparison.png")
