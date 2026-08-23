"""
Inspect exact points of outer_pts and align the bottom notch with the arch.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

from build_part import outer_pts, create_arch_wall_poly

# outer_pts is an Nx2 array in mm
pts = outer_pts.copy()

print("Points with Y < -15.5mm:")
for idx, (x, y) in enumerate(pts):
    if y < -15.5:
        print(f"Index {idx:2d}: X = {x:7.3f}, Y = {y:7.3f}")

arch_poly = create_arch_wall_poly()
# Inner arch is X in [-2.50, +2.50], Y in [-16.65, -11.00]
# Outer arch is X in [-3.70, +3.70], Y in [-16.65, -9.80]

# Notice indices:
# Let's find the bottom notch points:
# Index 47: X =   9.812, Y = -18.539  (Right tab outer corner)
# Index 48: X =   1.382, Y = -18.539  (Right tab inner corner at notch)
# Index 49: X =   1.382, Y = -16.650  (Notch top-right corner)
# Index 50: X =  -2.291, Y = -16.650  (Notch top-left corner)
# Index 51: X =  -2.291, Y = -18.539  (Left tab inner corner at notch)
# Index 52: X = -10.686, Y = -18.539  (Left tab outer corner)

def get_aligned_pts(notch_x_left, notch_x_right):
    new_pts = pts.copy()
    for idx, (x, y) in enumerate(new_pts):
        if abs(y - (-18.539)) < 0.05:
            if abs(x - 1.382) < 0.05:
                new_pts[idx] = [notch_x_right, -18.539]
            elif abs(x - (-2.291)) < 0.05:
                new_pts[idx] = [notch_x_left, -18.539]
        elif abs(y - (-16.650)) < 0.05:
            if abs(x - 1.382) < 0.05:
                new_pts[idx] = [notch_x_right, -16.650]
            elif abs(x - (-2.291)) < 0.05:
                new_pts[idx] = [notch_x_left, -16.650]
    return new_pts

pts_outer = get_aligned_pts(-3.70, 3.70)
pts_inner = get_aligned_pts(-2.50, 2.50)

poly_outer = Polygon(pts_outer)
poly_inner = Polygon(pts_inner)

fig, axes = plt.subplots(1, 2, figsize=(18, 7), dpi=160)

# Option A: Inset notch at X = ±3.70mm (Aligned to Outer Arch Walls)
axes[0].plot(*poly_outer.exterior.xy, 'b-o', markersize=3, label='Exterior Perimeter Wall (Notch X = ±3.70mm)')
axes[0].plot(*arch_poly.exterior.xy, 'r-', linewidth=2, label='Bottom Central Arch Wall')
axes[0].set_xlim(-12, 12)
axes[0].set_ylim(-20, -8)
axes[0].set_aspect('equal')
axes[0].grid(True)
axes[0].set_title('Option A: Inset Notch Aligned to Outer Walls of Arch (X = ±3.70mm)', fontsize=11, fontweight='bold')
axes[0].legend(loc='upper right')

# Option B: Inset notch at X = ±2.50mm (Aligned to Inner Walls of Arch)
axes[1].plot(*poly_inner.exterior.xy, 'b-o', markersize=3, label='Exterior Perimeter Wall (Notch X = ±2.50mm)')
axes[1].plot(*arch_poly.exterior.xy, 'r-', linewidth=2, label='Bottom Central Arch Wall')
axes[1].set_xlim(-12, 12)
axes[1].set_ylim(-20, -8)
axes[1].set_aspect('equal')
axes[1].grid(True)
axes[1].set_title('Option B: Inset Notch Aligned to Inner Walls of Arch (X = ±2.50mm)', fontsize=11, fontweight='bold')
axes[1].legend(loc='upper right')

plt.tight_layout()
plt.savefig('aligned_bottom_notch_options.png', dpi=160)
print("Saved aligned_bottom_notch_options.png")
