import os
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_shaft
import build_part

def test_proposed_calibration():
    print("=" * 75)
    print("TESTING CANDIDATE PIP CALIBRATION FOR EASIER DETACHMENT")
    print("=" * 75)
    
    # Candidate values:
    hub_w = 7.00             # reduced from 7.25 to 7.00 (+0.35mm lateral float per side)
    cam_x_start = 5.75       # shifted from 5.50 to 5.75 (+0.35mm clearance to Left Tower)
    cam_w_x = 1.85           # spans [5.75, 7.60] (clears stick at X >= 8.50mm)
    gap_p = 0.35             # increased from 0.28 to 0.35 (+0.07mm release gap under plunger)
    
    # 1. Check clearances on shaft in assembly coords
    shaft = build_shaft.build_shaft_rocker_mesh(
        hub_w=hub_w,
        cam_w_x=cam_w_x,
        in_assembly_coords=True,
        with_supports=False
    )
    # Note: need to test cam starting at 5.75
    # Let's inspect shaft bounds and features
    print(f"Shaft mesh watertight: {shaft.is_watertight}, volume: {shaft.volume:.2f} mm³")
    
    # Tower bounds
    left_tower_inner_x = 5.40
    right_tower_inner_x = 13.10
    
    x_c = build_shaft.X_TOWER_CENTER # 9.25
    hub_l = x_c - hub_w / 2.0
    hub_r = x_c + hub_w / 2.0
    
    clear_l = hub_l - left_tower_inner_x
    clear_r = right_tower_inner_x - hub_r
    print(f"Hub lateral clearance: Left={clear_l:.3f} mm, Right={clear_r:.3f} mm (was 0.225 mm)")
    assert clear_l >= 0.30 and clear_r >= 0.30
    
    cam_tower_clear = cam_x_start - left_tower_inner_x
    print(f"Cam-to-Left-Tower clearance: {cam_tower_clear:.3f} mm (was 0.100 mm!)")
    assert cam_tower_clear >= 0.30
    
    # Distance to shaft support stick at X >= 8.50
    cam_stick_clear = 8.50 - (cam_x_start + cam_w_x)
    print(f"Cam-to-Shaft-Stick clearance: {cam_stick_clear:.3f} mm (target >= 0.80 mm)")
    assert cam_stick_clear >= 0.80
    
    print("\nGeometric Clearances Test PASSED!")

if __name__ == '__main__':
    test_proposed_calibration()
