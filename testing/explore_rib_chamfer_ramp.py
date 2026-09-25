"""
testing/explore_rib_chamfer_ramp.py
Explores adding a chamfered ramp / reinforced pedestal from Rib 4 to the half moon
and between the ribs to eliminate stress concentration without interfering with the brass insert.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, box, LineString
import matplotlib.pyplot as plt

import build_part as bp

print("=== RIB & HALF MOON INTERACTION ===")
b3 = bp.to_mm_poly(bp.bracket_3_raw_pts)
b4 = bp.to_mm_poly(bp.bracket_4_raw_pts)

# Seating Rib 4:
# Rib 4 Y center = -4.65 mm, thickness = 0.60 mm -> Y in [-4.95, -4.35] mm
# Rib 3 Y center = -1.35 mm, thickness = 0.60 mm -> Y in [-1.65, -1.05] mm
# Half moon:
# Base Y = -4.30 mm, Apex Y = -3.00 mm
# Half moon is directly adjacent to Rib 4 (gap of 0.05 mm between -4.30 and -4.35 mm)!

print(f"Rib 4 span in Y: [{-4.65 - 0.30:.2f}, {-4.65 + 0.30:.2f}] mm")
print(f"Half moon span in Y: [-4.30, -3.00] mm")
print(f"Distance from Rib 4 top edge (-4.35mm) to Half Moon Base (-4.30mm): 0.05mm!")
print(f"Rib 3 span in Y: [{-1.35 - 0.30:.2f}, {-1.35 + 0.30:.2f}] mm")
print(f"Distance from Half Moon Apex (-3.00mm) to Rib 3 bottom edge (-1.65mm): 1.35mm")

# Rib height in Z:
z_floor = bp.BASE_THICK  # 1.00 mm
z_rib = bp.BASE_THICK + bp.BRACKET_SEATING_RIB_HEIGHT  # 2.15 mm
h_rib = bp.BRACKET_SEATING_RIB_HEIGHT  # 1.15 mm

print(f"\nElevations in Z:")
print(f"Floor: Z = {z_floor:.2f} mm")
print(f"Rib Top / Brass Seating Surface: Z = {z_rib:.2f} mm (Height = {h_rib:.2f} mm)")
print(f"Half Moon Top: Z = 10.50 mm")

# Where does the brass insert sit?
# The brass insert sits on the ribs at Z = 2.15 mm!
# In Rib 4 (Y in [-4.95, -4.35]):
# The brass U-bridge rests on top of Rib 4 at Z = 2.15 mm.
# From Rib 4 in Bracket 3 (X in [2.70, 4.50]) across to Rib 4 in Bracket 4 (X in [8.00, 9.86]):
# The brass U-bridge connects across the channel (X in [4.50, 8.00]).
# And the brass U-bridge is at Z >= 2.15 mm!
# That means from Z = 1.00 mm to Z = 2.15 mm, between X = 4.50 and 8.00 mm:
# It is 100% EMPTY SPACE!
# Currently, Rib 4 only exists in Bracket 3 and Bracket 4, NOT in the central channel!
# But the brass bridge sits at Z = 2.15 mm across the entire width!
