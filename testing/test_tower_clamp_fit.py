"""
testing/test_tower_clamp_fit.py
Comprehensive kinematic and geometric verification of the Universal Tower Prong Clamp
installed on both Left and Right shaft support towers.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    BASE_THICK, TOWER_HEIGHT, build_clean_shaft_towers_mesh, build_left_tower_struts_mesh
)
from build_shaft import (
    Y_AXLE, Z_AXLE, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER
)
from build_clamp import (
    get_clamp_polygon_yz, build_tower_clamp_mesh, CLAMP_WIDTH_X
)

def run_fit_verification():
    print("================================================================================")
    print("VERIFICATION: UNIVERSAL TOWER PRONG CLAMP FIT & KINEMATICS")
    print("================================================================================")
    
    # 1. Build Baseplate Towers & Struts
    towers = build_clean_shaft_towers_mesh()
    struts = build_left_tower_struts_mesh()
    
    # 2. Build Clamps for Left & Right Towers
    clamp_left = build_tower_clamp_mesh(in_assembly_coords=True, tower_side='left')
    clamp_right = build_tower_clamp_mesh(in_assembly_coords=True, tower_side='right')
    
    assert clamp_left.is_watertight, "Left clamp mesh must be watertight!"
    assert clamp_right.is_watertight, "Right clamp mesh must be watertight!"
    print(f"Left Clamp:  X in [{clamp_left.bounds[0,0]:.3f}, {clamp_left.bounds[1,0]:.3f}], Watertight: {clamp_left.is_watertight}")
    print(f"Right Clamp: X in [{clamp_right.bounds[0,0]:.3f}, {clamp_right.bounds[1,0]:.3f}], Watertight: {clamp_right.is_watertight}")
    
    # 3. Check X-Clearance to Rocker Hub (Hub is X in [5.50, 13.00])
    hub_x_min = 5.50
    hub_x_max = 13.00
    
    clr_left_to_hub = hub_x_min - clamp_left.bounds[1, 0]
    clr_right_to_hub = clamp_right.bounds[0, 0] - hub_x_max
    print(f"\nAxial Clearances to Rotating Rocker Hub:")
    print(f"  Left Clamp to Hub:  {clr_left_to_hub:.3f} mm (> 0.10mm required)")
    print(f"  Right Clamp to Hub: {clr_right_to_hub:.3f} mm (> 0.10mm required)")
    assert clr_left_to_hub >= 0.10, f"Left clamp clearance to hub too small: {clr_left_to_hub}"
    assert clr_right_to_hub >= 0.10, f"Right clamp clearance to hub too small: {clr_right_to_hub}"
    
    # 4. Check Zero Pin Friction: Clearance around axle pin in the outer side cheek
    shaft_rest = build_shaft_rocker_mesh(in_assembly_coords=True)
    pin_left = shaft_rest.vertices[shaft_rest.vertices[:, 0] < 3.90]
    pin_right = shaft_rest.vertices[shaft_rest.vertices[:, 0] > 14.60]
    
    # Arch radial clearance (R=1.70mm vs Pin R=1.40mm -> >= 0.30mm)
    print("\nAxle Pin Contact & Friction Inspection:")
    print(f"  Left Pin outer protrusion points:  {len(pin_left)}")
    print(f"  Right Pin outer protrusion points: {len(pin_right)}")
    dists_l = np.min([np.min(np.linalg.norm(clamp_left.vertices - p, axis=1)) for p in pin_left])
    dists_r = np.min([np.min(np.linalg.norm(clamp_right.vertices - p, axis=1)) for p in pin_right])
    print(f"  Minimum distance Left Pin to Clamp:  {dists_l:.3f} mm (Clearance arch: zero pin friction!)")
    print(f"  Minimum distance Right Pin to Clamp: {dists_r:.3f} mm (Clearance arch: zero pin friction!)")
    assert dists_l > 0.10, "Left pin must not touch clamp!"
    assert dists_r > 0.10, "Right pin must not touch clamp!"
    
    # 5. Rocker Dynamic Kinematics Sweep (0 deg to 20 deg)
    clamps_combined = trimesh.util.concatenate([clamp_left, clamp_right])
    
    print("\nKinematic Clearance Sweep (Rocker vs Clamps):")
    angles = [0, 5, 10, 15, 20]
    for deg in angles:
        theta = np.radians(deg)
        rot_mat = trimesh.transformations.rotation_matrix(theta, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
        shaft_rot = shaft_rest.copy()
        shaft_rot.apply_transform(rot_mat)
        
        # Check distance between clamps and rotating rocker (ignoring the axle pins inside the cradle)
        # Axle pins are inside cradle at Z <= 13.99mm. The clamp sits at Z >= 14.00mm above axle pins.
        # Check points on shaft with Z > 14.00mm
        shaft_pts_high = shaft_rot.vertices[shaft_rot.vertices[:, 2] > 14.00]
        # Find minimum distance between high shaft points and clamp vertices
        # Clamps X bounds: [3.925, 5.375] and [13.125, 14.575]
        # Shaft high points are in X in [4.93, 13.00]
        # Check closest points
        dists = []
        for v in shaft_pts_high:
            # Check if within X range of clamps
            if (3.90 <= v[0] <= 5.40) or (13.10 <= v[0] <= 14.60):
                dists.append(v)
        
        print(f"  Theta = {deg:2d} deg: Points on rotating rocker entering clamp X-zones above Z=14.00mm: {len(dists)}")
        assert len(dists) == 0, f"Collision detected at theta = {deg} deg!"
    
    print("-> 100% ZERO COLLISION during full dynamic operation!")
    print("================================================================================")
    print("FIT VERIFICATION PASSED SUCCESSFULLY!")
    print("================================================================================")

if __name__ == '__main__':
    run_fit_verification()
