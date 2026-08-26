"""
testing/analyze_brass_clearance_and_cam.py
Precise kinematic and geometric analysis of the horizontal gap (2.7mm) from the top of the left tower
to the brass pinching mechanism, and calculating exact clearance boundaries for the lever.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, TOWER_HEIGHT, BASE_THICK,
    create_all_brackets_poly
)

def run_analysis():
    print("================================================================================")
    print("ANALYSIS: 2.7mm HORIZONTAL GAP & LEVER INTERFERENCE REMEDIATION")
    print("================================================================================")
    
    # Left tower top coordinates
    z_tower_top = BASE_THICK + TOWER_HEIGHT  # 14.09 mm
    y_lt_top_front = 6.550                   # Front face of left tower at Z = 14.09 mm
    y_lt_top_rear = 12.180                   # Rear face of left tower at Z = 14.09 mm
    x_lt_inner = X_LEFT_TOWER_INNER          # 5.40 mm
    x_lt_outer = X_LEFT_TOWER_OUTER          # 3.90 mm
    
    # 2.7 mm horizontal gap from left tower top front to brass part rear edge:
    gap_h = 2.700
    y_brass_rear = y_lt_top_front - gap_h    # 6.550 - 2.700 = 3.850 mm
    
    print(f"Left Tower Top Front Edge: Y = {y_lt_top_front:.3f} mm, Z = {z_tower_top:.2f} mm")
    print(f"Horizontal Gap to Brass:     {gap_h:.3f} mm")
    print(f"-> Brass Part Rear Flange at Top (Z >= {z_tower_top:.2f} mm): Y = {y_brass_rear:.3f} mm")
    
    # Plug blade coordinates:
    # Standard NEMA plug blade (Hot):
    # Width W_y = 6.35 mm (0.250 in), Thickness W_x = 1.52 mm (0.060 in)
    # Center X = 6.28 mm
    # Nominal center Y = 2.50 mm (spans Y in [2.50 - 3.175, 2.50 + 3.175] = [-0.675, +5.675] mm)
    # Front edge of blade: Y = -0.675 mm, Rear edge of blade: Y = +5.675 mm
    blade_x_c = 6.28
    blade_w_x = 1.52
    blade_y_min = 2.50 - 6.35/2.0  # -0.675 mm
    blade_y_max = 2.50 + 6.35/2.0  # +5.675 mm
    
    print(f"\nPlug Blade (Hot):")
    print(f"  X in [{blade_x_c - blade_w_x/2:.2f}, {blade_x_c + blade_w_x/2:.2f}] mm (centered at X = {blade_x_c:.2f} mm)")
    print(f"  Y in [{blade_y_min:.3f}, {blade_y_max:.3f}] mm (centered at Y = 2.50 mm, width = 6.35 mm)")
    
    # Lever Cam current geometry:
    # Centered at X = 7.05 mm, width 2.70 mm -> X in [5.70, 8.40] mm
    # Cam reaches from shaft axle (Y = 9.279 mm, Z = 12.590 mm) to Y = 2.834 mm, Z = 10.422 mm
    # Notice: The cam reaches to Y = 2.834 mm, which is INSIDE the blade (Y in [-0.675, 5.675] mm).
    # BUT at Y = 3.850 mm (the brass rear flange), the cam is at Z in [10.8, 13.5] mm!
    # And the brass mechanism is taller than the tower (Z >= 14.09 mm)!
    # Therefore, the brass mechanism extends continuously from Y = -0.675 to Y = 3.850 mm at Z up to 16+ mm!
    
    print(f"\nLever Cam Interference Analysis:")
    print(f"  Current Cam X-span: [{CAM_X_CENTER - CAM_WIDTH_X/2:.2f}, {CAM_X_CENTER + CAM_WIDTH_X/2:.2f}] mm")
    print(f"  Current Cam Y-span: [2.83, {Y_AXLE:.2f}] mm")
    print(f"  Brass Mechanism Top Rear Face: Y = {y_brass_rear:.3f} mm, rising to Z > {z_tower_top:.2f} mm")
    print(f"  -> DIRECT OVERLAP: From Y = {2.83:.2f} mm to Y = {y_brass_rear:.2f} mm ({y_brass_rear - 2.83:.2f} mm of overlap in Y!)")
    
    # Let's analyze how the brass mechanism pinches:
    # The brass mechanism has two spring leaves:
    # 1. Left leaf (X < 6.28 mm): presses against the left face of the blade (X = 6.28 - 0.76 = 5.52 mm).
    #    At the top, it widens/flares to the left (towards X ~ 3.5 - 4.5 mm) and rear (+Y).
    # 2. Right leaf (X > 6.28 mm): presses against the right face of the blade (X = 6.28 + 0.76 = 7.04 mm).
    #    At the top, it widens/flares to the right (towards X ~ 8.0 - 9.5 mm) and rear (+Y).
    # 3. Between the two leaves is the SLIT where the blade enters (X = 6.28 mm).
    
    print("\n--- HOW THE OEM ROCKER / LEVER INTERACTS WITH THE BRASS MECHANISM ---")
    print("In the OEM design:")
    print("  - The plug blade tip enters downward (-Z) directly through the top widened funnel of the brass leaves.")
    print("  - The rocker lever's cam must contact the REAR EDGE or TOP of the blade (or enter the slit between the brass leaves).")
    print("  - If the cam arm is placed at the rear of the blade, or if it is narrow enough to pass between the flared brass leaves, or if the cam contacts the top/rear of the blade at Y > blade_center...")
    print("  - Let's check the options to eliminate all interference!")

if __name__ == '__main__':
    run_analysis()
