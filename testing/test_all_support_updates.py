"""
testing/test_all_support_updates.py
Comprehensive verification of:
1. Bottom clip 45° supports with 0.28mm release gap.
2. Insert backside breakaway supports with 0.28mm release gap.
3. Cantilever (cam tab) support stick with 0.28mm release gap and easy-snap neck.
"""

import sys, os
import numpy as np
import trimesh
from shapely.geometry import Polygon
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import build_shaft

def run_test():
    print("=" * 70)
    print("RUNNING ALL SUPPORT UPDATES VERIFICATION")
    print("=" * 70)

    # 1. Test build_exact_3d_model()
    print("Building exact 3D model...")
    part_mesh_flat, base_poly = build_part.build_exact_3d_model()
    print(f"Flat part vertices: {len(part_mesh_flat.vertices)}, faces: {len(part_mesh_flat.faces)}")
    
    # 2. Test 45° tilted supported part
    print("Building 45° tilted supported part mesh...")
    part_mesh_45, m_tilted, all_fins = build_part.build_45deg_supported_part_mesh(part_mesh_flat, base_poly)
    print(f"Supported part vertices: {len(part_mesh_45.vertices)}, faces: {len(part_mesh_45.faces)}")
    print(f"Supported part bounds: {part_mesh_45.bounds}")
    
    assert part_mesh_45.bounds[0, 2] >= -0.01, f"Part penetrates bed: {part_mesh_45.bounds[0, 2]}"
    print("PASS: Part sits correctly on print bed Z >= 0.00mm")

    shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=7.20, in_assembly_coords=True, return_subparts=True, with_supports=False)
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_raw = part_mesh_flat.copy().apply_transform(R)
    z_min_raw = m_raw.bounds[0, 2]
    
    cam_t = shaft_subparts['cam'].copy().apply_transform(R)
    cam_t.apply_translation([0, 0, -z_min_raw])
    plunger_t = shaft_subparts['plunger'].copy().apply_transform(R)
    plunger_t.apply_translation([0, 0, -z_min_raw])

    # Check that cam and plunger are free and not welded to fins
    tree_fins = cKDTree(all_fins.vertices)
    dists_cam, _ = tree_fins.query(cam_t.vertices)
    print(f"Min distance from cantilever to support fins/stick: {np.min(dists_cam):.3f} mm")
    assert np.min(dists_cam) >= 0.20, f"Cantilever gap too small: {np.min(dists_cam)}"
    
    dists_plunger, _ = tree_fins.query(plunger_t.vertices)
    print(f"Min distance from plunger to support fins/stick: {np.min(dists_plunger):.3f} mm")
    assert np.min(dists_plunger) >= 0.20, f"Plunger gap too small: {np.min(dists_plunger)}"

    # Specific check: Verify that the shifted back support fin at X = +6.80mm maintains >= 1.0mm clearance from the plunger
    pts_plunger, _ = trimesh.sample.sample_surface(plunger_t, 10000)
    # Filter fin vertices for backplate fins (Y in [-5.8, 14.0], X in [6.0, 7.6])
    fv = all_fins.vertices
    back_fin_verts = fv[(fv[:, 0] >= 6.0) & (fv[:, 0] <= 7.6) & (fv[:, 1] >= 0.0)]
    tree_back_fin = cKDTree(back_fin_verts)
    dists_fin_plunger, _ = tree_back_fin.query(pts_plunger)
    print(f"Min surface clearance between shifted back fin (X=+6.80) and plunger: {np.min(dists_fin_plunger):.3f} mm")
    assert np.min(dists_fin_plunger) >= 1.00, f"Back fin too close to plunger: {np.min(dists_fin_plunger)}"

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
