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

def create_b4_shaft_strut(x_c=8.092, fork_w_x=0.50, gap_shaft=0.48):
    """
    Creates the dedicated breakaway support strut off Bracket 4 supporting the lever shaft hub barrel:
    - Root: anchored solidly on the top face / hook region of Bracket 4 with an easy-snap breakaway neck.
    - Trunk: short, rigid column rising from Bracket 4 up to the fork base.
    - Y-Fork Head: twin contact lands with central V-notch cradling the floating shaft barrel with calibrated release gap.
    """
    cos45 = np.cos(np.pi/4)
    sin45 = np.sin(np.pi/4)
    
    # Anchor point on Bracket 4:
    # Bracket 4 top face is at Z_flat = 5.60mm.
    # At X ~ 8.092, Bracket 4 has hook / pocket region.
    # We choose flat Y_anchor = 5.20mm (between 4.95mm hook face and 7.17mm top wall).
    y_flat_anchor = 5.20
    z_flat_anchor = 5.60
    yp_anchor = y_flat_anchor * cos45 - z_flat_anchor * sin45  # ~ -0.283mm
    zp_anchor = y_flat_anchor * sin45 + z_flat_anchor * cos45 - z_min  # ~ 20.746mm
    
    # Target hub contact:
    # Lowest point of hub cylinder: Y' = -1.351mm, Z' = 25.483mm.
    yp_target = -1.351
    zp_target = 25.483 - gap_shaft  # 25.003mm
    
    # 1. Easy-snap breakaway neck at Bracket 4:
    # 0.50mm x 0.50mm neck, embedded 0.25mm into Bracket 4 for solid fusion, rising 0.60mm above surface
    neck = trimesh.creation.box([0.50, 0.50, 0.85])
    neck.apply_translation([x_c, yp_anchor, zp_anchor + 0.175])
    
    # 2. Trunk:
    # Rises from zp_anchor + 0.60 to zp_fork_base
    zp_trunk_base = zp_anchor + 0.60
    zp_fork_base = 23.60
    
    # Sweep trunk in Y'Z' plane
    pts_trunk_yz = [
        (yp_anchor - 0.25, zp_trunk_base),
        (yp_target - 0.28, zp_fork_base),
        (yp_target + 0.28, zp_fork_base),
        (yp_anchor + 0.25, zp_trunk_base),
    ]
    poly_trunk_yz = Polygon(pts_trunk_yz)
    m_trunk_2d = trimesh.creation.extrude_polygon(poly_trunk_yz, height=0.48)
    v_t = m_trunk_2d.vertices.copy()
    v_t_3d = np.column_stack([v_t[:, 2] + x_c - 0.24, v_t[:, 0], v_t[:, 1]])
    trunk = trimesh.Trimesh(vertices=v_t_3d, faces=m_trunk_2d.faces.copy(), process=True)
    if trunk.volume < 0:
        trunk.faces = np.fliplr(trunk.faces)
        
    # 3. Y-Fork Head:
    # Symmetrical in X around x_c: [x_c - fork_w_x/2, x_c + fork_w_x/2]
    # Spans from 8.092 - 0.25 = 7.842 to 8.092 + 0.25 = 8.342.
    x_left = x_c - fork_w_x / 2.0
    x_right = x_c + fork_w_x / 2.0
    tine_w = 0.18
    z_notch = zp_target - 0.75
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
    m_fork_2d = trimesh.creation.extrude_polygon(poly_fork_xz, height=0.55)
    v_f = m_fork_2d.vertices.copy()
    v_f_3d = np.column_stack([v_f[:, 0], v_f[:, 2] - 0.275 + yp_target, v_f[:, 1]])
    fork = trimesh.Trimesh(vertices=v_f_3d, faces=m_fork_2d.faces.copy(), process=True)
    if fork.volume < 0:
        fork.faces = np.fliplr(fork.faces)
        
    return trimesh.util.concatenate([neck, trunk, fork])

strut = create_b4_shaft_strut()
print("=" * 60)
print("TESTING PERFECTED BRACKET 4 SHAFT STRUT")
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

# Gap to shaft hub underside
# Lowest point of hub cylinder is Z'=25.483, strut top is Z'=25.003 -> gap = 0.480mm
gap = 25.483 - strut.bounds[1, 2]
print(f"Release gap to shaft hub: {gap:.3f} mm")
