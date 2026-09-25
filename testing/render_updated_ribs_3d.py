"""
testing/render_updated_ribs_3d.py
Renders a high-detail 3D visualization of the updated rib configuration in the right bracket set.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_part as bp

z_floor = bp.BASE_THICK  # 1.00 mm
z_rib = z_floor + bp.BRACKET_SEATING_RIB_HEIGHT  # 2.15 mm
h_rib = bp.BRACKET_SEATING_RIB_HEIGHT  # 1.15 mm

b3_spine = 2.701
b4_spine = 9.857
ext = bp.BRACKET_SEATING_RIB_EXT
thick = bp.BRACKET_SEATING_RIB_THICK

# Standard ribs on right side (stations 1, 2, 3)
std_boxes = []
for y_c in bp.BRACKET_SEATING_RIB_Y[:3]:
    y_min = y_c - thick / 2.0
    y_max = y_c + thick / 2.0
    std_boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
    std_boxes.append(box(b4_spine - ext, y_min, b4_spine, y_max))

poly_std = bp.unary_union(std_boxes)
m_std = bp.extrude_shapely_geom(poly_std, height=h_rib)
m_std.apply_translation([0, 0, z_floor])

# Chamfered continuous rib below half moon
chamf_dy = 0.80
y_c4 = -4.65
pts_yz = [
    (y_c4 - thick/2.0 - chamf_dy, z_floor),
    (y_c4 - thick/2.0, z_rib),
    (min(y_c4 + thick/2.0, -4.30), z_rib),
    (-4.30, z_floor)
]
poly_yz = Polygon(pts_yz)
span_r4 = b4_spine - b3_spine
m_r4_poly = trimesh.creation.extrude_polygon(poly_yz, height=span_r4)
v4 = m_r4_poly.vertices.copy()
v_r4 = np.column_stack([v4[:, 2] + b3_spine, v4[:, 0], v4[:, 1]])
m_r4 = trimesh.Trimesh(vertices=v_r4, faces=m_r4_poly.faces.copy(), process=True)

# Half moon
m_hm = bp.extrude_shapely_geom(bp.create_center_curved_feature_poly(), height=9.50)
m_hm.apply_translation([0, 0, z_floor])

# Bracket 3 and 4 walls (baseplate to 4.60mm)
b3_poly = bp.to_mm_poly(bp.bracket_3_raw_pts)
b4_poly = bp.to_mm_poly(bp.bracket_4_raw_pts)
m_b3 = bp.extrude_shapely_geom(b3_poly, height=bp.BRACKET_HEIGHT)
m_b3.apply_translation([0, 0, z_floor])
m_b4 = bp.extrude_shapely_geom(b4_poly, height=bp.BRACKET_HEIGHT)
m_b4.apply_translation([0, 0, z_floor])

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

def plot_mesh(mesh, color, alpha=0.5, label=None):
    polys = mesh.vertices[mesh.faces]
    coll = Poly3DCollection(polys, facecolors=color, edgecolors='black', linewidths=0.2, alpha=alpha)
    ax.add_collection3d(coll)

plot_mesh(m_std, 'royalblue', alpha=0.8, label='Standard Unchamfered Ribs (1-3)')
plot_mesh(m_r4, 'limegreen', alpha=0.9, label='One Chamfered Continuous Rib Below Moon (4)')
plot_mesh(m_hm, 'magenta', alpha=0.7, label='Calibrated Half Moon')
plot_mesh(m_b3, 'lightgray', alpha=0.25, label='Bracket 3')
plot_mesh(m_b4, 'lightgray', alpha=0.25, label='Bracket 4')

ax.set_xlim([1.0, 11.5])
ax.set_ylim([-8.0, 8.0])
ax.set_zlim([0.0, 12.0])

ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Z (mm)')
ax.view_init(elev=28, azim=-55)
ax.set_title('3D Detail: Right Bracket Set with Selective Rib Chamfer\n(Only Rib 4 Extended Across & Chamfered; Ribs 1-3 Unchamfered)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('testing/updated_ribs_3d.png', dpi=200)
print("Saved testing/updated_ribs_3d.png")
