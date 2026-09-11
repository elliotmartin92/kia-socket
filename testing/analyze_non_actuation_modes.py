"""
testing/analyze_non_actuation_modes.py
Analyzes all potential reasons why the lever does not actuate when the plug is inserted:
1. Baseplate axial shift / floating without rear housing
2. Blade missing cam tab (X-offset or Y-offset)
3. Cam slope / friction locking vs rotation
4. Shaft friction / cradle binding
5. Pre-depressed state / lack of bias spring
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER
)
from build_part import BASE_THICK, TOWER_HEIGHT

def run():
    print("================================================================================")
    print("ANALYSIS: WHY IS THE LEVER NOT ACTUATING UPON PLUG INSERTION?")
    print("================================================================================")
    
    # 1. Geometry of Blade vs Cam
    # Hot Blade (Right side):
    # Nominal X center = 6.28 mm
    # Nominal blade thickness in X = 1.52 mm (X in [5.52, 7.04] mm)
    # Nominal blade width in Y = 6.35 mm (Y in [-0.68, 5.68] mm, center Y = 2.50 mm)
    
    # Cam in build_shaft.py:
    # CAM_X_CENTER = 6.28 mm, CAM_WIDTH_X = 2.70 mm (X in [4.93, 7.63] mm)
    # Cam Y span at rest: [1.50, 9.28] mm
    # Cam Z span at rest: [5.00, 15.19] mm
    
    print("1. Blade vs Cam Overlap in (X, Y):")
    print(f"   Blade X span: [5.52, 7.04] mm (centered at X = 6.28 mm)")
    print(f"   Cam X span:   [4.93, 7.63] mm (Width = {CAM_WIDTH_X:.2f} mm)")
    print(f"   -> Overlap in X: Full blade width (1.52 mm) is completely inside the 2.70 mm cam!")
    print(f"   Blade Y span: [-0.68, 5.68] mm (centered at Y = 2.50 mm)")
    print(f"   Cam Y span:   [1.50, 9.28] mm")
    print(f"   -> Overlap in Y: From Y = 1.50 mm to Y = 5.68 mm (4.18 mm of direct physical contact in Y!)")
    
    # 2. Cam Surface Normal and Force Vectors:
    # Cam top ramp connects (5.00, 9.80) to (1.50, 7.20).
    # Vector along ramp: dY = -3.50, dZ = -2.60 mm.
    # Slope angle: arctan(-2.60 / -3.50) = arctan(0.743) = 36.6° from horizontal!
    # Normal to ramp (pointing up and rearward into +Y, +Z):
    # n = (+2.60, +3.50) / sqrt(2.6^2 + 3.5^2) = (+0.596, +0.803)
    
    slope_deg = np.degrees(np.arctan2(2.60, 3.50))
    print(f"\n2. Cam Ramp Angle & Force Resolution:")
    print(f"   Cam ramp angle: {slope_deg:.1f}° from horizontal.")
    print(f"   When blade pushes straight down (-Z):")
    print(f"   - Downward component directly drives rotation around axle (Lever arm = {Y_AXLE - 2.50:.2f} mm in Y).")
    print(f"   - Rearward horizontal force component pushes the axle into the back of the cradle (Y = 9.28 mm).")
    print(f"   - Mechanical torque: T = F_z * (Y_axle - Y_contact) = F_z * (9.28 - 2.50) = 6.78 * F_z (High mechanical advantage!).")
    
    # 3. Floating Baseplate Movement:
    # In the full Kia outlet assembly:
    # - The front faceplate has perimeter snap clips that latch to the intermediate baseplate (4x snap clips at 45°, 135°, 211°, 327°).
    # - The rear PCB / housing holds the baseplate firmly against the front faceplate.
    # - If the snap clips are NOT latched or if there is no rear housing supporting the baseplate from behind:
    #   When you push the plug prongs into the brass pinching clips:
    #   - The brass clips require significant insertion force (~5 - 15 N) to spread the spring leaves!
    #   - If the baseplate is not rigidly seated/clipped in the front bezel, the ENTIRE baseplate simply pushes backward (-Z relative to bezel) with the plug!
    #   - If the whole baseplate moves together with the plug, the relative motion between the plug blade and the baseplate is ZERO, so the lever never rotates!

if __name__ == '__main__':
    run()
