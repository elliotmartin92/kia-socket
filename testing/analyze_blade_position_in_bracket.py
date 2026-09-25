"""
testing/analyze_blade_position_in_bracket.py
Calculates exact blade position in Y based on:
1. Brass contact spring fingers (from caliper model and photos)
2. Cantilever cam tab stroke and contact position
3. Current half moon position vs required moon position
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box, LineString

import build_part as bp
import build_shaft as bs

print("=== BRACKET & RIB GEOMETRY ===")
b3 = bp.to_mm_poly(bp.bracket_3_raw_pts)
b4 = bp.to_mm_poly(bp.bracket_4_raw_pts)
print(f"Bracket 3 Y bounds: [{b3.bounds[1]:.3f}, {b3.bounds[3]:.3f}] (Center = {(b3.bounds[1]+b3.bounds[3])/2:.3f})")
print(f"Bracket 4 Y bounds: [{b4.bounds[1]:.3f}, {b4.bounds[3]:.3f}] (Center = {(b4.bounds[1]+b4.bounds[3])/2:.3f})")

ribs = bp.BRACKET_SEATING_RIB_Y
print(f"Seating Ribs: Rib 1 = {ribs[0]:.2f}, Rib 2 = {ribs[1]:.2f}, Rib 3 = {ribs[2]:.2f}, Rib 4 = {ribs[3]:.2f}")
rib_span_y = ribs[0] - ribs[3] # 5.25 - (-4.65) = 9.90 mm
rib_mid_y = (ribs[0] + ribs[3]) / 2.0 # 0.30 mm
print(f"Rib span: {rib_span_y:.2f} mm, Midpoint = {rib_mid_y:.2f} mm")

# In the brass part:
# The brass stamping has two vertical fingers.
# The pinch throat is between Rib 2 (Y=1.95) and Rib 3 (Y=-1.35).
# The center of the pinch throat is around Y = (1.95 + (-1.35)) / 2 = 0.30 mm!
# And the brass leaves have a total width along Y.
# Standard blade width = 6.35 mm (1/4").
# If the blade is centered in the pinch throat at Y_center = 0.30 mm:
y_blade_c = rib_mid_y
y_blade_top = y_blade_c + 6.35 / 2.0
y_blade_bot = y_blade_c - 6.35 / 2.0
print(f"\nIf blade is centered at pinch throat (Y = {y_blade_c:.2f} mm):")
print(f"  Blade Y range: [{y_blade_bot:.3f}, {y_blade_top:.3f}] mm")
print(f"  Blade Top (+Y edge): {y_blade_top:.3f} mm")
print(f"  Blade Bottom (-Y edge): {y_blade_bot:.3f} mm")

# Current Half Moon
curved_poly = bp.create_center_curved_feature_poly()
moon_apex_y = curved_poly.bounds[3]
moon_base_y = curved_poly.bounds[1]
print(f"\nCurrent Half Moon:")
print(f"  Base Y = {moon_base_y:.3f} mm")
print(f"  Apex Y = {moon_apex_y:.3f} mm")
print(f"  Overlap with centered blade: {moon_apex_y - y_blade_bot:.3f} mm collision!")

# Now what if the blade contacts the cantilever?
# Where is the cantilever contact surface?
# Top ramp runs from (Y=1.50, Z=6.30) to (Y=5.00, Z=8.90).
# When the blade is inserted, its top face (+Y) engages the top ramp.
# At Z = 10.50 (the top of the moon and top of the insertion path):
# Cam surface is at Y = 6.00 mm.
# At Z = 8.90: Cam surface is at Y = 5.00 mm.
# At Z = 6.30: Cam surface is at Y = 1.50 mm (nose tip).
# If the blade's +Y edge is pushed against the cam ramp:
# Suppose the blade's +Y edge is at Y_cam:
# If blade's +Y edge is at Y = 3.50 mm:
# Then blade's -Y edge is at 3.50 - 6.35 = -2.85 mm!
# If blade's +Y edge is at Y = 4.00 mm:
# Then blade's -Y edge is at 4.00 - 6.35 = -2.35 mm!
# If blade's +Y edge is at Y = 3.00 mm:
# Then blade's -Y edge is at 3.00 - 6.35 = -3.35 mm!

print("\n=== BLADE POSITION VS CANTILEVER & MOON ===")
print("User prompt says:")
print("  'Its job is to ensure the blade does not deflect down, that way the blade makes contact with the cantilever.'")
print("  'But if it is too high in the Y, the blade may play a role in snapping the moon.'")
print("  'So we should analyze the space between the moon and cantilever and calibrate it to a blade.'")
