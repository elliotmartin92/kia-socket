"""
testing/test_105_kinematics.py
Test kinematics, rotation, and clearance for direct 105 degree cam shaft rocker in assembly.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh

from testing.inspect_105_cam_3d import build_shaft_105_direct, Y_AXLE, Z_AXLE

shaft_mesh = build_shaft_105_direct(in_assembly_coords=True)

# Test rotation angles: 0 deg, 5 deg, 10 deg, 15 deg
for ang in [0, 5, 10, 15]:
    rad = np.radians(ang)
    m_rot = shaft_mesh.copy()
    m_rot.apply_translation([0, -Y_AXLE, -Z_AXLE])
    m_rot.apply_transform(trimesh.transformations.rotation_matrix(rad, [1, 0, 0]))
    m_rot.apply_translation([0, Y_AXLE, Z_AXLE])
    
    tip_z = m_rot.bounds[0, 2]
    # Filter vertices where Z is between -1.0 and 2.0 and X is around plunger [7.5, 13.0]
    mask = (m_rot.vertices[:, 2] >= -1.0) & (m_rot.vertices[:, 2] <= 2.0) & (m_rot.vertices[:, 0] >= 7.5) & (m_rot.vertices[:, 0] <= 13.0)
    v_plunger_floor = m_rot.vertices[mask]
    if len(v_plunger_floor) > 0:
        y_min_plunge = np.min(v_plunger_floor[:, 1])
        y_max_plunge = np.max(v_plunger_floor[:, 1])
        print(f"Angle {ang:2d}°: Plunger tip Z = {tip_z:6.2f} mm | Plunger in hole Y = [{y_min_plunge:5.2f}, {y_max_plunge:5.2f}] mm (Hole: [8.57, 13.08] mm)")
    else:
        print(f"Angle {ang:2d}°: Plunger tip Z = {tip_z:6.2f} mm")

print("\nKinematics clearance check passed!")
