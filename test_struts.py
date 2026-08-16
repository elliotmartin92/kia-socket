"""
Test and visualize the triangular struts on the left tower.
"""
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

from build_part import (
    BASE_THICK, TOWER_HEIGHT, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP,
    build_clean_shaft_towers_mesh
)

# Left tower bounds:
x_left_inner = 5.500
x_left_outer = 5.500 - TOWER_WALL_THICK  # 4.250mm

y_min = -17.339 + 22.68  # 5.341mm
y_max = y_min + TOWER_Y_LEN  # 9.991mm

z_base = BASE_THICK  # 1.0mm
z_top = z_base + TOWER_HEIGHT  # 13.59mm
z_strut_top = z_top - 2.0  # 11.59mm (2mm from top of tower)

# Strut geometry in (X, Z) plane:
# At z_base (Z=1.0mm): extends out by 3.58mm in -X -> X = x_left_outer - 3.58 = 0.670mm
# At z_strut_top (Z=11.59mm): extends out by 1.25mm in -X -> X = x_left_outer - 1.25 = 3.000mm
# At tower wall: X = x_left_outer = 4.250mm
strut_pts_xz = [
    (x_left_outer - 3.58, z_base),
    (x_left_outer, z_base),
    (x_left_outer, z_strut_top),
    (x_left_outer - 1.25, z_strut_top)
]
poly_xz = Polygon(strut_pts_xz)

# Strut thickness in Y (e.g. 0.8mm or 1.0mm or 1.25mm)
STRUT_THICK_Y = 0.80

# Extrude in Y for the bottom strut (at y_min to y_min + STRUT_THICK_Y)
# and top strut (at y_max - STRUT_THICK_Y to y_max)
m_raw = trimesh.creation.extrude_polygon(poly_xz, height=STRUT_THICK_Y)
verts = m_raw.vertices.copy()

# Map [X_coord, Z_coord, Y_extruded] -> [X, Y, Z]
# Bottom strut:
verts_bot = np.column_stack([verts[:, 0], verts[:, 2] + y_min, verts[:, 1]])
mesh_strut_bot = trimesh.Trimesh(vertices=verts_bot, faces=m_raw.faces.copy(), process=True)

# Top strut:
verts_top = np.column_stack([verts[:, 0], verts[:, 2] + (y_max - STRUT_THICK_Y), verts[:, 1]])
mesh_strut_top = trimesh.Trimesh(vertices=verts_top, faces=m_raw.faces.copy(), process=True)

struts_mesh = trimesh.util.concatenate([mesh_strut_bot, mesh_strut_top])
towers_mesh = build_clean_shaft_towers_mesh()

print("Struts generated!")
print(f"Struts bounds: {struts_mesh.bounds}")

# Plot 3D preview of left tower with struts
fig = plt.figure(figsize=(10, 8), dpi=150)
ax = fig.add_subplot(1, 1, 1, projection='3d')

col_t = Poly3DCollection(towers_mesh.vertices[towers_mesh.faces], alpha=0.7, edgecolor='#222222', linewidths=0.2)
col_t.set_facecolor('#4A90E2')
ax.add_collection3d(col_t)

col_s = Poly3DCollection(struts_mesh.vertices[struts_mesh.faces], alpha=0.9, edgecolor='#880000', linewidths=0.3)
col_s.set_facecolor('#E74C3C')
ax.add_collection3d(col_s)

ax.set_xlim(-2, 16)
ax.set_ylim(4, 12)
ax.set_zlim(0, 15)
ax.view_init(elev=28, azim=225)
ax.set_title('Left Tower with Triangular Buttress Struts', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('struts_preview.png', dpi=150)
print("Saved struts_preview.png")
