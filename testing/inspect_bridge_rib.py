"""
Inspect ribs in the right tower bridge area.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box
import matplotlib.pyplot as plt

from build_part import (
    get_exact_base_polygon, create_grid_ribs_poly,
    TOWER_WALL_THICK, TOWER_Y_LEN
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
all_ribs_poly = create_grid_ribs_poly(base_poly, outer_body_poly)

fig, ax = plt.subplots(figsize=(10, 8), dpi=160)

# Plot outer wall
ox, oy = outer_body_poly.exterior.xy
ax.plot(ox, oy, color='#1f77b4', linewidth=2)

# Plot all ribs
for geom in (all_ribs_poly.geoms if hasattr(all_ribs_poly, 'geoms') else [all_ribs_poly]):
    rx, ry = geom.exterior.xy
    ax.plot(rx, ry, color='#ff7f0e', linewidth=1.0)

# Right Tower bounds
x_right_inner = 13.360
x_right_outer = 13.360 + 1.25  # 14.610
y_min = -17.339 + 22.68  # 5.341
y_max = y_min + TOWER_Y_LEN  # 9.991

ax.fill([x_right_inner, x_right_outer, x_right_outer, x_right_inner],
        [y_min, y_min, y_max, y_max], color='#e377c2', alpha=0.5, label='Right Tower')

# Horizontal lines at 0, 3.2, 6.4, 9.6, 12.8
for y_h in [0, 3.2, 6.4, 9.6, 12.8]:
    ax.axhline(y_h, color='gray', linestyle=':', alpha=0.7)
    ax.text(10, y_h + 0.1, f'Y = {y_h:.1f}', fontsize=8, color='gray')

# Vertical line at 15.6
ax.axvline(15.6, color='gray', linestyle=':', alpha=0.7)
ax.text(15.6 + 0.1, 4, 'X = 15.6', fontsize=8, color='gray')

ax.set_xlim(10, 22)
ax.set_ylim(2, 14)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.3)
ax.set_title('Detailed View of Right Tower and Bridge Ribs')
ax.legend()

plt.tight_layout()
plt.savefig('bridge_rib_detail.png', dpi=160)
print("Saved bridge_rib_detail.png")
