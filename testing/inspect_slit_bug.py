"""
Inspect the disconnected geometry in slit_insert.stl
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
import trimesh
import matplotlib.pyplot as plt

# Let's inspect what happened in build_slit_insert_mesh:
outer_body = box(-3.50/2, -5.40/2, 3.50/2, 5.40/2)  # [-1.75, 1.75] x [-2.70, 2.70]
inner_body = box(-1.10/2, -3.00/2, 1.10/2, 3.00/2)  # [-0.55, 0.55] x [-1.50, 1.50]
body_poly = outer_body.difference(inner_body)

outer_key = box(-0.95/2, -2.85/2, 0.95/2, 2.85/2)   # [-0.475, 0.475] x [-1.425, 1.425]
inner_key = box(-0.65/2, -2.55/2, 0.65/2, 2.55/2)   # [-0.325, 0.325] x [-1.275, 1.275]
key_poly = outer_key.difference(inner_key)

print(f"Body inner hole bounds: {inner_body.bounds}")
print(f"Key outer plug bounds:  {outer_key.bounds}")
print(f"Does body_poly overlap key_poly in 2D? {body_poly.intersects(key_poly)}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=160)

# 2D Top View showing the gap
ax1.plot(*outer_body.exterior.xy, 'b-', linewidth=2, label='Body Outer Wall (3.5x5.4mm)')
ax1.plot(*inner_body.exterior.xy, 'b--', linewidth=2, label='Body Inner Hole (1.1x3.0mm)')
ax1.fill(*body_poly.exterior.xy, color='blue', alpha=0.2)
ax1.fill(*inner_body.exterior.xy, color='white')

ax1.plot(*outer_key.exterior.xy, 'r-', linewidth=2, label='Key Outer Wall (0.95x2.85mm)')
ax1.plot(*inner_key.exterior.xy, 'r--', linewidth=2, label='Key Inner Hole (0.65x2.55mm)')
ax1.fill(*outer_key.exterior.xy, color='red', alpha=0.3)
ax1.fill(*inner_key.exterior.xy, color='white')

ax1.set_xlim(-2.5, 2.5)
ax1.set_ylim(-3.5, 3.5)
ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_title('Top-Down View of Current Slit Insert (Floating Gap Shown in Red vs Blue)', fontsize=11, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8.5)

# X-Z Cross section
ax2.axhline(0, color='gray', linestyle='--')
ax2.axhline(2.47, color='purple', linestyle=':', label='Z = 2.47mm Shoulder Interface')
ax2.axhline(3.32, color='gray', linestyle='--')

# Body walls: X in [-1.75, -0.55] and [+0.55, +1.75], Z in [0, 2.47]
ax2.fill_between([-1.75, -0.55], 0, 2.47, color='blue', alpha=0.4, label='Body Wall (Z: 0 to 2.47mm)')
ax2.fill_between([0.55, 1.75], 0, 2.47, color='blue', alpha=0.4)

# Key walls: X in [-0.475, -0.325] and [+0.325, +0.475], Z in [2.47, 3.32]
ax2.fill_between([-0.475, -0.325], 2.47, 3.32, color='red', alpha=0.6, label='Key Wall (Z: 2.47 to 3.32mm)')
ax2.fill_between([0.325, 0.475], 2.47, 3.32, color='red', alpha=0.6)

# Annotate gap
ax2.annotate('0.075mm Air Gap!\n(No connection)', xy=(-0.51, 2.47), xytext=(-1.5, 2.9),
             arrowprops=dict(arrowstyle='->', color='red', lw=1.5), fontweight='bold', color='red', fontsize=10)

ax2.set_xlim(-2.5, 2.5)
ax2.set_ylim(-0.5, 4.0)
ax2.set_aspect('equal')
ax2.grid(True)
ax2.set_title('X-Z Cross Section: Disconnected Floating Key Bug', fontsize=11, fontweight='bold')
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Z (mm)')
ax2.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
plt.savefig('inspect_slit_insert_bug.png', dpi=160)
print("Saved inspect_slit_insert_bug.png")
