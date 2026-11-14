import os, sys
import numpy as np
import trimesh
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

# Isolate Bracket 4
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

# Also isolate Towers
towers_flat = build_part.build_clean_shaft_towers_mesh()
towers_tilted = towers_flat.copy().apply_transform(R)
towers_tilted.apply_translation([0, 0, -z_min])

# Plunger strut
p_x_c = 10.284
p_y_c = 11.30
z_plunger_lowest = 2.52 - z_min
gap_plunger = 0.28
z_p_stick_top = z_plunger_lowest - gap_plunger
z_bed = 0.60
z_p_fork_base = 13.00
p_trunk_h = z_p_fork_base - z_bed
p_trunk = trimesh.creation.box([1.80, 1.80, p_trunk_h])
p_trunk.apply_translation([p_x_c, p_y_c, z_bed + p_trunk_h / 2.0])
z_p_notch = 13.80
pts_p_xz = [
    (8.484, z_p_fork_base), (8.484, z_p_stick_top), (9.284, z_p_stick_top),
    (p_x_c,  z_p_notch), (11.284, z_p_stick_top), (12.084, z_p_stick_top),
    (12.084, z_p_fork_base),
]
poly_p_xz = Polygon(pts_p_xz)
p_head_2d = trimesh.creation.extrude_polygon(poly_p_xz, height=1.00)
v_p = p_head_2d.vertices.copy()
v_p_3d = np.column_stack([v_p[:, 0], v_p[:, 2] - 0.50 + p_y_c, v_p[:, 1]])
p_fork_head = trimesh.Trimesh(vertices=v_p_3d, faces=p_head_2d.faces.copy(), process=True)
plunger_strut = trimesh.util.concatenate([p_trunk, p_fork_head])

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

# Old shaft strut
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

# Plot 4 views
fig = plt.figure(figsize=(18, 14), dpi=150)
views = [
    (30, -60, "Perspective View 1 (Slicer-like)", 1),
    (15, -135, "Perspective View 2 (Front-Left)", 2),
    (0, -90, "Side View (Y-Z plane)", 3),
    (90, -90, "Top View (X-Y plane)", 4),
]

full_lever = trimesh.util.concatenate(list(shaft_subparts.values()))
full_lever_tilted = full_lever.copy().apply_transform(R)
full_lever_tilted.apply_translation([0, 0, -z_min])

for elev, azim, title, idx in views:
    ax = fig.add_subplot(2, 2, idx, projection='3d')
    # Bracket 4 in blue
    ax.add_collection3d(Poly3DCollection(b4_tilted.vertices[b4_tilted.faces], alpha=0.35, facecolor='#2196f3', edgecolor='#1565c0', lw=0.3))
    # Towers in grey
    ax.add_collection3d(Poly3DCollection(towers_tilted.vertices[towers_tilted.faces], alpha=0.20, facecolor='#9e9e9e', edgecolor='none'))
    # Lever in orange
    ax.add_collection3d(Poly3DCollection(full_lever_tilted.vertices[full_lever_tilted.faces], alpha=0.70, facecolor='#ff7043', edgecolor='#d84315', lw=0.3))
    # Plunger strut in purple
    ax.add_collection3d(Poly3DCollection(plunger_strut.vertices[plunger_strut.faces], alpha=0.8, facecolor='#9c27b0', edgecolor='#4a148c', lw=0.4))
    # Cam strut in yellow
    ax.add_collection3d(Poly3DCollection(cam_strut.vertices[cam_strut.faces], alpha=0.8, facecolor='#ffeb3b', edgecolor='#f57f17', lw=0.4))
    # Old shaft strut in red
    ax.add_collection3d(Poly3DCollection(old_shaft_strut.vertices[old_shaft_strut.faces], alpha=0.85, facecolor='#f44336', edgecolor='#b71c1c', lw=0.5))
    
    ax.set_xlim(3, 15)
    ax.set_ylim(-7, 13)
    ax.set_zlim(10, 31)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')

plt.suptitle("Lever, Supports, Bracket 4, and Towers (Red = Old Shaft Stick Support)", fontsize=14, fontweight='bold')
plt.tight_layout()
out_png = 'testing/bracket4_and_lever_views.png'
plt.savefig(out_png)
print(f"Saved {out_png}")
