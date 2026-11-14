import numpy as np
import trimesh
import os, sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = base_mesh.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, return_subparts=True, with_supports=False)
shaft_tilted = {}
for k, s in shaft_subparts.items():
    st = s.copy().apply_transform(R)
    st.apply_translation([0, 0, -z_min])
    shaft_tilted[k] = st

full_lever = trimesh.util.concatenate(list(shaft_subparts.values()))
full_lever_tilted = full_lever.copy().apply_transform(R)
full_lever_tilted.apply_translation([0, 0, -z_min])

# Isolate Bracket 4
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

# Old shaft strut from base
shaft_s_x_c = 8.160
shaft_s_y_c = -1.351
z_shaft_lowest = 25.483
gap_shaft = 0.48
z_shaft_stick_top = z_shaft_lowest - gap_shaft
z_floor_shaft_rib = 13.17
shaft_neck = trimesh.creation.box([0.45, 0.45, 0.90])
shaft_neck.apply_translation([shaft_s_x_c, shaft_s_y_c, z_floor_shaft_rib + 0.45])
z_shaft_trunk_base = z_floor_shaft_rib + 0.90
z_shaft_fork_base = 20.00
shaft_trunk_h = z_shaft_fork_base - z_shaft_trunk_base
shaft_trunk = trimesh.creation.box([0.45, 0.55, shaft_trunk_h])
shaft_trunk.apply_translation([shaft_s_x_c, shaft_s_y_c, z_shaft_trunk_base + shaft_trunk_h / 2.0])
z_shaft_notch = z_shaft_stick_top - 0.90
pts_shaft_xz = [
    (7.92, z_shaft_fork_base), (7.92, z_shaft_stick_top), (8.10, z_shaft_stick_top),
    (shaft_s_x_c, z_shaft_notch), (8.22, z_shaft_stick_top), (8.40, z_shaft_stick_top),
    (8.40, z_shaft_fork_base),
]
poly_shaft_xz = Polygon(pts_shaft_xz)
head_shaft_2d = trimesh.creation.extrude_polygon(poly_shaft_xz, height=0.55)
v_s = head_shaft_2d.vertices.copy()
v_s_3d = np.column_stack([v_s[:, 0], v_s[:, 2] - 0.275 + shaft_s_y_c, v_s[:, 1]])
shaft_fork_head = trimesh.Trimesh(vertices=v_s_3d, faces=head_shaft_2d.faces.copy(), process=True)
old_shaft_strut = trimesh.util.concatenate([shaft_neck, shaft_trunk, shaft_fork_head])

# Cam strut
cam_c_x = 6.600
cam_c_y = -2.333
z_cam_lowest = 17.988
gap_cam = 0.28
z_cam_stick_top = z_cam_lowest - gap_cam
z_floor_cam = cam_c_y + 14.523
cam_neck = trimesh.creation.box([0.70, 0.70, 0.90])
cam_neck.apply_translation([cam_c_x, cam_c_y, z_floor_cam + 0.15])
z_trunk_base = z_floor_cam + 0.60
z_fork_base = 15.50
cam_trunk_h = z_fork_base - z_trunk_base
cam_trunk = trimesh.creation.box([1.30, 1.20, cam_trunk_h])
cam_trunk.apply_translation([cam_c_x, cam_c_y, z_trunk_base + cam_trunk_h / 2.0])
z_notch = 16.30
pts_xz = [
    (5.65, z_fork_base), (5.65, z_cam_stick_top), (6.15, z_cam_stick_top),
    (6.60, z_notch), (7.05, z_cam_stick_top), (7.55, z_cam_stick_top),
    (7.55, z_fork_base),
]
poly_xz = Polygon(pts_xz)
head_2d = trimesh.creation.extrude_polygon(poly_xz, height=0.70)
v = head_2d.vertices.copy()
v_3d = np.column_stack([v[:, 0], v[:, 2] - 0.35 + cam_c_y, v[:, 1]])
cam_fork_head = trimesh.Trimesh(vertices=v_3d, faces=head_2d.faces.copy(), process=True)
cam_strut = trimesh.util.concatenate([cam_neck, cam_trunk, cam_fork_head])

# Let's create two variations of the Bracket 4 strut:
# Design 1: Anchored on Bracket 4 top face at Y_flat = 4.95 - 5.50 (hook region), X = 8.16
# Design 2: Anchored on Bracket 4 top wall at Y_flat = 6.00 - 7.17 (pocket region), X = 8.25
from test_candidate_b4_strut import build_strut_option_b
b4_strut_1 = build_strut_option_b(anchor_y_flat=4.95, x_c=8.16, w_x=0.55)

# Design 2: Anchored on Bracket 4 at Y_flat = 6.40, X = 8.20
b4_strut_2 = build_strut_option_b(anchor_y_flat=6.00, x_c=8.18, w_x=0.55)

# Let's render side-by-side close-ups!
fig = plt.figure(figsize=(18, 9), dpi=160)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

for ax, strut_to_show, name, color in [
    (ax1, old_shaft_strut, "Current Setup: Stick from Base (Too Close to Cantilever)", '#f44336'),
    (ax2, b4_strut_1, "Proposed: Strut Off Bracket 4 Ending in Y (Max Clearance)", '#4caf50')
]:
    # Bracket 4
    ax.add_collection3d(Poly3DCollection(b4_tilted.vertices[b4_tilted.faces], alpha=0.35, facecolor='#2196f3', edgecolor='#1565c0', lw=0.3))
    # Lever
    ax.add_collection3d(Poly3DCollection(full_lever_tilted.vertices[full_lever_tilted.faces], alpha=0.75, facecolor='#ff7043', edgecolor='#d84315', lw=0.3))
    # Cantilever / Cam Strut
    ax.add_collection3d(Poly3DCollection(cam_strut.vertices[cam_strut.faces], alpha=0.85, facecolor='#fbc02d', edgecolor='#f57f17', lw=0.4))
    # Strut under test
    ax.add_collection3d(Poly3DCollection(strut_to_show.vertices[strut_to_show.faces], alpha=0.95, facecolor=color, edgecolor='#1b5e20' if color=='#4caf50' else '#b71c1c', lw=0.5))
    
    ax.set_xlim(5, 12)
    ax.set_ylim(-5, 6)
    ax.set_zlim(12, 28)
    ax.view_init(elev=22, azim=-70)
    ax.set_title(name, fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')

plt.suptitle("Shaft Support Comparison: Base Stick vs. Bracket 4 Y-Strut", fontsize=13, fontweight='bold')
plt.tight_layout()
out_png = 'testing/b4_strut_comparison.png'
plt.savefig(out_png)
print(f"Saved {out_png}")
