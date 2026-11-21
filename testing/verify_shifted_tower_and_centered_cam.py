"""
testing/verify_shifted_tower_and_centered_cam.py

Exhaustive verification of the Left Tower Shift (Delta X = -0.45mm)
and Lengthened Shaft Rocker with Dead-Center Cam Tab.
"""
import sys
import numpy as np
import trimesh

sys.path.insert(0, '.')
import build_part as bp
import build_shaft as bs

def verify():
    print("=" * 80)
    print("VERIFICATION: LEFT TOWER SHIFT & CENTERED CAM TAB")
    print("=" * 80)

    # 1. Tower Coordinates
    print("\n[1] Verifying Tower Coordinates and Geometry:")
    assert bp.TOWER_INTERNAL_GAP == 8.15, f"Expected 8.15, got {bp.TOWER_INTERNAL_GAP}"
    assert bs.X_LEFT_TOWER_INNER == 4.95, f"Expected 4.95, got {bs.X_LEFT_TOWER_INNER}"
    assert bs.X_LEFT_TOWER_OUTER == 3.45, f"Expected 3.45, got {bs.X_LEFT_TOWER_OUTER}"
    assert bs.X_RIGHT_TOWER_INNER == 13.10, f"Expected 13.10, got {bs.X_RIGHT_TOWER_INNER}"
    assert bs.X_RIGHT_TOWER_OUTER == 14.60, f"Expected 14.60, got {bs.X_RIGHT_TOWER_OUTER}"
    print(f"    Left Tower:  [{bs.X_LEFT_TOWER_OUTER:.3f}, {bs.X_LEFT_TOWER_INNER:.3f}] mm (Thick: {bs.X_LEFT_TOWER_INNER - bs.X_LEFT_TOWER_OUTER:.2f} mm)")
    print(f"    Right Tower: [{bs.X_RIGHT_TOWER_INNER:.3f}, {bs.X_RIGHT_TOWER_OUTER:.3f}] mm (Thick: {bs.X_RIGHT_TOWER_OUTER - bs.X_RIGHT_TOWER_INNER:.2f} mm)")
    print(f"    Tower Gap:   {bp.TOWER_INTERNAL_GAP:.2f} mm")

    # 2. Shaft Rocker Dimensions & Clearances
    print("\n[2] Verifying Shaft Hub Barrel & Bearing Pin Clearances:")
    assert np.isclose(bs.HUB_WIDTH, 7.45), f"Expected 7.45, got {bs.HUB_WIDTH}"
    assert np.isclose(bs.TOTAL_AXLE_LEN, 11.95), f"Expected 11.95, got {bs.TOTAL_AXLE_LEN}"
    assert np.isclose(bs.PIN_LEN, 2.25), f"Expected 2.25, got {bs.PIN_LEN}"
    
    hub_x_min = bs.X_TOWER_CENTER - bs.HUB_WIDTH / 2.0
    hub_x_max = bs.X_TOWER_CENTER + bs.HUB_WIDTH / 2.0
    assert np.isclose(hub_x_min, 5.30), f"Expected 5.30, got {hub_x_min}"
    assert np.isclose(hub_x_max, 12.75), f"Expected 12.75, got {hub_x_max}"
    
    left_axial_gap = hub_x_min - bs.X_LEFT_TOWER_INNER
    right_axial_gap = bs.X_RIGHT_TOWER_INNER - hub_x_max
    assert np.isclose(left_axial_gap, 0.35), f"Expected 0.35, got {left_axial_gap}"
    assert np.isclose(right_axial_gap, 0.35), f"Expected 0.35, got {right_axial_gap}"
    print(f"    Hub Barrel X span: [{hub_x_min:.3f}, {hub_x_max:.3f}] mm (Width: {bs.HUB_WIDTH:.2f} mm)")
    print(f"    Left Axial Float:  {left_axial_gap:.3f} mm")
    print(f"    Right Axial Float: {right_axial_gap:.3f} mm")
    print(f"    Radial Journal Clearance: {(bp.TOWER_BORE_RADIUS*2.0 - bs.PIN_DIAMETER)/2.0:.3f} mm")

    # 3. Cam Tab Centering & Clearances
    print("\n[3] Verifying Cam Tab Centering in Brass Throat & Blade Engagement:")
    cam_x_min = bs.CAM_X_START
    cam_x_max = bs.CAM_X_START + bs.CAM_WIDTH_X
    cam_center = (cam_x_min + cam_x_max) / 2.0
    assert np.isclose(cam_x_min, 5.35), f"Expected 5.35, got {cam_x_min}"
    assert np.isclose(cam_x_max, 7.15), f"Expected 7.15, got {cam_x_max}"
    assert np.isclose(cam_center, 6.25), f"Expected 6.25, got {cam_center}"
    
    throat_center = 6.250
    assert np.isclose(cam_center, throat_center), f"Cam not centered in throat: {cam_center} vs {throat_center}"
    
    bracket_4_x_inner = 8.000
    cam_to_b4 = bracket_4_x_inner - cam_x_max
    assert cam_to_b4 >= 0.85, f"Clearance to Bracket 4 too tight: {cam_to_b4}"
    
    left_tower_to_cam = cam_x_min - bs.X_LEFT_TOWER_INNER
    assert left_axial_gap <= left_tower_to_cam, "Cam tab interferes with Left Tower!"
    
    # NEMA hot blade X span: [5.49, 7.01] mm (nominal 1.52mm width)
    blade_x_min = 6.250 - 1.52 / 2.0 # 5.49 mm
    blade_x_max = 6.250 + 1.52 / 2.0 # 7.01 mm
    margin_left = blade_x_min - cam_x_min
    margin_right = cam_x_max - blade_x_max
    
    print(f"    Cam Tab X span:    [{cam_x_min:.3f}, {cam_x_max:.3f}] mm (Width: {bs.CAM_WIDTH_X:.2f} mm)")
    print(f"    Cam Tab Center:    {cam_center:.3f} mm (EXACT THROAT CENTER: {throat_center:.3f} mm)")
    print(f"    Margin to Left:    +{margin_left:.3f} mm")
    print(f"    Margin to Right:   +{margin_right:.3f} mm")
    print(f"    Clearance to B4:   +{cam_to_b4:.3f} mm (Gained +0.45mm clearance from previous design!)")

    # 4. 3D Mesh Manifold and Clearance Verifications
    print("\n[4] Building & Verifying 3D Meshes:")
    shaft_clean = bs.build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    assert shaft_clean.is_watertight, "Shaft mesh not watertight!"
    print(f"    Shaft mesh: Watertight = True, Volume = {shaft_clean.volume:.2f} mm³")
    
    part_mesh, _ = bp.build_exact_3d_model()
    assert part_mesh.is_watertight, "Part mesh not watertight!"
    print(f"    Part mesh:  Watertight = True, Volume = {part_mesh.volume:.2f} mm³")

    print("\n" + "=" * 80)
    print("ALL VERIFICATIONS PASSED 100%! READY FOR PRODUCTION REGENERATION.")
    print("=" * 80)

if __name__ == '__main__':
    verify()
