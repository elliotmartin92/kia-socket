"""
testing/analyze_user_blade_measurement.py
Analyze the user's measurement:
"FYI, I measure this to be 10.5mm from the interior wall of the mating part to the tip of the blade."
and "inserting a plug isn't actuating the lever all the way up."
"""

import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
import build_part as bp

print("=" * 80)
print("ANALYSIS OF USER'S 10.5mm BLADE MEASUREMENT")
print("=" * 80)

# Main part Z elevations:
# Z = 0.00: Baseplate bottom face
# Z = 1.00: Baseplate floor top
# Z = 4.60: Brackets top
# Z = 4.97: Clip undercut shelf (latch datum)
# Z = 6.77: Outer perimeter wall top (rim)
# Z = 10.50: Center curved feature apex
# Z = 12.59: Shaft axle center
# Z = 14.09: Shaft towers top

blade_reach = 10.50 # mm from interior wall of mating part to blade tip

print(f"User measurement: Blade extends {blade_reach:.2f} mm into the assembly from mating part interior wall.")
print("\nLet's evaluate where the blade tip lands (Z_tip) under different datum interpretations:\n")

# Interpretation 1: Mating part interior wall rests against the top rim of our perimeter wall (Z = 6.77mm)
# If the mating part slides OVER our outer wall, its interior ceiling might sit at Z = 6.77mm (or higher, e.g. covering towers).
# BUT the plug blade enters from the front (pointing in -Z toward the baseplate floor).
# Wait, does the blade enter in -Z (from top down toward Z=0)?
# YES! The plug is inserted into the front receptacle, so the prongs move in -Z toward the baseplate floor (Z=1.00mm).

# Datum Option A: Interior wall of mating part is at the top of the outer wall (Z = 6.77 mm)
z_datum_A = 6.77
z_tip_A = z_datum_A - blade_reach # 6.77 - 10.50 = -3.73 mm (through the floor!)

# Datum Option B: Interior wall is the front faceplate inside surface. Where are the towers?
# Towers extend to Z = 14.09 mm!
# If the front receptacle fits over the entire baseplate including the towers (Z_top = 14.09mm),
# then the interior wall/ceiling of the receptacle MUST clear the towers: Z_interior >= 14.09 mm!
# E.g., if Z_interior = 14.50 mm (just above towers):
# Then blade tip with 10.5mm reach would be:
z_datum_B1 = 14.09
z_tip_B1 = z_datum_B1 - blade_reach # 14.09 - 10.50 = 3.59 mm!

# Datum Option B2: If Z_interior = 15.00 mm:
z_datum_B2 = 15.00
z_tip_B2 = z_datum_B2 - blade_reach # 15.00 - 10.50 = 4.50 mm!

# Datum Option B3: If Z_interior = 16.00 mm:
z_datum_B3 = 16.00
z_tip_B3 = z_datum_B3 - blade_reach # 16.00 - 10.50 = 5.50 mm!

# Datum Option B4: If Z_interior = 17.00 mm:
z_datum_B4 = 17.00
z_tip_B4 = z_datum_B4 - blade_reach # 17.00 - 10.50 = 6.50 mm!

# Datum Option B5: If Z_interior = 17.27mm (Shaft axle 12.59 + 4.68mm):
# Let's check what Z_tip is needed to actuate the current cam!

print("Datum Option A (If interior wall = perimeter wall top Z = 6.77):")
print(f"  Z_tip = {z_tip_A:.2f} mm")

print("\nDatum Option B (If interior wall clears towers Z >= 14.09):")
for z_int in [14.09, 14.50, 15.00, 15.50, 16.00, 16.50, 17.00, 17.50]:
    zt = z_int - blade_reach
    print(f"  Interior wall at Z = {z_int:5.2f} mm -> Blade tip at Z_tip = {zt:5.2f} mm")

# Datum Option C: What if "interior wall of the mating part" is the interior surface where the blade emerges?
# Notice: In the front receptacle bezel, the AC plug slots are formed in the front face.
# Inside the receptacle, there is the interior wall (the backside of the front face where the blade exits the guide slot).
# If the blade length is measured from that interior wall to the tip = 10.5mm:
# Total NEMA plug blade length is typically 16.0 to 17.0 mm (standard 5/8 in = 15.88mm min, 17.0mm max).
# Front faceplate / bezel thickness + slot depth = 16.5 - 10.5 = 6.0 mm!
# That matches typical automotive outlet bezels (face thickness + shutter/slot guide = 5.5 - 6.5 mm)!
print("\nStandard NEMA 5-15 blade total length: 16.50 mm")
print(f"  If blade protrudes 10.50 mm from interior wall -> Bezel wall thickness = {16.50 - 10.50:.2f} mm")
print("  This perfectly matches standard US AC outlet faceplate thickness (~6.0 mm)!")
