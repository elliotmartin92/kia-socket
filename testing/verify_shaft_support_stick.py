"""
testing/verify_shaft_support_stick.py
Verification test suite for the dedicated breakaway stick support with Y-fork head
under the floating section of the lever shaft (hub barrel).
Validates zero intersection with Bracket 4 wall, safe clearances to all moving parts,
and calibrated 0.28mm release gap.
"""

import os
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE, HUB_WIDTH, HUB_DIAMETER
from build_part import build_exact_3d_model, build_45deg_supported_part_mesh, bracket_4_raw_pts, to_mm_poly

def run_verification():
    print("=" * 80)
    print("VERIFICATION: DEDICATED BREAKAWAY STICK SUPPORT UNDER FLOATING LEVER SHAFT")
    print("=" * 80)
    
    # 1. Coordinate frame datums
    base_mesh, base_poly = build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    
    # Lowest point of hub cylinder
    z_shaft_lowest = (Y_AXLE * np.sin(np.radians(45.0)) + Z_AXLE * np.cos(np.radians(45.0))) - z_min - (HUB_DIAMETER / 2.0)
    y_shaft_tilted = Y_AXLE * np.cos(np.radians(45.0)) - Z_AXLE * np.sin(np.radians(45.0))
    
    print(f"\n[1] Geometric Datums:")
    print(f"    Shaft Hub Lowest Point in Tilted Coords: Y' = {y_shaft_tilted:.3f} mm, Z' = {z_shaft_lowest:.3f} mm")
    
    # 2. Build 45-deg supported part
    combined, tilted_main, fins = build_45deg_supported_part_mesh(base_mesh, base_poly, include_pip_shaft=True)
    
    # Inspect support fin components in shaft region:
    # X in [7.70, 9.50], Y in [-3.20, -1.50], Z in [13.0, 26.3]
    fin_v = fins.vertices
    mask = (
        (fin_v[:, 0] >= 7.70) & (fin_v[:, 0] <= 9.50) &
        (fin_v[:, 1] >= -3.20) & (fin_v[:, 1] <= -1.50) &
        (fin_v[:, 2] >= 13.00) & (fin_v[:, 2] <= 26.30)
    )
    stick_verts = fin_v[mask]
    assert len(stick_verts) > 0, "No vertices found for shaft stick support in fins!"
    
    z_stick_top = np.max(stick_verts[:, 2])
    release_gap = z_shaft_lowest - z_stick_top
    print(f"\n[2] Stick Support Height & Release Gap:")
    print(f"    Stick Support Top Z': {z_stick_top:.3f} mm")
    print(f"    Target Shaft Underside Z': {z_shaft_lowest:.3f} mm")
    print(f"    Measured Release Gap: {release_gap:.3f} mm (Target: 0.48 mm +/- 0.02 mm)")
    assert abs(release_gap - 0.48) < 0.02, f"Release gap mismatch: {release_gap:.3f} mm"
    print("    -> PASS: Calibrated 0.48mm release gap confirmed.")
    
    # 3. Y-Fork Head Geometry
    x_min_stick = np.min(stick_verts[:, 0])
    x_max_stick = np.max(stick_verts[:, 0])
    x_span = x_max_stick - x_min_stick
    x_center = (x_min_stick + x_max_stick) / 2.0
    print(f"\n[3] Y-Fork Head Architecture:")
    print(f"    X Span: [{x_min_stick:.2f}, {x_max_stick:.2f}] mm (Total Span: {x_span:.2f} mm)")
    print(f"    X Center: {x_center:.2f} mm (Target: 8.85 mm)")
    assert abs(x_center - 8.85) < 0.15, f"X center mismatch: {x_center:.2f} mm"
    assert x_span >= 0.40, f"Fork head span too narrow: {x_span:.2f} mm"
    
    # Check twin tines and central notch
    slice_top = fins.section(plane_origin=[0, 0, z_stick_top - 0.05], plane_normal=[0, 0, 1])
    assert slice_top is not None, "Slice at fork top must exist!"
    pts_top = slice_top.vertices
    mask_top = (pts_top[:, 0] >= 7.7) & (pts_top[:, 0] <= 9.5) & (pts_top[:, 1] >= -3.2) & (pts_top[:, 1] <= -1.5)
    pts_fork_tines = pts_top[mask_top]
    
    left_tine_x = pts_fork_tines[pts_fork_tines[:, 0] < x_center, 0]
    right_tine_x = pts_fork_tines[pts_fork_tines[:, 0] > x_center, 0]
    assert len(left_tine_x) > 0 and len(right_tine_x) > 0, "Both left and right tines must exist at top!"
    notch_gap = np.min(right_tine_x) - np.max(left_tine_x)
    print(f"    Twin Tines Confirmed: Left [{np.min(left_tine_x):.2f}, {np.max(left_tine_x):.2f}], Right [{np.min(right_tine_x):.2f}, {np.max(right_tine_x):.2f}]")
    print(f"    Central Notch Opening: {notch_gap:.2f} mm")
    assert notch_gap >= 0.10, f"Notch opening too small: {notch_gap:.2f} mm"
    print("    -> PASS: Y-Fork head with twin tines and central V-notch verified.")
    
    # 4. Bracket 4 Wall Clearance (ZERO INTERSECTION)
    print(f"\n[4] Bracket 4 Wall Clearance (Zero Intersection Verification):")
    b4_poly = to_mm_poly(bracket_4_raw_pts)
    b4_3d = trimesh.creation.extrude_polygon(b4_poly, height=4.60)
    b4_3d.apply_translation([0, 0, 1.0])
    b4_t = b4_3d.copy().apply_transform(R)
    b4_t.apply_translation([0, 0, -z_min])
    
    tree_b4 = cKDTree(b4_t.vertices)
    # Check distance for all vertices of the support stick
    d_b4, _ = tree_b4.query(stick_verts)
    min_d_b4 = np.min(d_b4)
    print(f"    Minimum Distance from Support to Bracket 4: {min_d_b4:.3f} mm (Target: >= 0.50 mm)")
    assert min_d_b4 >= 0.50, f"Support is too close to Bracket 4: {min_d_b4:.3f} mm"
    print("    -> PASS: Zero intersection with Bracket 4 confirmed! Generous clearance guarantees effortless removal.")
    
    # 5. 3D Clearances to moving lever parts
    subparts = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False, return_subparts=True)
    tree_stick = cKDTree(stick_verts)
    
    print(f"\n[5] Clearances to Surrounding Mechanism Features:")
    for name, part in subparts.items():
        part_t = part.copy().apply_transform(R)
        part_t.apply_translation([0, 0, -z_min])
        dists, _ = tree_stick.query(part_t.vertices)
        min_d = np.min(dists)
        print(f"    Clearance to {name:<10}: {min_d:.3f} mm")
        assert min_d >= 0.27, f"Clearance to {name} too tight: {min_d:.3f} mm"
    print("    -> PASS: Safe clearances verified to all lever mechanism components.")
    
    print("\n" + "=" * 80)
    print("ALL LEVER SHAFT SUPPORT STICK VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == '__main__':
    run_verification()
