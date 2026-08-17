"""
Compare slit insert footprint options to eliminate the gap to the outer perimeter walls.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    get_exact_base_polygon, extrude_shapely_geom, SLIT_BOSS_HEIGHT
)

# Left slit: X in [-8.953, -7.853], Y in [-16.339, -13.339]
# Right slit: X in [7.853, 8.953], Y in [-16.339, -13.339]
# Bottom Tab Outer Edge: Y = -18.539mm

base_poly, _, _ = get_exact_base_polygon()

# Option 1: Symmetrical box (Current - 1.0mm gap to Y = -18.539mm)
# Body Y: [-17.539, -12.139]
opt1_left = box(-8.403 - 1.75, -17.539, -8.403 + 1.75, -12.139)

# Option 2: Extended -Y wall (Flush with Bottom Tab Y = -18.539mm)
# Body Y: [-18.539, -12.139] (Front wall is 2.20mm thick, outer edge flush with bottom tab at Y = -18.539mm)
opt2_left = box(-8.403 - 1.75, -18.539, -8.403 + 1.75, -12.139)
opt2_right = box(8.403 - 1.75, -18.539, 8.403 + 1.75, -12.139)

# Option 3: Full-tab footprint (Extends to corner X = -10.686mm and Y = -18.539mm)
# Left tab: X in [-10.686, -2.500], Y = -18.539mm
opt3_left = box(-10.403, -18.539, -6.403, -12.139)

fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=160)

for idx, (ax, title, ins_poly) in enumerate([
    (axes[0], "Option 1: Isolated Symmetric Box\n(1.00mm Gap to Bottom Tab Wall)", opt1_left),
    (axes[1], "Option 2: Flush Bottom Edge (Recommended)\n(Wall extends to Y = -18.54mm, perfectly flush)", opt2_left),
    (axes[2], "Option 3: Wide Footprint\n(Extended in both X and Y)", opt3_left)
]):
    # Base perimeter
    ax.plot(*base_poly.exterior.xy, 'k-', linewidth=2, label='Main Baseplate Wall')
    for interior in base_poly.interiors:
        ax.plot(*interior.xy, 'r-', linewidth=1.5, label='Through Slit' if interior.bounds[0] < 0 else "")
        
    ax.plot(*ins_poly.exterior.xy, 'b-', linewidth=2.5, label='Insert Outer Body')
    ax.fill(*ins_poly.exterior.xy, color='#e91e63', alpha=0.35)
    
    # Slit hole
    slit_box = box(-8.953, -16.339, -7.853, -13.339)
    ax.plot(*slit_box.exterior.xy, 'r-', linewidth=2)
    
    ax.set_xlim(-13, -2)
    ax.set_ylim(-20, -10)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_title(title, fontsize=10.5, fontweight='bold')
    if idx == 0:
        ax.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('insert_gap_solutions_preview.png', dpi=160)
print("Saved insert_gap_solutions_preview.png")
