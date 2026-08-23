"""
Visualize the bottom arch region options.
"""
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    SCALE, X0, Y0, outer_pts, OUTER_WALL_THICK, OUTER_WALL_HEIGHT
)

# 1. Exact raw outer perimeter from SVG
raw_outer_poly = Polygon(outer_pts)

# 2. Arch path from SVG
p0 = (132.6, 171.8)
p1 = (132.6 - 0.6, 171.8 - 9.6)
p2 = (132.6 + 2.0, 171.8 - 16.2)
p3 = (132.6 - 5.1, 171.8 - 16.2)
arch_pts = []
for t in np.linspace(0, 1, 30):
    bx = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
    by = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
    arch_pts.append(((bx - X0)*SCALE, -(by - Y0)*SCALE))

p0 = p3
p1 = (p0[0] - 7.0, p0[1] + 0.0)
p2 = (p0[0] - 5.7, p0[1] + 5.7)
p3 = (p0[0] - 5.4, p0[1] + 16.2)
for t in np.linspace(0.03, 1, 30):
    bx = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
    by = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
    arch_pts.append(((bx - X0)*SCALE, -(by - Y0)*SCALE))

# Closed arch loop (with the horizontal line Y = -16.65mm)
closed_arch_poly = Polygon(arch_pts)

fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=160)

# Option 1: Solid perimeter base (with inset bottom wall) + Arch as an internal wall
ax1 = axes[0]
rx, ry = raw_outer_poly.exterior.xy
ax1.plot(rx, ry, 'b-', linewidth=2, label='Outer Perimeter Wall (with 1.88mm inset)')
ix, iy = raw_outer_poly.buffer(-OUTER_WALL_THICK).exterior.xy
ax1.plot(ix, iy, 'b--', linewidth=1.2, label='Inner Wall Face')

# Arch curve
ax1.plot([p[0] for p in arch_pts], [p[1] for p in arch_pts], 'r-', linewidth=2.5, label='Arch Wall (6.77mm tall)')
ax1.set_xlim(-15, 15)
ax1.set_ylim(-21, -8)
ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_title('Option A: Arch as an Internal Wall (Solid Floor Beneath)', fontsize=11, fontweight='bold')
ax1.legend()

# Option 2: Arch as a floor cutout with wall around it, but exterior wall closed at Y = -16.65mm
ax2 = axes[1]
cut_poly = raw_outer_poly.difference(closed_arch_poly)
cx, cy = cut_poly.exterior.xy
ax2.plot(cx, cy, 'g-', linewidth=2, label='Floor Perimeter with Arch Cutout')
ax2.plot([p[0] for p in arch_pts], [p[1] for p in arch_pts], 'r-', linewidth=2.5, label='Arch Wall')
ax2.plot([arch_pts[0][0], arch_pts[-1][0]], [arch_pts[0][1], arch_pts[-1][1]], 'b-', linewidth=2.5, label='Bottom Wall (Y = -16.65mm)')
ax2.set_xlim(-15, 15)
ax2.set_ylim(-21, -8)
ax2.set_aspect('equal')
ax2.grid(True)
ax2.set_title('Option B: Arch as Floor Cutout (Closed Exterior Wall at Bottom)', fontsize=11, fontweight='bold')
ax2.legend()

plt.tight_layout()
plt.savefig('bottom_arch_options.png', dpi=160)
print("Saved bottom_arch_options.png")
