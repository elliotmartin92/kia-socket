"""
testing/simulate_full_seating_stackup.py
Calculates exact geometric stackup of:
1. Plug blade penetration depth from front bezel to baseplate floor
2. Cam elevation vs blade tip elevation throughout full insertion
3. Plunger position and clearance against PCB switch and through-hole
4. Key physical measurements (with calipers) to verify interference
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    BASE_THICK, TOWER_HEIGHT, OUTER_WALL_HEIGHT
)

def run():
    print("================================================================================")
    print("PLUG BLADE SEATING & ROCKER INTERFERENCE: STACKUP & MEASUREMENT ANALYSIS")
    print("================================================================================")
    
    # Dimensions
    # Baseplate:
    # Z = 0.00 mm (Bottom face)
    # Z = 1.00 mm (Floor top face)
    # Z = 4.60 mm (Bracket top)
    # Z = 6.77 mm (Outer perimeter wall top)
    # Z = 12.59 mm (Pivot axle center)
    # Z = 14.09 mm (Tower top)
    
    # In the Kia outlet housing:
    # Front bezel / faceplate snaps over the perimeter wall.
    # The front face of the outlet where the plug sits is typically at or slightly above the perimeter wall/towers.
    # Standard NEMA 1-15 / 5-15 plug:
    # Blade length L_blade = 16.0 to 17.5 mm (nominally 16.5 mm = 0.650 in, min 15.88 mm = 0.625 in).
    # If the plug faceplate rests at Z_fascia:
    # If Z_fascia ~ 18.0 mm (just above tower tips Z=14.09mm + bezel thickness):
    # Then fully seated blade tip is at Z_tip = Z_fascia - L_blade.
    # E.g. If Z_fascia = 18.0 mm and L_blade = 16.5 mm, Z_tip_seated = 1.50 mm (just above floor Z=1.0 mm).
    # If L_blade = 17.0 mm, Z_tip_seated = 1.00 mm.
    # If Z_fascia = 19.0 mm, Z_tip_seated = 2.50 mm.
    
    print("\n--- 1. VERTICAL (Z-AXIS) ELEVATIONS ---")
    print(f"  Baseplate Floor Bottom Datum:  Z =  0.00 mm")
    print(f"  Baseplate Floor Top Surface:   Z =  {BASE_THICK:.2f} mm")
    print(f"  Guide Brackets Top:            Z =  4.60 mm")
    print(f"  Perimeter Outer Wall Top:      Z =  {OUTER_WALL_HEIGHT:.2f} mm")
    print(f"  Shaft Axle Center:             Z = {Z_AXLE:.2f} mm (Y = {Y_AXLE:.2f} mm)")
    print(f"  Shaft Retention Towers Top:    Z = {BASE_THICK + TOWER_HEIGHT:.2f} mm")
    print(f"  Tactile Switch Actuation:      Z = -{PLUNGER_REACH_BELOW_Z:.2f} mm")
    
    # Rocker Cam profile in build_shaft.py:
    # poly_pts_cam = [
    #   (9.28, 12.59), (9.28, 15.19), (5.00, 9.80), (1.50, 7.20), (1.80, 5.00), (4.50, 5.20), (7.78, 10.09)
    # ]
    r_hub = HUB_DIAMETER / 2.0
    cam_pts = np.array([
        [Y_AXLE, Z_AXLE],
        [Y_AXLE, Z_AXLE + r_hub + 0.5],
        [5.00, 9.80],
        [1.50, 7.20],
        [1.80, 5.00],
        [4.50, 5.20],
        [Y_AXLE - 1.50, Z_AXLE - 2.50]
    ])
    
    print("\n--- 2. CAM ELEVATION VS ROTATION ANGLE ---")
    print("Angle (deg) | Cam Lowest Z (mm) | Cam Leading Top Z (mm) | Plunger Tip Z (mm) | Plunger Tip Y (mm)")
    for deg in [0, 2, 4, 6, 8, 10, 12, 14, 16]:
        rad = np.radians(deg)
        c, s = np.cos(rad), np.sin(rad)
        
        # Cam rot
        c_rot = np.zeros_like(cam_pts)
        for i, (y, z) in enumerate(cam_pts):
            dy, dz = y - Y_AXLE, z - Z_AXLE
            c_rot[i, 0] = Y_AXLE + c * dy - s * dz
            c_rot[i, 1] = Z_AXLE + s * dy + c * dz
            
        dy_p, dz_p = 10.479 - Y_AXLE, -6.50 - Z_AXLE
        y_tip = Y_AXLE + c * dy_p - s * dz_p
        z_tip = Z_AXLE + s * dy_p + c * dz_p
        
        print(f"{deg:11.1f} | {c_rot[:, 1].min():17.2f} | {c_rot[2:4, 1].max():22.2f} | {z_tip:18.2f} | {y_tip:18.2f}")
        
    print("\n--- 3. POTENTIAL INTERFERENCE SCENARIOS & CRITICAL MEASUREMENTS ---")
    print("Scenario A: Rocker Cam Bottoming Out / Too Thick under the Blade")
    print("  - If the blade reaches Z = 1.0 - 3.0 mm, but the cam at maximum rotation only drops to Z = 3.6 - 4.5 mm.")
    print("  - Result: The blade hits the cam before the plug faceplate seats against the bezel.")
    print("")
    print("Scenario B: Plunger Bottoming on Tactile Switch / PCB")
    print("  - If the plunger reaches the PCB / solid switch stop after only ~6° rotation (Cam at Z ~ 6.5 mm),")
    print("    the rocker arm locks rigidly and stops the blade from inserting further.")
    print("")
    print("Scenario C: Plunger Hitting Baseplate Floor Through-Hole Wall")
    print("  - Through-hole max Y = 13.08 mm. At theta = 12°, plunger tip Y = 14.42 mm, body at Z=0 is Y=12.79 mm.")
    print("")
    print("Scenario D: Cam Interfering with Brass Contact Clip")
    print("  - If the cam arm collides with the brass contact spring leaves, it cannot swing down.")
    print("")
    print("Scenario E: Axle / Pin Binding or Rocker Width Interference")
    print("  - If rocker hub (7.50mm) binds between towers (7.70mm), or pins (Ø2.8mm in Ø3.0mm) bind under load.")

if __name__ == '__main__':
    run()
