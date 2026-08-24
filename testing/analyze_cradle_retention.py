"""
testing/analyze_cradle_retention.py
Analyze retention force, undercut depth, wrap angle, and snap-in mechanics for various cradle throat widths and hook profiles.
"""
import numpy as np

D_PIN = 2.80
R_PIN = D_PIN / 2.0  # 1.40 mm
D_SOCKET = 3.00
R_SOCKET = D_SOCKET / 2.0  # 1.50 mm
Z_AXIS = 12.590

print("=== Cradle Retention Analysis for Ø2.80mm Shaft in Ø3.00mm Socket ===")

for throat_w in [2.45, 2.30, 2.20, 2.10, 2.00, 1.90, 1.80]:
    half_w = throat_w / 2.0
    if half_w >= R_SOCKET:
        continue
    sin_a = half_w / R_SOCKET
    alpha = np.arcsin(sin_a) # Angle from vertical
    alpha_deg = np.degrees(alpha)
    
    wrap_angle_deg = 180.0 + 2.0 * (90.0 - alpha_deg)
    
    z_tip = Z_AXIS + R_SOCKET * np.cos(alpha)
    tip_height_above_axis = z_tip - Z_AXIS
    
    interference = D_PIN - throat_w
    undercut_per_side = interference / 2.0
    retention_overlap_pct = (interference / D_PIN) * 100.0
    
    print(f"\nThroat Width = {throat_w:.2f} mm:")
    print(f"  Snap Interference: {interference:.2f} mm ({undercut_per_side:.3f} mm per side, {retention_overlap_pct:.1f}% diameter overlap)")
    print(f"  Wrap Angle: {wrap_angle_deg:.1f}° ({wrap_angle_deg/360.0*100:.1f}% full circle)")
    print(f"  Retention Tip Height above Axis: {tip_height_above_axis:.2f} mm (Z_tip = {z_tip:.2f} mm)")
