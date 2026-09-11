"""
testing/analyze_50_percent_travel.py
Calculates the kinematics of 50% through-hole plunger travel:
- Plunger delta Y and delta Z
- Switch contact and trigger point
- Tower hub axial clearance and friction reduction tweaks
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, PIN_LEN,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN,
    X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER
)
from build_part import BASE_THICK, TOWER_HEIGHT

def run():
    print("================================================================================")
    print("ANALYSIS: 50% THROUGH-HOLE PLUNGER TRAVEL & SWITCH TRIGGER VERIFICATION")
    print("================================================================================")
    
    # 1. Through-Hole Bounds in Y:
    # HOLE_Y_MIN = 8.570 mm, HOLE_Y_MAX = 13.082 mm (Span = 4.512 mm)
    hole_y_min = HOLE_Y_CENTER - HOLE_Y_LEN/2.0
    hole_y_max = HOLE_Y_CENTER + HOLE_Y_LEN/2.0
    
    # Plunger resting position at Z = 0:
    # At theta = 0 deg, Plunger Y at floor Z=0 is Y = 10.07 mm to 11.48 mm (Center ~ 10.48 mm).
    # Plunger tip at Z = -6.50 mm is at Y = 10.48 mm.
    
    print(f"Through-Hole Y-Span: [{hole_y_min:.2f}, {hole_y_max:.2f}] mm (Total Length = {HOLE_Y_LEN:.2f} mm)")
    print(f"Plunger Rest Position: Y = 10.48 mm")
    
    # Tactile Switch Specs:
    # Switch stem rest contact: Y ~ 12.00 - 12.40 mm
    # Actuation stroke: 0.35 mm (snap dome click)
    
    print("\n--- ROTATION VS PLUNGER DISPLACEMENT & THROUGH-HOLE TRAVEL ---")
    print("theta(deg) | Plunger Tip (Y, Z) | Delta Y from Rest (mm) | Delta Z (mm) | % of Hole Travel | Switch Status")
    
    dy_p = 10.479 - Y_AXLE
    dz_p = -6.50 - Z_AXLE
    
    for theta in [0, 2, 4, 5, 6, 7.2, 8, 10]:
        rad = np.radians(theta)
        c, s = np.cos(rad), np.sin(rad)
        
        y_tip = Y_AXLE + c * dy_p - s * dz_p
        z_tip = Z_AXLE + s * dy_p + c * dz_p
        
        delta_y = y_tip - 10.479
        delta_z = z_tip - (-6.50)
        
        # Percentage of forward travel toward rear wall:
        # Distance from rest (10.48) to rear wall (13.08) = 2.60 mm
        pct_travel = (delta_y / 2.60) * 100.0
        
        if delta_y >= 1.60:
            switch_status = "FULLY ACTUATED (CLICK!)"
        elif delta_y >= 0.80:
            switch_status = "Making contact / Pre-travel"
        else:
            switch_status = "Resting / Idle"
            
        print(f"{theta:10.1f}° | ({y_tip:5.2f}, {z_tip:6.2f}) | {delta_y:22.2f} mm | {delta_z:12.2f} mm | {pct_travel:15.1f}% | {switch_status}")
        
    print("\n--- AXLE & HUB CLEARANCES (FRICTION ANALYSIS) ---")
    tower_gap = X_RIGHT_TOWER_INNER - X_LEFT_TOWER_INNER # 13.10 - 5.40 = 7.70 mm
    hub_w = HUB_WIDTH # 7.50 mm
    axial_gap = (tower_gap - hub_w) / 2.0 # 0.10 mm per side
    
    cradle_dia = 3.00 # mm
    pin_dia = PIN_DIAMETER # 2.80 mm
    radial_gap = (cradle_dia - pin_dia) / 2.0 # 0.10 mm
    
    print(f"Tower Gap in X:      {tower_gap:.2f} mm")
    print(f"Shaft Hub Width:     {hub_w:.2f} mm")
    print(f"-> Axial Clearance:  {axial_gap:.3f} mm per side (0.10 mm is TIGHT for FDM print layers!)")
    print(f"Cradle Socket Dia:   Ø{cradle_dia:.2f} mm")
    print(f"Shaft Pin Dia:       Ø{pin_dia:.2f} mm")
    print(f"-> Radial Clearance: {radial_gap:.3f} mm")
    
    print("\nRECOMMENDED TOLERANCE TWEAKS TO ELIMINATE FRICTION:")
    print("1. Reduce Hub Width from 7.50 mm to 7.20 mm (increases axial clearance to 0.25 mm per side).")
    print("2. Reduce Pin Diameter from Ø2.80 mm to Ø2.70 mm (increases radial clearance to 0.15 mm).")
    print("3. Extend Through-Hole from Y=13.08 to Y=14.50 mm so plunger has 100% full unconstrained travel.")

if __name__ == '__main__':
    run()
