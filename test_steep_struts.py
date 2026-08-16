"""
Test pure triangular struts with no horizontal top shelf.
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    BASE_THICK, TOWER_HEIGHT, TOWER_Y_LEN, TOWER_WALL_THICK,
    build_clean_shaft_towers_mesh
)

x_left_inner = 5.500
x_left_outer = x_left_inner - TOWER_WALL_THICK  # 4.250mm

y_min = -17.339 + 22.68  # 5.341mm
y_max = y_min + TOWER_Y_LEN  # 9.991mm

z_base = BASE_THICK  # 1.0mm
z_top = z_base + TOWER_HEIGHT  # 13.59mm
z_strut_top = z_top - 2.0  # 11.59mm (2mm from top of tower)

# Pure triangular profile in (X, Z) - NO horizontal flat top!
strut_pts_xz = [
    (x_left_outer - 3.58, z_base),
    (x_left_outer, z_base),
    (x_left_outer, z_strut_top),
]
poly_xz = Polygon(strut_pts_xz)

strut_thick_y = 0.80

m_raw = trimesh.creation.extrude_polygon(poly_xz, height=strut_thick_y)
verts = m_raw.vertices.copy()

# Bottom strut:
verts_bot = np.column_stack([verts[:, 0], verts[:, 2] + y_min, verts[:, 1]])
mesh_bot = trimesh.Trimesh(vertices=verts_bot, faces=m_raw.faces.copy(), process=True)

# Top strut:
verts_top = np.column_stack([verts[:, 0], verts[:, 2] + (y_max - strut_thick_y), verts[:, 1]])
mesh_top = trimesh.Trimesh(vertices=verts_top, faces=m_raw.faces.copy(), process=True)

struts_mesh = trimesh.util.concatenate([mesh_bot, mesh_top])
towers_mesh = build_clean_shaft_towers_mesh()

# Plot 3D
fig = plt.figure(figsize=(10, 8), dpi=160)
ax = fig.add_subplot(1, 1, 1, projection='3d')

col_t = Poly3DCollection(towers_mesh.vertices[towers_mesh.faces], alpha=0.75, edgecolor='#222222', linewidths=0.2)
col_t.set_facecolor('#4A90E2')
ax.add_collection3d(col_t)

col_s = Poly3DCollection(struts_mesh.vertices[struts_mesh.faces], alpha=0.95, edgecolor='#880000', linewidths=0.4)
col_s.set_facecolor('#E74C3C')
ax.add_collection3d(col_s)

ax.set_xlim(-2, 16)
ax.set_ylim(4, 12)
ax.set_zlim(0, 15)
ax.view_init(elev=25, azim=225)
ax.set_title('Steep Triangular Struts with Zero Horizontal Top Shelf', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('steep_struts_preview.png', dpi=160)
print("Saved steep_struts_preview.png")
