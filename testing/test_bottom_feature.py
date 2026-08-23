"""
Test full bottom geometry with inset exterior wall, base floor, and arch wall.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    SCALE, X0, Y0, outer_pts, OUTER_WALL_THICK, OUTER_WALL_HEIGHT, BASE_THICK
)

# 1. Base perimeter from SVG outer_pts
raw_outer_poly = Polygon(outer_pts)

# Arch path points
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

# Arch line string
arch_line = sg.LineString(arch_pts)
# Arch wall polygon (1.2mm thick along arch line, buffered inward or centered)
arch_wall_poly = arch_line.buffer(OUTER_WALL_THICK / 2.0, cap_style=2).intersection(raw_outer_poly)

# Perimeter wall poly
inner_poly = raw_outer_poly.buffer(-OUTER_WALL_THICK)
wall_poly = raw_outer_poly.difference(inner_poly)
all_walls_poly = unary_union([wall_poly, arch_wall_poly])

# Base floor
base_floor_mesh = trimesh.creation.extrude_polygon(raw_outer_poly, height=BASE_THICK)

# Walls
walls_mesh = trimesh.creation.extrude_polygon(all_walls_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
walls_mesh.apply_translation([0, 0, BASE_THICK])

combo_mesh = trimesh.util.concatenate([base_floor_mesh, walls_mesh])

# Plot 3D close-up of bottom region
fig = plt.figure(figsize=(10, 8), dpi=160)
ax = fig.add_subplot(1, 1, 1, projection='3d')

col = Poly3DCollection(combo_mesh.vertices[combo_mesh.faces], alpha=0.9, edgecolor='#222222', linewidths=0.2)
col.set_facecolor('#4A90E2')
ax.add_collection3d(col)

ax.set_xlim(-16, 16)
ax.set_ylim(-21, -8)
ax.set_zlim(-1, 8)
ax.view_init(elev=35, azim=225)
ax.set_title('Bottom Arch & Inset Exterior Wall Close-Up (Solid Floor)', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('bottom_feature_3d_test.png', dpi=160)
print("Saved bottom_feature_3d_test.png")
