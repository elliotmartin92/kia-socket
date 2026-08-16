"""
Inspect bottom exterior wall notch coordinates vs bottom arch wall.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString, box
import matplotlib.pyplot as plt

from build_part import (
    outer_pts, SCALE, X0, Y0, OUTER_WALL_THICK,
    create_arch_wall_poly, get_exact_base_polygon
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
arch_poly = create_arch_wall_poly()

# Extract the bottom segment of outer_body_poly (Y < -15.0)
coords = np.array(outer_body_poly.exterior.coords)
bottom_coords = coords[coords[:, 1] < -15.0]

print("Bottom perimeter coordinates in outer_body_poly:")
for x, y in bottom_coords:
    print(f"  X = {x:7.3f}, Y = {y:7.3f}")

print("\nArch wall exterior bounds:")
print("  Arch bounds:", arch_poly.bounds)

fig, ax = plt.subplots(figsize=(10, 8), dpi=160)
ax.plot(*outer_body_poly.exterior.xy, 'b-o', markersize=4, label='Exterior Perimeter Wall')
ax.plot(*arch_poly.exterior.xy, 'r-', linewidth=2, label='Bottom Central Arch Wall (5mm inner)')

ax.set_xlim(-12, 12)
ax.set_ylim(-20, -8)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Bottom Central Arch vs Inset Bottom Perimeter Wall', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig('bottom_wall_alignment_inspect.png', dpi=160)
print("Saved bottom_wall_alignment_inspect.png")
