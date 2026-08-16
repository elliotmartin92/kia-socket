"""
Generate detailed comparison plots of the bottom notch and arch alignments.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString, box
import matplotlib.pyplot as plt

from build_part import (
    outer_pts, create_arch_wall_poly, OUTER_WALL_THICK,
    OUTER_WALL_HEIGHT, BASE_THICK
)

pts = outer_pts.copy()

def make_bottom_poly(notch_x_outer_left, notch_x_outer_right):
    new_pts = pts.copy()
    for idx, (x, y) in enumerate(new_pts):
        if abs(y - (-18.539)) < 0.05:
            if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
                new_pts[idx] = [notch_x_outer_right, -18.539]
            elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
                new_pts[idx] = [notch_x_outer_left, -18.539]
        elif abs(y - (-16.650)) < 0.05:
            if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
                new_pts[idx] = [notch_x_outer_right, -16.650]
            elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
                new_pts[idx] = [notch_x_outer_left, -16.650]
    poly = Polygon(new_pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly

def make_arch_poly(inner_w=5.0, wall_t=1.20):
    r_in = inner_w / 2.0
    r_out = r_in + wall_t
    apex_y = -11.00
    base_y = -16.650
    center_y = apex_y - r_in
    
    # Outer arch
    th = np.linspace(0, np.pi, 30)
    outer_arc = [(r_out * np.cos(t), center_y + r_out * np.sin(t)) for t in th]
    outer_full = [(r_out, base_y)] + outer_arc + [(-r_out, base_y)]
    
    # Inner arch
    inner_arc = [(r_in * np.cos(t), center_y + r_in * np.sin(t)) for t in th[::-1]]
    inner_full = [(-r_in, base_y)] + inner_arc + [(r_in, base_y)]
    
    return Polygon(outer_full + inner_full)

# Config 1: Outer notch aligns with Inner arch (notch outer X = ±2.50mm, arch inner X = ±2.50mm)
poly_1 = make_bottom_poly(-2.50, 2.50)
inner_1 = poly_1.buffer(-OUTER_WALL_THICK)
arch_1 = make_arch_poly(5.00, 1.20)

# Config 2: Notch interior width = 3.55mm (outer notch X = ±(3.55/2 + 1.20) = ±2.975mm)
poly_2 = make_bottom_poly(-2.975, 2.975)
inner_2 = poly_2.buffer(-OUTER_WALL_THICK)
arch_2 = make_arch_poly(5.00, 1.20)

# Config 3: Arch and Notch BOTH have 3.55mm interior width (aligned at inner X = ±1.775mm, outer X = ±2.975mm)
poly_3 = make_bottom_poly(-2.975, 2.975)
inner_3 = poly_3.buffer(-OUTER_WALL_THICK)
arch_3 = make_arch_poly(3.55, 1.20)

# Config 4: Notch outer X = ±3.70mm (Option A from earlier)
poly_4 = make_bottom_poly(-3.70, 3.70)
inner_4 = poly_4.buffer(-OUTER_WALL_THICK)
arch_4 = make_arch_poly(5.00, 1.20)

fig, axes = plt.subplots(2, 2, figsize=(18, 16), dpi=160)

# Plot Config 1
ax = axes[0, 0]
ax.plot(*poly_1.exterior.xy, 'b-o', markersize=3, label='Perimeter Outer Wall')
ax.plot(*inner_1.exterior.xy, 'b--', alpha=0.6, label='Perimeter Inner Wall')
ax.plot(*arch_1.exterior.xy, 'r-', linewidth=2, label='Arch Wall (5.00mm Inner Width)')
ax.axvline(-2.50, color='purple', linestyle=':', label='X = -2.50mm (Arch Inner Leg)')
ax.axvline(2.50, color='purple', linestyle=':', label='X = +2.50mm (Arch Inner Leg)')
ax.set_xlim(-10, 10)
ax.set_ylim(-20, -9)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Config 1: Inset Notch Outer Walls Align with Arch INNER Walls (X = ±2.50mm)\n(Arch 5.0mm Inner Width)', fontsize=11, fontweight='bold')
ax.legend(loc='upper right', fontsize=8)

# Plot Config 2
ax = axes[0, 1]
ax.plot(*poly_2.exterior.xy, 'b-o', markersize=3, label='Perimeter Outer Wall')
ax.plot(*inner_2.exterior.xy, 'b--', alpha=0.6, label='Perimeter Inner Wall')
ax.plot(*arch_2.exterior.xy, 'r-', linewidth=2, label='Arch Wall (5.00mm Inner Width)')
ax.axvline(-1.775, color='green', linestyle=':', label='X = -1.775mm (Notch Inner Face)')
ax.axvline(1.775, color='green', linestyle=':', label='X = +1.775mm (Notch Inner Face)')
ax.set_xlim(-10, 10)
ax.set_ylim(-20, -9)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Config 2: Inset Notch has 3.55mm Interior Width (X_out = ±2.975mm)\n(Arch has 5.0mm Inner Width)', fontsize=11, fontweight='bold')
ax.legend(loc='upper right', fontsize=8)

# Plot Config 3
ax = axes[1, 0]
ax.plot(*poly_3.exterior.xy, 'b-o', markersize=3, label='Perimeter Outer Wall')
ax.plot(*inner_3.exterior.xy, 'b--', alpha=0.6, label='Perimeter Inner Wall')
ax.plot(*arch_3.exterior.xy, 'r-', linewidth=2, label='Arch Wall (3.55mm Inner Width)')
ax.axvline(-1.775, color='green', linestyle=':', label='X = -1.775mm (Arch & Notch Inner)')
ax.axvline(1.775, color='green', linestyle=':', label='X = +1.775mm (Arch & Notch Inner)')
ax.axvline(-2.975, color='orange', linestyle=':', label='X = -2.975mm (Arch & Notch Outer)')
ax.axvline(2.975, color='orange', linestyle=':', label='X = +2.975mm (Arch & Notch Outer)')
ax.set_xlim(-10, 10)
ax.set_ylim(-20, -9)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Config 3: BOTH Arch & Inset Notch have 3.55mm Interior Width\n(Inner walls aligned at X = ±1.775mm, Outer walls at X = ±2.975mm)', fontsize=11, fontweight='bold')
ax.legend(loc='upper right', fontsize=8)

# Plot Config 4
ax = axes[1, 1]
ax.plot(*poly_4.exterior.xy, 'b-o', markersize=3, label='Perimeter Outer Wall')
ax.plot(*inner_4.exterior.xy, 'b--', alpha=0.6, label='Perimeter Inner Wall')
ax.plot(*arch_4.exterior.xy, 'r-', linewidth=2, label='Arch Wall (5.00mm Inner Width)')
ax.axvline(-3.70, color='gray', linestyle=':', label='X = -3.70mm (Arch & Notch Outer)')
ax.axvline(3.70, color='gray', linestyle=':', label='X = +3.70mm (Arch & Notch Outer)')
ax.axvline(-2.50, color='purple', linestyle=':', label='X = -2.50mm (Arch Inner Leg)')
ax.axvline(2.50, color='purple', linestyle=':', label='X = +2.50mm (Arch Inner Leg)')
ax.set_xlim(-10, 10)
ax.set_ylim(-20, -9)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Config 4: Inset Notch Outer Walls Align with Arch OUTER Walls (X = ±3.70mm)\n(Arch 5.0mm Inner Width)', fontsize=11, fontweight='bold')
ax.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('bottom_notch_and_arch_configs.png', dpi=160)
print("Saved bottom_notch_and_arch_configs.png")
