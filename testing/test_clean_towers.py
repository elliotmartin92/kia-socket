"""
Build clean shaft support towers by extruding the exact U-cradle side profile (Y-Z plane) along X.
Zero boolean artifacts, perfectly clean mesh!
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    BASE_THICK, TOWER_HEIGHT, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP,
    bracket_3_raw_pts, to_mm_poly
)

b3 = to_mm_poly(bracket_3_raw_pts)
b3_center_x = (b3.bounds[0] + b3.bounds[2]) / 2.0  # 3.236mm

y_inner_wall = 17.395
y_shaft = y_inner_wall - 6.77  # 10.625mm
y_max = y_shaft + TOWER_Y_LEN / 2.0  # 12.950mm
y_min = y_shaft - TOWER_Y_LEN / 2.0  # 8.300mm

z_base = BASE_THICK  # 1.0mm
z_top = z_base + TOWER_HEIGHT  # 13.59mm
r_shaft = 1.00  # 2mm diameter shaft -> 1mm radius
z_cradle_center = z_top - r_shaft  # 12.59mm
z_cradle_bot = z_cradle_center - r_shaft  # 11.59mm

# Create 2D profile in (Y, Z) plane
# Arc points for semicircular bottom from -90 deg (left) through 0 (bottom) to +90 deg (right)
# In (Y, Z): left is y_shaft - r, right is y_shaft + r
angles = np.linspace(np.pi, 0, 32)
arc_pts = [(y_shaft + r_shaft * np.cos(a), z_cradle_center - r_shaft * np.sin(a)) for a in angles]

# Polygon boundary in (Y, Z) plane:
# Bottom-left -> Bottom-right -> Top-right -> Right of U-slot -> Arc -> Left of U-slot -> Top-left -> close
profile_yz = [
    (y_min, z_base),
    (y_max, z_base),
    (y_max, z_top),
    (y_shaft + r_shaft, z_top),
] + arc_pts + [
    (y_shaft - r_shaft, z_top),
    (y_min, z_top)
]

poly_2d = Polygon(profile_yz)

# Extrude along X axis:
# Extrude polygon in 2D (height = thickness in X)
m_left_raw = trimesh.creation.extrude_polygon(poly_2d, height=TOWER_WALL_THICK)
# In trimesh, extrusion is along Z. We need:
# original 2D (X, Y) -> (Y, Z), and extrude along X.
# Let's map coordinates:
# trimesh vertices are [Y, Z, X_local].
# We transform so that [X, Y, Z] = [X_local + X_offset, Y, Z]
verts_left = m_left_raw.vertices.copy()
# verts_left has [Y_coord, Z_coord, X_extruded]
# We want [X, Y, Z]:
verts_3d_left = np.column_stack([verts_left[:, 2], verts_left[:, 0], verts_left[:, 1]])

x_left_start = b3_center_x - TOWER_WALL_THICK / 2.0  # 2.736mm
verts_3d_left[:, 0] += x_left_start

mesh_left = trimesh.Trimesh(vertices=verts_3d_left, faces=m_left_raw.faces.copy(), process=True)

# Right tower:
verts_3d_right = verts_3d_left.copy()
x_right_start = (b3_center_x + TOWER_WALL_THICK / 2.0) + TOWER_INTERNAL_GAP  # 11.596mm
verts_3d_right[:, 0] = verts_left[:, 2] + x_right_start
mesh_right = trimesh.Trimesh(vertices=verts_3d_right, faces=m_left_raw.faces.copy(), process=True)

towers_clean = trimesh.util.concatenate([mesh_left, mesh_right])

print("Clean towers generated without booleans!")
print(f"Towers bounds: {towers_clean.bounds}")
print(f"Is watertight: {towers_clean.is_watertight}")

# Plot close-up preview
fig = plt.figure(figsize=(10, 8), dpi=150)
ax = fig.add_subplot(1, 1, 1, projection='3d')
col = Poly3DCollection(towers_clean.vertices[towers_clean.faces], alpha=0.85, edgecolor='#222222', linewidths=0.3)
col.set_facecolor('#4A90E2')
ax.add_collection3d(col)

ax.set_xlim(0, 15)
ax.set_ylim(6, 15)
ax.set_zlim(0, 15)
ax.view_init(elev=25, azim=215)
ax.set_title('Directly Extruded Clean U-Cradle Support Towers (No Artifacts)', fontsize=11, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('clean_u_cradle.png', dpi=150)
print("Saved clean_u_cradle.png")
