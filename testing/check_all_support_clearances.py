"""
Check current clearances between all supports and their mating part surfaces.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from scipy.spatial import cKDTree

import build_part as bp
from build_shaft import build_shaft_rocker_mesh

def check():
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    part_mesh_flat, base_poly = bp.build_exact_3d_model()
    m_tilted = part_mesh_flat.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    shaft_t = shaft_assembled.copy().apply_transform(R)
    shaft_t.apply_translation([0, 0, -z_min])
    
    # 1. Slit insert backside support
    insert_supp = bp.build_insert_backside_breakaway_supports_mesh()
    # Find distance from insert support to part
    tree_part = cKDTree(m_tilted.vertices)
    # Only vertices on the upper profile of insert_supp (Z > 0.5)
    v_supp = insert_supp.vertices[insert_supp.vertices[:, 2] > 0.5]
    dists, _ = tree_part.query(v_supp)
    print(f"Insert backside support: min distance to part = {np.min(dists):.3f} mm")
    
    # 2. Plunger support:
    # Let's check poly_plunger_tine_yz top edge vs shaft
    tree_shaft = cKDTree(shaft_t.vertices)
    # The plunger points in build_part.py:
    # (12.10, 15.80), (11.30, 15.432), (10.75, 15.594), (7.50, 18.814)
    # These are in Y-Z plane of machine coords!
    # X ranges: [8.484, 9.284], [11.284, 12.084], [9.934, 10.634]
    p_pts_3d = []
    for y, z in [(12.10, 15.80), (11.30, 15.432), (10.75, 15.594), (7.50, 18.814)]:
        for x in [8.884, 10.284, 11.684]:
            p_pts_3d.append([x, y, z])
    dists_plunger, _ = tree_shaft.query(p_pts_3d)
    print(f"Plunger support top points: min distance to shaft = {np.min(dists_plunger):.3f} mm")
    
    # 3. Cam support:
    # Top points: (-3.50, 18.585), (-2.33, 17.700), (-1.20, 19.003)
    # X ranges: [5.65, 6.20], [7.00, 7.55]
    cam_pts_3d = []
    for y, z in [(-3.50, 18.585), (-2.33, 17.700), (-1.20, 19.003)]:
        for x in [5.925, 7.275]:
            cam_pts_3d.append([x, y, z])
    dists_cam, _ = tree_shaft.query(cam_pts_3d)
    print(f"Cam support top points: min distance to shaft = {np.min(dists_cam):.3f} mm")

if __name__ == '__main__':
    check()
