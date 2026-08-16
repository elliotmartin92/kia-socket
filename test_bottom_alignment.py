"""
Test exact alignment of bottom perimeter notch with the bottom arch wall in 2D and 3D.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box
import trimesh
import matplotlib.pyplot as plt

from build_part import (
    outer_pts, create_arch_wall_poly, OUTER_WALL_THICK,
    OUTER_WALL_HEIGHT, BASE_THICK
)

def get_aligned_outer_pts(notch_x_left=-3.70, notch_x_right=3.70):
    pts = outer_pts.copy()
    for idx, (x, y) in enumerate(pts):
        if abs(y - (-18.539)) < 0.05:
            if abs(x - 1.382) < 0.05:
                pts[idx] = [notch_x_right, -18.539]
            elif abs(x - (-2.291)) < 0.05:
                pts[idx] = [notch_x_left, -18.539]
        elif abs(y - (-16.650)) < 0.05:
            if abs(x - 1.382) < 0.05:
                pts[idx] = [notch_x_right, -16.650]
            elif abs(x - (-2.291)) < 0.05:
                pts[idx] = [notch_x_left, -16.650]
    return pts

pts_aligned = get_aligned_outer_pts()
outer_body_poly = Polygon(pts_aligned)
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_2d = outer_body_poly.difference(inner_wall_poly)
arch_poly = create_arch_wall_poly()

# 2D Plot
fig, axes = plt.subplots(1, 2, figsize=(18, 7), dpi=160)

axes[0].plot(*outer_body_poly.exterior.xy, 'b-o', markersize=3, label='Exterior Perimeter Wall')
axes[0].plot(*inner_wall_poly.exterior.xy, 'b--', alpha=0.5, label='Inner Perimeter Wall')
axes[0].plot(*arch_poly.exterior.xy, 'r-', linewidth=2, label='Bottom Central Arch Wall (5mm inner)')
axes[0].axvline(-3.70, color='gray', linestyle=':', label='X = -3.70mm (Arch Outer Leg)')
axes[0].axvline(3.70, color='gray', linestyle=':', label='X = +3.70mm (Arch Outer Leg)')
axes[0].axvline(-2.50, color='purple', linestyle=':', label='X = -2.50mm (Arch Inner Leg)')
axes[0].axvline(2.50, color='purple', linestyle=':', label='X = +2.50mm (Arch Inner Leg)')
axes[0].set_xlim(-12, 12)
axes[0].set_ylim(-20, -8)
axes[0].set_aspect('equal')
axes[0].grid(True)
axes[0].set_title('2D Plan View: Inset Wall Notch Aligned to Arch Sidewalls', fontsize=12, fontweight='bold')
axes[0].legend(loc='upper right')

# 3D Mesh rendering of bottom region
mesh_base = trimesh.creation.extrude_polygon(outer_body_poly, height=BASE_THICK)
mesh_wall = trimesh.creation.extrude_polygon(wall_2d, height=OUTER_WALL_HEIGHT - BASE_THICK)
mesh_wall.apply_translation([0, 0, BASE_THICK])
mesh_arch = trimesh.creation.extrude_polygon(arch_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
mesh_arch.apply_translation([0, 0, BASE_THICK])

combo = trimesh.util.concatenate([mesh_base, mesh_wall, mesh_arch])

from mpl_toolkits.mplot3d.art3d import Poly3DCollection
dists = np.linalg.norm(combo.vertices[:, :2] - np.array([0, -15]), axis=1)
mask = np.all(dists[combo.faces] < 12.0, axis=1)
faces = combo.faces[mask]

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
col = Poly3DCollection(combo.vertices[faces], alpha=0.9, edgecolor='#222222', linewidths=0.25)
col.set_facecolor('#00bcd4')
ax2.add_collection3d(col)
ax2.set_xlim(-10, 10)
ax2.set_ylim(-20, -10)
ax2.set_zlim(0, 8)
ax2.view_init(elev=35, azim=-90)
ax2.set_title('3D View: Seamless Aligned Bottom Central Arch & Inset Wall', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('aligned_bottom_arch_and_wall.png', dpi=160)
print("Saved aligned_bottom_arch_and_wall.png")
