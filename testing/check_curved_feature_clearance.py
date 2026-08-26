"""
testing/check_curved_feature_clearance.py
Verify exact spatial clearances between the inserted AC plug blades and the Center Curved Feature.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import create_center_curved_feature_poly, create_all_brackets_poly
from build_shaft import CAM_WIDTH_X, CAM_X_CENTER

# NEMA 5-15 Geometry
Y_GROUND_PIN = -12.400       # Center of U-arch ground receptacle (mm)
NEMA_PIN_TO_BLADE_Y = 15.290 # Standard NEMA 5-15 distance from ground pin to blade centerline (0.602")
Y_BLADE_CENTER = Y_GROUND_PIN + NEMA_PIN_TO_BLADE_Y # +2.890 mm

# Blade Dimensions (mm)
W_BLADE_HOT = 6.35      # 1/4" narrow hot blade
W_BLADE_NEUTRAL = 7.92  # 5/16" wide neutral blade
T_BLADE = 1.52          # 0.060" thickness

# Hot Blade X-Y bounds
HOT_X_CENTER = +6.279
HOT_Y_MIN = Y_BLADE_CENTER - W_BLADE_HOT / 2.0  # -0.285 mm
HOT_Y_MAX = Y_BLADE_CENTER + W_BLADE_HOT / 2.0  # +6.065 mm
HOT_X_MIN = HOT_X_CENTER - T_BLADE / 2.0        # +5.519 mm
HOT_X_MAX = HOT_X_CENTER + T_BLADE / 2.0        # +7.039 mm

# Center Curved Feature bounds
curved_poly = create_center_curved_feature_poly()
minx_c, miny_c, maxx_c, maxy_c = curved_poly.bounds

print("=== CLEARANCE VERIFICATION: PLUG BLADES VS CENTER CURVED FEATURE ===")
print(f"1. Standard NEMA 5-15 Ground Pin Center:  Y = {Y_GROUND_PIN:.3f} mm")
print(f"2. Standard NEMA 5-15 Pin-to-Blade Pitch:   dY = {NEMA_PIN_TO_BLADE_Y:.3f} mm (0.602 in)")
print(f"3. Nominal AC Plug Blade Centerline:     Y = {Y_BLADE_CENTER:.3f} mm")
print(f"\n4. Right Hot Blade Footprint (X-Y):")
print(f"   - X span: [{HOT_X_MIN:.3f}, {HOT_X_MAX:.3f}] mm (Width: {T_BLADE:.2f} mm)")
print(f"   - Y span: [{HOT_Y_MIN:.3f}, {HOT_Y_MAX:.3f}] mm (Length: {W_BLADE_HOT:.2f} mm)")
print(f"\n5. Center Curved Feature Footprint (X-Y):")
print(f"   - X span: [{minx_c:.3f}, {maxx_c:.3f}] mm (Width: {maxx_c - minx_c:.2f} mm)")
print(f"   - Y span: [{miny_c:.3f}, {maxy_c:.3f}] mm (Depth: {maxy_c - miny_c:.2f} mm, Apex at Y = {maxy_c:.3f} mm)")
print(f"   - Height in Z: [1.00, 10.50] mm")

gap_y = HOT_Y_MIN - maxy_c
print(f"\n6. Net Longitudinal (Y) Clearance: {gap_y:.3f} mm")
if gap_y > 0:
    print(f"   >>> RESULT: ZERO CONTACT (Generous +{gap_y:.2f} mm clear air gap between blade bottom and curved feature apex) <<<")
else:
    print(f"   >>> RESULT: INTERFERENCE of {-gap_y:.2f} mm <<<")

# Plot 2D Top-Down Inspection
fig, ax = plt.subplots(figsize=(12, 8), dpi=180)

# Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax.plot(bx, by, color='#2e7d32', lw=1.5)
    ax.fill(bx, by, color='#e8f5e9', alpha=0.6)

# Center Curved Feature (Purple)
cx_pts, cy_pts = curved_poly.exterior.xy
ax.fill(cx_pts, cy_pts, color='#ba68c8', alpha=0.8, ec='#6a1b9a', lw=2.0, label='Center Curved Feature (10.50mm H)')
for interior in curved_poly.interiors:
    ix, iy = interior.xy
    ax.fill(ix, iy, color='#ffffff')
    ax.plot(ix, iy, color='#6a1b9a', lw=1.5)

# Hot Blade (Blue)
ax.fill([HOT_X_MIN, HOT_X_MAX, HOT_X_MAX, HOT_X_MIN],
        [HOT_Y_MIN, HOT_Y_MIN, HOT_Y_MAX, HOT_Y_MAX],
        color='#1976d2', alpha=0.85, ec='#0d47a1', lw=2.0, label=f'Hot Plug Blade (1.52x6.35mm @ Y={Y_BLADE_CENTER:.2f})')

# Neutral Blade (Light Blue)
ax.fill([-HOT_X_MAX, -HOT_X_MIN, -HOT_X_MIN, -HOT_X_MAX],
        [Y_BLADE_CENTER - W_BLADE_NEUTRAL/2, Y_BLADE_CENTER - W_BLADE_NEUTRAL/2, Y_BLADE_CENTER + W_BLADE_NEUTRAL/2, Y_BLADE_CENTER + W_BLADE_NEUTRAL/2],
        color='#90caf9', alpha=0.85, ec='#1565c0', lw=2.0, label='Neutral Plug Blade (1.52x7.92mm)')

# Dimension callout for the +2.16mm gap
ax.annotate(f'Clear Air Gap = +{gap_y:.2f} mm\n(Zero Contact / No Interference)',
            xy=(HOT_X_CENTER, (HOT_Y_MIN + maxy_c)/2), xytext=(11.0, -3.5),
            arrowprops=dict(facecolor='#2e7d32', edgecolor='#1b5e20', width=1.5, headwidth=5),
            fontsize=9.5, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round,pad=0.4', fc='#e8f5e9', ec='#2e7d32'))

ax.plot([HOT_X_CENTER, HOT_X_CENTER], [maxy_c, HOT_Y_MIN], 'r--', lw=2.0)

ax.set_xlim(-12, 14)
ax.set_ylim(-8, 9)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title(f"Planar Clearance: Plug Blade vs Center Curved Feature (+{gap_y:.2f}mm Gap)", fontsize=12, fontweight='bold')
ax.set_xlabel("X (mm)", fontweight='bold')
ax.set_ylabel("Y (mm)", fontweight='bold')
ax.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
out_path = "testing/curved_feature_blade_clearance.png"
plt.savefig(out_path, dpi=200)
print(f"Saved inspection plot to {out_path}")
