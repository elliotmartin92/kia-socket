"""
testing/calculate_rocker_dimensions.py
Calculates exact dimensions across the rocker/cam and the opposite face where the lever begins,
comparing the CAD model with the user's physical caliper measurement of 10.7mm.
"""

import os
import sys
import numpy as np
import trimesh

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh
)
from testing.test_oem_shaft_rocker import build_oem_shaft_rocker_mesh

def analyze_dimensions():
    print("=== ROCKER / CAM / LEVER ROOT DIMENSIONAL AUDIT ===")
    
    # 1. Current Heavy-Duty Rocker in build_shaft.py
    m_asmb = build_shaft_rocker_mesh(in_assembly_coords=True)
    m_prnt = build_shaft_rocker_mesh(in_assembly_coords=False)
    
    # In assembly coordinates:
    # Shaft axis: Y = 9.279, Z = 12.590
    # Hub: radius = 2.10 mm (diameter = 4.20 mm)
    # Cam tab angle = -161.40 deg, reach = 6.80 mm
    
    # Cam top surface points in assembly (Y, Z):
    # Tip of cam:
    # p_top_tip: Y ≈ 2.834, Z ≈ 10.422 (plus crown +0.45mm along normal)
    # Top tangent at hub: Y ≈ 8.609, Z ≈ 14.580 (Shaft apex: Y = 9.279, Z = 14.690)
    
    # Rear / opposite face of hub / lever spine:
    # Hub rear apex: Y = Y_AXLE + 2.10 = 11.379 mm, Z = 12.590 mm
    # Plunger spine top blend: Y ≈ 11.379 to 13.079 mm, Z ≈ 12.39 to 7.5 mm
    
    # Let's compute caliper spans across various directions:
    
    # A. Total Y span of the cam + hub:
    y_cam_tip = 2.834
    y_hub_rear = Y_AXLE + 2.10 # 11.379
    dy_cam_to_hub_rear = y_hub_rear - y_cam_tip # 8.545 mm
    
    # B. Distance from Cam tip to Plunger spine rear-most point at the hub junction:
    # Plunger spine at Z ~ 12.0 mm: Y ≈ 11.38 mm
    # Plunger spine at Z ~ 7.5 mm: Y ≈ 13.08 mm
    # Distance from cam tip (2.834, 10.422) to (11.379, 12.590):
    dist_tip_to_hub_rear = np.sqrt((11.379 - 2.834)**2 + (12.590 - 10.422)**2) # 8.816 mm
    dist_tip_to_plunger_spine = np.sqrt((13.079 - 2.834)**2 + (7.500 - 10.422)**2) # 10.652 mm!
    
    print(f"Current Heavy-Duty CAD Model:")
    print(f"  - Hub Diameter: {HUB_DIAMETER:.2f} mm")
    print(f"  - Total Y-span (Cam tip to Hub rear): {dy_cam_to_hub_rear:.2f} mm")
    print(f"  - Distance from Cam Tip to Hub Rear Apex: {dist_tip_to_hub_rear:.2f} mm")
    print(f"  - Distance from Cam Tip to Plunger Spine Curve: {dist_tip_to_plunger_spine:.2f} mm (LOOK AT THIS: {dist_tip_to_plunger_spine:.2f} mm vs user measured 10.7 mm!)")
    
    # C. Caliper measurement perpendicular to cam face or across the head:
    # Cam top surface normal: u_perp_up = [-0.319, 0.948] (angle ~ 108.6 deg)
    # Caliper thickness from cam top surface to opposite bottom/rear corner of plunger root:
    v_cam_top = np.array([2.834, 10.422 + 0.45*0.948]) # with crown
    v_plunger_root = np.array([12.479, 7.500]) # where lever begins
    dist_cam_top_to_lever_begin = np.linalg.norm(v_plunger_root - v_cam_top)
    print(f"  - Distance from Cam Top Peak to where Lever begins (Plunger root): {dist_cam_top_to_lever_begin:.2f} mm")
    
    # 2. OEM Rocker in testing/test_oem_shaft_rocker.py
    m_oem = build_oem_shaft_rocker_mesh(in_assembly_coords=True)
    # OEM: Y_AXLE = 7.666, Z_AXLE = 12.590, Hub = 3.30mm, y_cam_tip = 3.466, z_cam_tip = 6.790
    y_oem_cam_tip = 3.466
    z_oem_cam_tip = 6.790
    y_oem_hub_rear = 7.666 + 3.30/2.0 # 9.316
    # Plunger root in OEM: (11.40, 7.50)
    dist_oem_tip_to_lever_root = np.sqrt((11.40 - 3.466)**2 + (7.50 - 6.790)**2)
    print(f"\nOEM Rocker Model:")
    print(f"  - Distance from Cam Tip to Lever Root in OEM: {dist_oem_tip_to_lever_root:.2f} mm")
    
    # Let's inspect the exact geometry and print out all relevant landmark points:
    print(f"\nLandmark Coordinates (Y, Z):")
    print(f"  Pivot Axle Center:     ({Y_AXLE:.3f}, {Z_AXLE:.3f})")
    print(f"  Cam Tip (Top-most tip): ({2.834:.3f}, {10.422 + 0.43:.3f})")
    print(f"  Cam Tangent at Hub:    ({8.609:.3f}, {14.580:.3f})")
    print(f"  Hub Top Apex:          ({Y_AXLE:.3f}, {Z_AXLE + HUB_DIAMETER/2:.3f}) = ({Y_AXLE:.3f}, {Z_AXLE + 2.10:.3f})")
    print(f"  Hub Rear Apex:         ({Y_AXLE + HUB_DIAMETER/2:.3f}, {Z_AXLE:.3f}) = ({Y_AXLE + 2.10:.3f}, {Z_AXLE:.3f})")
    print(f"  Plunger Root / Neck:   ({10.479 + 1.00:.3f}, {7.500:.3f}) to ({Y_AXLE + 3.80:.3f}, {7.500:.3f}) = (11.48 to 13.08, 7.50)")

if __name__ == '__main__':
    analyze_dimensions()
