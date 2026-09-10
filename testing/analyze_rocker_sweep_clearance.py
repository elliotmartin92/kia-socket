"""
testing/analyze_rocker_sweep_clearance.py
Analyze the 3D kinematic motion of the shaft rocker to determine the exact dynamic
envelope and clearance above Z = 14.00mm between X = 5.40mm and X = 13.10mm.
"""

import os
import sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE

def analyze_rocker_sweep():
    # Build rocker mesh in assembly coordinates (theta = 0 deg, rest position)
    mesh_rest = build_shaft_rocker_mesh(in_assembly_coords=True)
    
    # Check max Z at rest
    print(f"Rest Mesh Bounds:")
    print(f"  X: [{mesh_rest.bounds[0,0]:.3f}, {mesh_rest.bounds[1,0]:.3f}]")
    print(f"  Y: [{mesh_rest.bounds[0,1]:.3f}, {mesh_rest.bounds[1,1]:.3f}]")
    print(f"  Z: [{mesh_rest.bounds[0,2]:.3f}, {mesh_rest.bounds[1,2]:.3f}]")
    
    # Vertices with Z > 13.50mm
    v_high = mesh_rest.vertices[mesh_rest.vertices[:, 2] > 13.50]
    print(f"\nVertices at rest with Z > 13.50 mm: {len(v_high)}")
    if len(v_high) > 0:
        print(f"  X-range of high vertices: [{v_high[:,0].min():.3f}, {v_high[:,0].max():.3f}]")
        print(f"  Y-range of high vertices: [{v_high[:,1].min():.3f}, {v_high[:,1].max():.3f}]")
        print(f"  Z-range of high vertices: [{v_high[:,2].min():.3f}, {v_high[:,2].max():.3f}]")
        
    # Check rotation up to theta = 15 degrees (actuated position)
    # Plug insertion rotates rocker around axle: Y = 9.279, Z = 12.590
    # Cam is pushed down/back -> plunger swings down/forward
    # Let's check rotation direction
    # In simulate_exact_physical_assembly.py, plug enters from +Z downward, pushing cam ramp
    # Cam ramp is at Y < 9.279. Pushing down rotates negative around X axis (clockwise looking from +X)
    angles = [0, 5, 10, 15, 20]
    print("\n--- ROTATION SWEEP ---")
    for theta_deg in angles:
        theta = np.radians(theta_deg)
        # Rotation around X axis passing through (Y_AXLE, Z_AXLE)
        rot_mat = trimesh.transformations.rotation_matrix(theta, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
        m_rot = mesh_rest.copy()
        m_rot.apply_transform(rot_mat)
        
        v_h = m_rot.vertices[m_rot.vertices[:, 2] > 14.00]
        print(f"Theta = {theta_deg:2d} deg: Max Z = {m_rot.bounds[1, 2]:.3f} mm, verts > 14.00mm: {len(v_h)}")
        if len(v_h) > 0:
            print(f"   X-range > 14.00mm: [{v_h[:,0].min():.2f}, {v_h[:,0].max():.2f}], Y-range: [{v_h[:,1].min():.2f}, {v_h[:,1].max():.2f}]")

if __name__ == '__main__':
    analyze_rocker_sweep()
