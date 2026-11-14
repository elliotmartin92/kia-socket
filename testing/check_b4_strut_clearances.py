import numpy as np
import trimesh
import os, sys
from scipy.spatial import cKDTree

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft
from test_candidate_b4_strut import build_strut_option_b, R, z_min, shaft_tilted, b4_tilted

strut = build_strut_option_b()

print("=" * 60)
print("CLEARANCE CHECK FOR NEW BRACKET 4 SHAFT STRUT")
print("=" * 60)

for k, s in shaft_tilted.items():
    tree = cKDTree(s.vertices)
    ds, _ = tree.query(strut.vertices)
    min_d = np.min(ds)
    print(f"Distance to shaft {k:10s}: {min_d:.3f} mm")

tree_b4 = cKDTree(b4_tilted.vertices)
ds_b4, _ = tree_b4.query(strut.vertices)
print(f"Min distance to Bracket 4 (at root): {np.min(ds_b4):.3f} mm")

# Cam tab support strut
# Let's check distance to the cam tab support strut:
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
from shapely.geometry import Polygon
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

tree_cam_strut = cKDTree(cam_strut.vertices)
ds_cam_strut, _ = tree_cam_strut.query(strut.vertices)
print(f"Min distance to Cam Support Strut: {np.min(ds_cam_strut):.3f} mm")
