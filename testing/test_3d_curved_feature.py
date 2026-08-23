"""
Test 3D integration of 10.5mm tall curved feature with Option 1A positioning.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    build_exact_3d_model, get_exact_base_polygon, create_all_brackets_poly,
    BASE_THICK
)

cx = 6.279
w_x = 4.30
h_y = 1.62
rx = w_x / 2.0
ry = h_y
wall_t = 0.60
rib_t = 0.60

datum_y = -17.339 + 11.27  # -6.069 mm
base_y = datum_y + 2.00    # -4.069 mm

angles = np.linspace(np.pi, 0, 32)
out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
in_arc = [(cx + (rx - wall_t) * np.cos(a), base_y + (ry - wall_t) * np.sin(a)) for a in angles]

wall_poly = Polygon(out_arc + list(reversed(in_arc)))
rib_poly = box(cx - rib_t/2.0, base_y, cx + rib_t/2.0, base_y + ry)
curved_feat_poly = unary_union([wall_poly, rib_poly])

# Extrude to 10.5mm total height (Z: 1.0 to 10.5mm)
feat_mesh = trimesh.creation.extrude_polygon(curved_feat_poly, height=10.5 - BASE_THICK)
feat_mesh.apply_translation([0, 0, BASE_THICK])

# Load part mesh
part_mesh, _ = build_exact_3d_model()
combo = trimesh.util.concatenate([part_mesh, feat_mesh])

# Plot 3D
fig = plt.figure(figsize=(12, 9), dpi=160)
ax = fig.add_subplot(1, 1, 1, projection='3d')
mesh_col = Poly3DCollection(combo.vertices[combo.faces], alpha=0.8, edgecolor='#333333', linewidths=0.15)
mesh_col.set_facecolor('#4A90E2')
ax.add_collection3d(mesh_col)

# Highlight new feature in magenta
feat_col = Poly3DCollection(feat_mesh.vertices[feat_mesh.faces], alpha=0.95, edgecolor='#4a148c', linewidths=0.3)
feat_col.set_facecolor('#d500f9')
ax.add_collection3d(feat_col)

ax.set_xlim(-24, 24)
ax.set_ylim(-24, 24)
ax.set_zlim(-3, 15)
ax.view_init(elev=35, azim=230)
ax.set_title('3D Assembly with 10.5mm Tall Curved Feature (Option 1A)', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('new_curved_feature_3d.png', dpi=160)
print("Saved new_curved_feature_3d.png")
