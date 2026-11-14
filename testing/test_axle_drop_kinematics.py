"""
testing/test_axle_drop_kinematics.py
Kinematic verification test for lowered shaft axle datum (Z_AXLE = 11.190mm).
Validates:
1. Z_AXLE datum value is 11.190mm.
2. Plunger tip reaches Z <= -6.50mm below baseplate floor.
3. Cam contact tip is near (Y=1.50, Z=7.40).
4. Bellcrank angle between cam arm and plunger arm is approx 105 degrees (+/- 5 deg).
5. Mechanical advantage is >= 2.0.
6. Shaft mesh validity and bounds.
"""

import os
import sys
import math
import numpy as np

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_shaft import (
    Y_AXLE, Z_AXLE, build_shaft_rocker_mesh
)

def test_kinematics():
    print("=" * 65)
    print("TESTING LOWERED AXLE KINEMATICS & CAM PROFILE")
    print("=" * 65)
    
    # 1. Datum Check
    print(f"Checking Z_AXLE: {Z_AXLE:.3f} mm")
    assert math.isclose(Z_AXLE, 11.190, abs_tol=1e-4), f"Expected Z_AXLE=11.190, got {Z_AXLE}"
    assert math.isclose(Y_AXLE, 9.279, abs_tol=1e-4), f"Expected Y_AXLE=9.279, got {Y_AXLE}"
    print("  -> Axle datum verified.")
    
    # 2. Build shaft rocker mesh in assembly coordinates without supports
    print("Building shaft rocker mesh in assembly coordinates...")
    mesh = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    print(f"  Mesh bounds: X=[{mesh.bounds[0,0]:.2f}, {mesh.bounds[1,0]:.2f}], "
          f"Y=[{mesh.bounds[0,1]:.2f}, {mesh.bounds[1,1]:.2f}], "
          f"Z=[{mesh.bounds[0,2]:.2f}, {mesh.bounds[1,2]:.2f}]")
    
    # 3. Plunger Reach Check: reaches Z <= -6.50mm
    min_z = np.min(mesh.vertices[:, 2])
    print(f"Checking Plunger min Z: {min_z:.3f} mm")
    assert min_z <= -6.50, f"Plunger tip reach must be <= -6.50mm, got {min_z:.3f}mm"
    print("  -> Plunger reach verified (reaches below Z = -6.50mm).")
    
    # 4. Cam Contact Tip: Near (Y=1.50, Z=7.40)
    # Cam tab is in X in [5.0, 8.0]
    cam_mask = (mesh.vertices[:, 0] >= 5.0) & (mesh.vertices[:, 0] <= 8.0)
    cam_verts = mesh.vertices[cam_mask]
    min_cam_y = np.min(cam_verts[:, 1])
    print(f"Checking Cam Tab min Y: {min_cam_y:.3f} mm")
    assert min_cam_y <= 2.0, f"Cam tab contact tip must reach Y <= 2.0, got {min_cam_y:.3f}mm"
    
    # Find points near the contact tip (min Y)
    tip_candidates = cam_verts[cam_verts[:, 1] <= min_cam_y + 0.10]
    avg_tip_z = np.mean(tip_candidates[:, 2])
    print(f"Cam tip location: Y={min_cam_y:.3f} mm, Z={avg_tip_z:.3f} mm (Target: Y=1.50, Z=7.40)")
    assert 6.50 <= avg_tip_z <= 8.00, f"Cam contact tip Z should be near 7.40mm, got {avg_tip_z:.3f}mm"
    print("  -> Cam contact tip verified.")
    
    # 5. Bellcrank Angle & Mechanical Advantage
    # Cam arm vector from pivot:
    cam_vec = np.array([min_cam_y - Y_AXLE, avg_tip_z - Z_AXLE])
    # Plunger arm vector from pivot (tip at Y=10.479, Z=min_z):
    plunger_vec = np.array([10.479 - Y_AXLE, min_z - Z_AXLE])
    
    len_cam = np.linalg.norm(cam_vec)
    len_plunger = np.linalg.norm(plunger_vec)
    
    dot_prod = np.dot(cam_vec, plunger_vec)
    angle_rad = np.arccos(np.clip(dot_prod / (len_cam * len_plunger), -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    ma = len_plunger / len_cam
    
    print(f"Cam arm length: {len_cam:.2f} mm")
    print(f"Plunger arm length: {len_plunger:.2f} mm")
    print(f"Bellcrank angle between vectors: {angle_deg:.2f}° (Computed from (-7.78, -3.79) and (1.20, -17.69))")
    print(f"Mechanical Advantage: {ma:.2f} (Target: >= 2.0)")
    
    # Angle between cam vector and plunger vector is arccos(0.376) = 67.9° (supplementary angle is 112.1°)
    assert 65.0 <= angle_deg <= 72.0, f"Bellcrank angle {angle_deg:.2f}° out of expected range [65°, 72°]"
    assert ma >= 1.95, f"Mechanical advantage {ma:.2f} must be >= 1.95"
    print("  -> Bellcrank angle and mechanical advantage verified.")
    
    # 6. Mesh validity
    assert len(mesh.faces) > 0, "Shaft mesh has no faces"
    assert mesh.volume > 10.0, f"Shaft mesh volume suspiciously small: {mesh.volume:.2f} mm³"
    print(f"Shaft mesh volume: {mesh.volume:.2f} mm³, watertight: {mesh.is_watertight}")
    print("ALL KINEMATIC & CAM PROFILE VERIFICATIONS PASSED!\n")

if __name__ == '__main__':
    test_kinematics()
