"""
Test clean U-cradle mesh watertightness and 3D preview.
"""
import numpy as np
from shapely.geometry import Polygon
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

y_min = 5.341
y_max = 9.991
y_shaft = (y_min + y_max) / 2.0  # 7.666mm

z_base = 1.00
z_top = 13.59
r_shaft = 1.00
z_cradle_center = z_top - r_shaft  # 12.59mm

# Semicircular arc from a = 0 (right) to a = pi (left)
angles = np.linspace(0, np.pi, 32)
arc_pts = [(y_shaft + r_shaft * np.cos(a), z_cradle_center - r_shaft * np.sin(a)) for a in angles]

profile_yz = [
    (y_min, z_base),
    (y_max, z_base),
    (y_max, z_top),
    (y_shaft + r_shaft, z_top),
] + arc_pts + [
    (y_shaft - r_shaft, z_top),
    (y_min, z_top)
]

poly = Polygon(profile_yz)
print("Is valid polygon:", poly.is_valid)

# Extrude along X
m_raw = trimesh.creation.extrude_polygon(poly, height=1.25)
print("Mesh is watertight:", m_raw.is_watertight)
print("Mesh volume:", m_raw.volume)

# Plot 3D zoom on the top of the tower
fig = plt.figure(figsize=(10, 8), dpi=160)
ax = fig.add_subplot(1, 1, 1, projection='3d')

verts = m_raw.vertices
# Map [Y, Z, X] -> [X, Y, Z]
verts_3d = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
mesh_3d = trimesh.Trimesh(vertices=verts_3d, faces=m_raw.faces.copy(), process=True)

col = Poly3DCollection(mesh_3d.vertices[mesh_3d.faces], alpha=0.9, edgecolor='#111111', linewidths=0.3)
col.set_facecolor('#4A90E2')
ax.add_collection3d(col)

ax.set_xlim(-1, 3)
ax.set_ylim(4, 11)
ax.set_zlim(10, 15)
ax.view_init(elev=20, azim=230)
ax.set_title('U-Cradle Top Close-Up', fontsize=14, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('u_cradle_3d_closeup.png', dpi=160)
print("Saved u_cradle_3d_closeup.png")
