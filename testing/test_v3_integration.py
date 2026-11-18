import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import KINEMATIC_VARIANTS, build_shaft_rocker_mesh
from build_part import build_exact_3d_model, build_45deg_supported_part_mesh

def test_v3_integration():
    print("=" * 75)
    print("TESTING INTEGRATION OF TEST 4 (IIII) - V3 BALANCED NOMINAL")
    print("=" * 75)
    
    # Check that ACTIVE_VARIANT is v3_nominal
    from build_shaft import ACTIVE_VARIANT, PLUNGER_Y_CENTER
    print(f"Active Variant in build_shaft: {ACTIVE_VARIANT}")
    print(f"Plunger Y Center: {PLUNGER_Y_CENTER}")
    assert ACTIVE_VARIANT == 'v3_nominal', f"Expected v3_nominal, got {ACTIVE_VARIANT}"
    assert np.isclose(PLUNGER_Y_CENTER, 10.95), f"Expected plunger_y = 10.95, got {PLUNGER_Y_CENTER}"
    
    # 1. Build shaft rocker meshes
    shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    print(f"Shaft Assembled Watertight: {shaft_assembled.is_watertight}, Volume: {shaft_assembled.volume:.2f} mm³")
    assert shaft_assembled.is_watertight
    
    shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=True)
    print(f"Shaft Printable Watertight: {shaft_printable.is_watertight}, Volume: {shaft_printable.volume:.2f} mm³")
    assert shaft_printable.is_watertight
    
    shaft_clean = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
    print(f"Shaft Clean Watertight: {shaft_clean.is_watertight}, Volume: {shaft_clean.volume:.2f} mm³")
    assert shaft_clean.is_watertight
    
    # 2. Build 45 deg supported part with PIP lever
    part_mesh_flat, base_poly = build_exact_3d_model()
    part_mesh_45, m_tilted, all_fins = build_45deg_supported_part_mesh(part_mesh_flat, base_poly, include_pip_shaft=True)
    print(f"Part 45° Watertight: {part_mesh_45.is_watertight}, Bounds: {part_mesh_45.bounds.tolist()}")
    
    # Check PIP lever position in part_mesh_45
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    z_min = m_tilted.bounds[0, 2] # m_tilted already translated to 0
    shaft_pip = shaft_assembled.copy().apply_transform(R)
    shaft_pip.apply_translation([0, 0, -part_mesh_flat.copy().apply_transform(R).bounds[0, 2]])
    
    # 3. Raycast gap verification for Cam Tines in part_mesh_45
    x_cam_tines = [5.65 + 0.275, 7.00 + 0.275]
    y_cams = np.linspace(-3.80, -1.30, 10)
    cam_gaps = []
    for xc in x_cam_tines:
        for yc in y_cams:
            ray_org = np.array([[xc, yc, 0.0]])
            locs, _, _ = all_fins.ray.intersects_location(ray_org, np.array([[0, 0, 1.0]]))
            if len(locs) > 0:
                z_top = locs[:, 2].max()
                ray_up = np.array([[xc, yc, z_top - 0.01]])
                locs_l, _, _ = shaft_pip.ray.intersects_location(ray_up, np.array([[0, 0, 1.0]]))
                if len(locs_l) > 0:
                    gap = locs_l[:, 2].min() - z_top
                    cam_gaps.append(gap)
    
    if len(cam_gaps) > 0:
        print(f"Cam Tines Support Gap: min={min(cam_gaps):.3f} mm, max={max(cam_gaps):.3f} mm, mean={np.mean(cam_gaps):.3f} mm")
        assert min(cam_gaps) >= 0.22 and max(cam_gaps) <= 0.32, f"Cam gap out of range: {cam_gaps}"
    
    # 4. Raycast gap verification for Plunger Tines in part_mesh_45
    x_pl_tines = [8.484 + 0.40, 10.284, 11.284 + 0.40]
    y_pls = np.linspace(8.50, 12.30, 12)
    pl_gaps = []
    for xp in x_pl_tines:
        for yp in y_pls:
            ray_org = np.array([[xp, yp, 0.0]])
            locs, _, _ = all_fins.ray.intersects_location(ray_org, np.array([[0, 0, 1.0]]))
            if len(locs) > 0:
                z_top = locs[:, 2].max()
                ray_up = np.array([[xp, yp, z_top - 0.01]])
                locs_l, _, _ = shaft_pip.ray.intersects_location(ray_up, np.array([[0, 0, 1.0]]))
                if len(locs_l) > 0:
                    gap = locs_l[:, 2].min() - z_top
                    pl_gaps.append(gap)
                    
    if len(pl_gaps) > 0:
        print(f"Plunger Tines Support Gap: min={min(pl_gaps):.3f} mm, max={max(pl_gaps):.3f} mm, mean={np.mean(pl_gaps):.3f} mm")
        assert min(pl_gaps) >= 0.22 and max(pl_gaps) <= 0.32, f"Plunger gap out of range: {pl_gaps}"
        
    print("\nALL V3 INTEGRATION CHECKS PASSED!")

if __name__ == '__main__':
    test_v3_integration()
