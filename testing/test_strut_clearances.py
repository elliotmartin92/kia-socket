"""
testing/test_strut_clearances.py
Verifies clearances and release gaps for the 3 PIP lever breakaway support struts:
1. Plunger support strut (twin tines under plunger blade)
2. Cam tab support strut (twin tines under cam contact ramp)
3. Hub barrel support strut (slender Y-fork under floating hub barrel)
"""

import os
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_part import build_exact_3d_model
from build_shaft import build_shaft_rocker_mesh

def test_supports():
    print("=" * 65)
    print("TESTING STRUT CLEARANCES & RELEASE GAPS")
    print("=" * 65)
    
    base_mesh, _ = build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
    shaft_tilted = shaft_mesh.copy().apply_transform(R)
    shaft_tilted.apply_translation([0, 0, -z_min])
    
    tree_shaft = cKDTree(shaft_tilted.vertices)
    
    # 1. Plunger support
    p_x_c = 10.284
    p_y_c = 11.30
    z_plunger_lowest = 2.52 - z_min  # ~15.63mm
    gap_plunger = 0.28
    z_p_stick_top = z_plunger_lowest - gap_plunger
    z_bed = 0.60
    z_p_fork_base = 13.00
    p_trunk_h = z_p_fork_base - z_bed
    p_trunk = trimesh.creation.box([1.80, 1.80, p_trunk_h])
    p_trunk.apply_translation([p_x_c, p_y_c, z_bed + p_trunk_h / 2.0])
    
    from shapely.geometry import Polygon
    z_p_notch = 13.80
    pts_p_xz = [
        (8.484, z_p_fork_base),
        (8.484, z_p_stick_top),
        (9.284, z_p_stick_top),
        (p_x_c,  z_p_notch),
        (11.284, z_p_stick_top),
        (12.084, z_p_stick_top),
        (12.084, z_p_fork_base),
    ]
    poly_p_xz = Polygon(pts_p_xz)
    p_head_2d = trimesh.creation.extrude_polygon(poly_p_xz, height=1.00)
    v_p = p_head_2d.vertices.copy()
    v_p_3d = np.column_stack([v_p[:, 0], v_p[:, 2] - 0.50 + p_y_c, v_p[:, 1]])
    p_fork_head = trimesh.Trimesh(vertices=v_p_3d, faces=p_head_2d.faces.copy(), process=True)
    m_plunger_strut = trimesh.util.concatenate([p_trunk, p_fork_head])
    
    d_p, _ = tree_shaft.query(m_plunger_strut.vertices)
    min_d_p = np.min(d_p)
    print(f"Plunger strut min distance to shaft: {min_d_p:.3f} mm (Target release gap: ~0.28 mm)")
    assert 0.20 <= min_d_p <= 0.45, f"Plunger strut distance {min_d_p:.3f} out of range"
    
    # 2. Cam tab support
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
        (5.65, z_fork_base),
        (5.65, z_cam_stick_top),
        (6.15, z_cam_stick_top),
        (6.60, z_notch),
        (7.05, z_cam_stick_top),
        (7.55, z_cam_stick_top),
        (7.55, z_fork_base),
    ]
    poly_xz = Polygon(pts_xz)
    head_2d = trimesh.creation.extrude_polygon(poly_xz, height=0.70)
    v = head_2d.vertices.copy()
    v_3d = np.column_stack([v[:, 0], v[:, 2] - 0.35 + cam_c_y, v[:, 1]])
    cam_fork_head = trimesh.Trimesh(vertices=v_3d, faces=head_2d.faces.copy(), process=True)
    m_cam_strut = trimesh.util.concatenate([cam_neck, cam_trunk, cam_fork_head])
    
    d_c, _ = tree_shaft.query(m_cam_strut.vertices)
    min_d_c = np.min(d_c)
    print(f"Cam strut min distance to shaft: {min_d_c:.3f} mm (Target release gap: ~0.28 mm)")
    assert 0.20 <= min_d_c <= 0.55, f"Cam strut distance {min_d_c:.3f} out of range"
    
    # 3. Hub support off Bracket 4:
    # shaft_s_x_c = 8.900, yp_hub_target = -1.351, z_shaft_lowest = 25.483, gap_shaft = 0.48
    shaft_s_x_c = 8.900
    cos45 = np.cos(np.pi / 4)
    sin45 = np.sin(np.pi / 4)
    y_flat_b4 = 6.40
    z_flat_b4 = 5.60
    yp_b4_anchor = y_flat_b4 * cos45 - z_flat_b4 * sin45
    zp_b4_anchor = y_flat_b4 * sin45 + z_flat_b4 * cos45 - z_min
    
    yp_hub_target = -1.351
    z_shaft_lowest = 25.483
    gap_shaft = 0.48
    z_shaft_stick_top = z_shaft_lowest - gap_shaft  # 25.003
    
    shaft_neck = trimesh.creation.box([0.70, 0.70, 0.80])
    shaft_neck.apply_translation([shaft_s_x_c, yp_b4_anchor, zp_b4_anchor + 0.15])
    
    zp_trunk_base = zp_b4_anchor + 0.55
    zp_fork_base = 23.60
    pts_trunk_yz = [
        (yp_b4_anchor - 0.40, zp_trunk_base),
        (yp_hub_target - 0.45, zp_fork_base),
        (yp_hub_target + 0.45, zp_fork_base),
        (yp_b4_anchor + 0.40, zp_trunk_base),
    ]
    poly_trunk_yz = Polygon(pts_trunk_yz)
    m_trunk_2d = trimesh.creation.extrude_polygon(poly_trunk_yz, height=1.20)
    v_t = m_trunk_2d.vertices.copy()
    v_t_3d = np.column_stack([v_t[:, 2] + shaft_s_x_c - 0.60, v_t[:, 0], v_t[:, 1]])
    shaft_trunk = trimesh.Trimesh(vertices=v_t_3d, faces=m_trunk_2d.faces.copy(), process=True)
    if shaft_trunk.volume < 0:
        shaft_trunk.faces = np.fliplr(shaft_trunk.faces)
        
    x_fork_w = 1.80
    x_left = shaft_s_x_c - x_fork_w / 2.0
    x_right = shaft_s_x_c + x_fork_w / 2.0
    tine_w = 0.55
    z_shaft_notch = z_shaft_stick_top - 0.80
    pts_shaft_xz = [
        (x_left, zp_fork_base),
        (x_left, z_shaft_stick_top),
        (x_left + tine_w, z_shaft_stick_top),
        (shaft_s_x_c, z_shaft_notch),
        (x_right - tine_w, z_shaft_stick_top),
        (x_right, z_shaft_stick_top),
        (x_right, zp_fork_base),
    ]
    poly_shaft_xz = Polygon(pts_shaft_xz)
    head_shaft_2d = trimesh.creation.extrude_polygon(poly_shaft_xz, height=0.90)
    v_s = head_shaft_2d.vertices.copy()
    v_s_3d = np.column_stack([v_s[:, 0], v_s[:, 2] - 0.45 + yp_hub_target, v_s[:, 1]])
    shaft_fork_head = trimesh.Trimesh(vertices=v_s_3d, faces=head_shaft_2d.faces.copy(), process=True)
    if shaft_fork_head.volume < 0:
        shaft_fork_head.faces = np.fliplr(shaft_fork_head.faces)
    m_shaft_strut = trimesh.util.concatenate([shaft_neck, shaft_trunk, shaft_fork_head])
    
    d_s, _ = tree_shaft.query(m_shaft_strut.vertices)
    min_d_s = np.min(d_s)
    print(f"Hub strut min distance to shaft: {min_d_s:.3f} mm (Target release gap: ~0.48 mm)")
    assert 0.35 <= min_d_s <= 0.55, f"Hub strut distance {min_d_s:.3f} out of range"
    
    print("\nALL 3 BREAKAWAY STRUT CLEARANCES & GAPS VERIFIED SUCCESSFULLY!")

if __name__ == '__main__':
    test_supports()
