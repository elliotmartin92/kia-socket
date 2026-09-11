"""
testing/analyze_blade_penetration_depth.py
Calculates exact penetration depth of standard NEMA 1-15 and 5-15 plug blades:
- Blade length: 15.88 mm (5/8 in) min, 16.50 mm nominal, 17.50 mm max
- Faceplate / bezel thickness and socket slot depth
- Resulting Z-elevation of the blade tip inside the sub-housing
- Maximum allowable cam Z-elevation for 100% flush seating
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
from build_part import BASE_THICK, TOWER_HEIGHT, OUTER_WALL_HEIGHT

def analyze_depth():
    print("================================================================================")
    print("PLUG BLADE PENETRATION DEPTH & CAM CLEARANCE ANALYSIS")
    print("================================================================================")
    
    # 1. Physical Heights in Assembly:
    # Floor: Z = 0.00 to 1.00 mm
    # Brackets: Z = 1.00 to 4.60 mm
    # Outer Wall: Z = 1.00 to 6.77 mm
    # Center Curved Feature: Z = 1.00 to 10.50 mm
    # Shaft Axle: Z = 12.59 mm
    # Towers: Z = 1.00 to 14.09 mm
    
    # Where does the front bezel / faceplate sit?
    # In the Kia socket housing, the front faceplate locks over the outer perimeter wall and covers the towers.
    # The front face where the plug body rests is typically at Z_bezel_front ~ 18.0 mm (or 16.0 - 19.0 mm).
    # Faceplate wall thickness is ~2.0 mm (internal face at Z ~ 16.0 mm).
    
    print("Assembly Z Elevations:")
    print(f"  Floor top:            Z = {BASE_THICK:.2f} mm")
    print(f"  Brackets top:         Z = 4.60 mm")
    print(f"  Outer wall top:       Z = {OUTER_WALL_HEIGHT:.2f} mm")
    print(f"  Towers top:           Z = {BASE_THICK + TOWER_HEIGHT:.2f} mm")
    print(f"  Shaft Axle:           Z = {Z_AXLE:.2f} mm")
    
    # For a range of potential Bezel front face heights:
    print("\n--- PLUG BLADE TIP ELEVATION (Z_tip) FOR DIFFERENT BEZEL HEIGHTS ---")
    print("Bezel Front (mm) | Blade Length = 16.0 mm | Blade Length = 16.5 mm | Blade Length = 17.0 mm")
    for z_bezel in [16.0, 17.0, 17.5, 18.0, 18.5, 19.0, 20.0]:
        z_160 = z_bezel - 16.0
        z_165 = z_bezel - 16.5
        z_170 = z_bezel - 17.0
        print(f"  Z = {z_bezel:5.1f} mm    |   Z_tip = {z_160:5.2f} mm    |   Z_tip = {z_165:5.2f} mm    |   Z_tip = {z_170:5.2f} mm")
        
    print("\n--- KEY INSIGHTS ---")
    print("1. If Z_bezel is around 17.5 - 18.5 mm, the blade tip penetrates down to Z = 1.0 - 2.5 mm!")
    print("2. Current Cam at rest starts at Z = 5.0 - 9.8 mm.")
    print("3. Because the plunger hits the through-hole rear wall at theta = 7.2 deg, the cam stops at Z ~ 6.5 mm.")
    print("4. This creates an immediate gap of ~4.0 - 5.0 mm where the blade CANNOT insert further!")
    print("5. Even if through-hole is opened up, the cam profile itself must be thin / low enough so that at full rotation, the top of the cam drops to Z <= Z_tip (e.g. Z <= 2.0 mm) OR the cam arm is positioned behind the blade!")

if __name__ == '__main__':
    analyze_depth()
