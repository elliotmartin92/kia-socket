"""
Visualize the two shaft support towers above the top-right hole.
"""
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly, create_grid_ribs_poly,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_HEIGHT, BRACKET_HEIGHT, BASE_THICK, build_exact_3d_model
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
hole_x, hole_y, hole_w, hole_h = hole_info

b3 = to_mm_poly(bracket_3_raw_pts)
b3_center_x = (b3.bounds[0] + b3.bounds[2]) / 2.0  # 3.236mm

TOWER_HEIGHT = 12.59  # Protrudes 12.59mm above face (Z: 1.0 to 13.59mm)
TOWER_Y_LEN = 4.65   # 4.65mm in Y
INTERNAL_GAP = 7.86  # 7.86mm internal distance in X
TOWER_THICK_X = 1.0  # Default 1.0mm wall thickness in X (to be confirmed)

y_mid = hole_y       # Centered in Y with the hole (~10.83mm)
y_min = y_mid - TOWER_Y_LEN / 2.0
y_max = y_mid + TOWER_Y_LEN / 2.0

# Left Tower: Centered at b3_center_x (3.236mm)
# Inner face of left tower is at b3_center_x + TOWER_THICK_X / 2.0
x_left_min = b3_center_x - TOWER_THICK_X / 2.0
x_left_max = b3_center_x + TOWER_THICK_X / 2.0

# Right Tower: Inner face is at (x_left_max + INTERNAL_GAP)
x_right_min = x_left_max + INTERNAL_GAP
x_right_max = x_right_min + TOWER_THICK_X

left_tower_box = box(x_left_min, y_min, x_left_max, y_max)
right_tower_box = box(x_right_min, y_min, x_right_max, y_max)

print(f"Left tower bounds: X=[{x_left_min:.3f}, {x_left_max:.3f}], Y=[{y_min:.3f}, {y_max:.3f}]")
print(f"Right tower bounds: X=[{x_right_min:.3f}, {x_right_max:.3f}], Y=[{y_min:.3f}, {y_max:.3f}]")
print(f"Internal distance between towers: {x_right_min - x_left_max:.3f} mm")

# Generate preview
fig = plt.figure(figsize=(18, 7), dpi=150)

# Panel 1: 2D Top Profile with Tower Footprints
ax1 = fig.add_subplot(1, 2, 1)
x, y = base_poly.exterior.xy
ax1.plot(x, y, color='#1f77b4', linewidth=2)
for interior in base_poly.interiors:
    ix, iy = interior.xy
    ax1.plot(ix, iy, color='#d62728', linewidth=1.5)

brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax1.plot(bx, by, color='#2ca02c', linewidth=1.5)

# Towers in Magenta
for t_box, name in [(left_tower_box, 'Left Support Tower'), (right_tower_box, 'Right Support Tower')]:
    tx, ty = t_box.exterior.xy
    ax1.fill(tx, ty, color='#e377c2', alpha=0.8, edgecolor='#7f7f7f', linewidth=1.5)
    ax1.plot(tx, ty, color='#d62728', linewidth=1.5)

ax1.annotate(f'Internal Spacing: {INTERNAL_GAP}mm',
            xy=((x_left_max + x_right_min)/2, y_mid), xytext=((x_left_max + x_right_min)/2, y_mid - 3.5),
            fontsize=8.5, fontweight='bold', color='purple', ha='center',
            arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))

ax1.set_title('Top-Down 2D Profile with Shaft Support Towers', fontsize=11, fontweight='bold')
ax1.set_aspect('equal')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.set_xlim(-22, 22)
ax1.set_ylim(-22, 22)

# Panel 2: 3D Isometric View with Support Towers
part_mesh, _ = build_exact_3d_model()

# Build 3D mesh for towers
left_mesh = trimesh.creation.box([TOWER_THICK_X, TOWER_Y_LEN, TOWER_HEIGHT])
left_mesh.apply_translation([(x_left_min + x_left_max)/2, y_mid, BASE_THICK + TOWER_HEIGHT/2])

right_mesh = trimesh.creation.box([TOWER_THICK_X, TOWER_Y_LEN, TOWER_HEIGHT])
right_mesh.apply_translation([(x_right_min + x_right_max)/2, y_mid, BASE_THICK + TOWER_HEIGHT/2])

tower_meshes = trimesh.util.concatenate([left_mesh, right_mesh])
combined_mesh = trimesh.util.concatenate([part_mesh, tower_meshes])

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
vertices = combined_mesh.vertices
faces = combined_mesh.faces

mesh_col = Poly3DCollection(vertices[faces], alpha=0.75, edgecolor='#333333', linewidths=0.2)
mesh_col.set_facecolor('#4A90E2')
ax2.add_collection3d(mesh_col)

ax2.set_xlim(-24, 24)
ax2.set_ylim(-24, 24)
ax2.set_zlim(-4, 15)
ax2.view_init(elev=25, azim=215)
ax2.set_title(f'3D Isometric (Shaft Support Towers: {TOWER_HEIGHT}mm Tall)', fontsize=11, fontweight='bold')
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('shaft_supports_preview.png', dpi=150)
print("Saved shaft_supports_preview.png")
