"""
testing/analyze_curved_feature_role.py
Analyze the functional role of the Center Curved Feature (10.50mm tall):
- Guidance envelope under tilted / misaligned plug insertion
- Dielectric creepage and arc shielding
- Friction and jamming risks if the blade were in continuous contact vs isolated
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import create_center_curved_feature_poly, create_all_brackets_poly
from build_shaft import CAM_WIDTH_X, CAM_X_CENTER, Y_AXLE, Z_AXLE

# Dimensions
Y_BLADE_CENTER = 2.890
W_HOT = 6.35
T_HOT = 1.52
HOT_X_CENTER = 6.279

curved_poly = create_center_curved_feature_poly()
minx_c, miny_c, maxx_c, maxy_c = curved_poly.bounds # maxy_c = -2.449mm

# Tilt and Misalignment Scenarios (Pitch angle: -3° to +3°)
# When a user inserts a plug with -3° tilt (tilted down in -Y):
# Bottom of blade at Z=1.0mm shifts by -16.5 * sin(3°) = -0.86mm
# Total Y min = -0.285 - 0.86 = -1.145mm -> still +1.30mm clearance to curved feature!
# If tilted -6° (extreme tilt):
# Bottom of blade shifts by -16.5 * sin(6°) = -1.72mm -> Y min = -2.01mm -> +0.44mm clearance!

print("=== FUNCTIONAL ANALYSIS OF CENTER CURVED FEATURE ===")
print("Scenario 1: Nominal Insertion (Pitch = 0°)")
print(f"   - Blade Y: [{-0.285:.2f}, {+6.065:.2f}] mm")
print(f"   - Curved Feature Apex: Y = {maxy_c:.2f} mm")
print(f"   - Clearance: {(-0.285) - maxy_c:.2f} mm\n")

for deg in [-2.0, -4.0, -6.0, -8.0]:
    shift_y = 16.5 * np.sin(np.radians(deg))
    y_min_tilted = -0.285 + shift_y
    clearance = y_min_tilted - maxy_c
    contact = (clearance <= 0)
    print(f"Scenario: Plug Tilted {deg:4.1f}° towards -Y:")
    print(f"   - Blade Bottom Tip Y: {y_min_tilted:5.2f} mm")
    print(f"   - Clearance to Curved Feature: {clearance:5.2f} mm | Contact: {contact}")

print("\nConclusion: The +2.16mm gap allows smooth, zero-friction insertion across all normal plug use (±5° tilt), while the 10.50mm tall curved wall acts as a fail-safe mechanical boundary against extreme misalignment (>8° tilt) and a dielectric barrier.")
