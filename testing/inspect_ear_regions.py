import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    create_grid_ribs_poly, OUTER_WALL_THICK
)
import matplotlib.pyplot as plt
import shapely.geometry as sg

base_poly, outer_poly, _ = get_exact_base_polygon()
inner_poly = outer_poly.buffer(-OUTER_WALL_THICK)
brackets = create_all_brackets_poly()
ribs = create_grid_ribs_poly(base_poly, outer_poly)

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=160)

# 1. Left Ear Region
ax = axes[0]
ax.plot(*outer_poly.exterior.xy, 'b-', linewidth=2, label='Outer Body')
ax.plot(*inner_poly.exterior.xy, 'b--', linewidth=1.2, label='Inner Wall Face (1.2mm)')
for geom in (brackets.geoms if hasattr(brackets, 'geoms') else [brackets]):
    ax.plot(*geom.exterior.xy, 'g-', linewidth=1.5)
for geom in (ribs.geoms if hasattr(ribs, 'geoms') else [ribs]):
    ax.plot(*geom.exterior.xy, 'orange', linewidth=1)

ax.set_xlim(-24, -15)
ax.set_ylim(-8, 8)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Left Ear Region (Current: 8.88mm)', fontsize=12, fontweight='bold')
ax.legend(loc='lower left')

# 2. Right Ear Region
ax = axes[1]
ax.plot(*outer_poly.exterior.xy, 'b-', linewidth=2, label='Outer Body')
ax.plot(*inner_poly.exterior.xy, 'b--', linewidth=1.2, label='Inner Wall Face (1.2mm)')
for geom in (brackets.geoms if hasattr(brackets, 'geoms') else [brackets]):
    ax.plot(*geom.exterior.xy, 'g-', linewidth=1.5)
for geom in (ribs.geoms if hasattr(ribs, 'geoms') else [ribs]):
    ax.plot(*geom.exterior.xy, 'orange', linewidth=1)

ax.set_xlim(15, 24)
ax.set_ylim(-8, 8)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Right Ear Region (Current: 8.88mm)', fontsize=12, fontweight='bold')
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig('testing/ear_regions_inspection.png', dpi=160)
print("Saved testing/ear_regions_inspection.png")
