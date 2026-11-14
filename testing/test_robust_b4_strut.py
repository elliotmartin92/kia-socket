import numpy as np
import trimesh
import os, sys
from scipy.spatial import cKDTree
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

# Let's test a robust Y-strut:
# Width in X: 1.80 mm! (spans X in [8.00, 9.80], center X = 8.90 mm)
# Anchor on Bracket 4:
# In flat coords: Bracket 4 top wall at Y in [6.00, 7.17], Z = 5.60 mm.
# Tilted:
# Y' at flat Y=6.40, Z=5.60 is 0.566 mm, Z' = 21.594 mm.
# Target shaft contact:
# At Y' = -1.351 mm, lowest point is Z' = 25.483 mm.
# Release gap = 0.48 mm -> Z'_top = 25.003 mm.
#
# What if the fork has:
# Total width in X: 1.80 mm (X in [8.00, 9.80])
# Twin tines:
# Left tine: X in [8.00, 8.55] (width 0.55 mm)
# Central notch: X in [8.55, 9.25] (opening 0.70 mm)
# Right tine: X in [9.25, 9.80] (width 0.55 mm)
# Depth in Y: 0.90 mm!
# Neck: 0.70 x 0.70 mm or 0.80 x 0.80 mm at Bracket 4!

def build_robust_strut(x_c=8.90, fork_w=1.80, tine_w=0.55, gap_shaft=0.48):
    cos45 = np.cos(np.pi/4)
    sin45 = np.sin(np.pi/4)
    
    # Anchor point on Bracket 4 top:
    y_flat_b4 = 6.40
    z_flat_b4 = 5.60
    yp_anchor = y_flat_b4 * cos45 - z_flat_b4 * sin45  # ~ 0.566 mm
    zp_anchor = y_flat_b4 * sin45 + z_flat_b4 * cos45 - z_min  # ~ 21.594 mm
    
    yp_target = -1.351
    zp_target = 25.483 - gap_shaft # 25.003 mm
    
    # 1. Easy-snap neck at Bracket 4:
    # 0.70 x 0.70 mm neck, 0.75 mm tall
    neck = trimesh.creation.box([0.70, 0.70, 0.80])
    neck.apply_translation([x_c, yp_anchor, zp_anchor + 0.15])
    
    # 2. Trunk:
    # Rising from zp_anchor + 0.55 to zp_fork_base = 23.60 mm
    zp_trunk_base = zp_anchor + 0.55
    zp_fork_base = 23.60
    pts_trunk_yz = [
        (yp_anchor - 0.40, zp_trunk_base),
        (yp_target - 0.45, zp_fork_base),
        (yp_target + 0.45, zp_fork_base),
        (yp_anchor + 0.40, zp_trunk_base),
    ]
    poly_trunk_yz = Polygon(pts_trunk_yz)
    m_trunk_2d = trimesh.creation.extrude_polygon(poly_trunk_yz, height=1.20)
    v_t = m_trunk_2d.vertices.copy()
    v_t_3d = np.column_stack([v_t[:, 2] + x_c - 0.60, v_t[:, 0], v_t[:, 1]])
    trunk = trimesh.Trimesh(vertices=v_t_3d, faces=m_trunk_2d.faces.copy(), process=True)
    if trunk.volume < 0:
        trunk.faces = np.fliplr(trunk.faces)
        
    # 3. Y-Fork Head:
    # Spans from x_c - fork_w/2 to x_c + fork_w/2: [8.00, 9.80]
    x_left = x_c - fork_w / 2.0
    x_right = x_c + fork_w / 2.0
    z_notch = zp_target - 0.80
    pts_fork_xz = [
        (x_left, zp_fork_base),
        (x_left, zp_target),
        (x_left + tine_w, zp_target),
        (x_c, z_notch),
        (x_right - tine_w, zp_target),
        (x_right, zp_target),
        (x_right, zp_fork_base),
    ]
    poly_fork_xz = Polygon(pts_fork_xz)
    m_fork_2d = trimesh.creation.extrude_polygon(poly_fork_xz, height=0.90)
    v_f = m_fork_2d.vertices.copy()
    v_f_3d = np.column_stack([v_f[:, 0], v_f[:, 2] - 0.45 + yp_target, v_f[:, 1]])
    fork = trimesh.Trimesh(vertices=v_f_3d, faces=m_fork_2d.faces.copy(), process=True)
    if fork.volume < 0:
        fork.faces = np.fliplr(fork.faces)
        
    return trimesh.util.concatenate([neck, trunk, fork])

strut = build_robust_strut()
print("=" * 60)
print("TESTING ROBUST BRACKET 4 SHAFT STRUT")
print("=" * 60)
print(f"Strut bounds:\nX=[{strut.bounds[0,0]:.3f}, {strut.bounds[1,0]:.3f}]\nY=[{strut.bounds[0,1]:.3f}, {strut.bounds[1,1]:.3f}]\nZ=[{strut.bounds[0,2]:.3f}, {strut.bounds[1,2]:.3f}]")

for k, s in shaft_tilted.items():
    tree = cKDTree(s.vertices)
    ds, _ = tree.query(strut.vertices)
    print(f"  vs shaft {k:10s}: min dist = {np.min(ds):.3f} mm")

# Measure distance to cam tab and plunger blade specifically
tree_cam = cKDTree(shaft_tilted['cam'].vertices)
ds_cam, _ = tree_cam.query(strut.vertices)
print(f"\nClearance to Cam Tab:     {np.min(ds_cam):.3f} mm")

tree_p = cKDTree(shaft_tilted['plunger'].vertices)
ds_p, _ = tree_p.query(strut.vertices)
print(f"Clearance to Plunger:     {np.min(ds_p):.3f} mm")
