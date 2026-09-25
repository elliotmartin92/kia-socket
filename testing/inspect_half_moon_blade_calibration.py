"""
testing/inspect_half_moon_blade_calibration.py
Analyzes the space between the half moon and the cantilever (cam tab),
calibrated to a standard NEMA plug blade (width = 6.35mm, thickness = 1.52mm).
Also checks brass insert clearance in Brackets 3 & 4.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, Point, box, LineString
import trimesh

import build_part as bp
import build_shaft as bs

print("=" * 60)
print("1. CANTILEVER (CAM TAB) PROFILE IN (Y, Z)")
print("=" * 60)
# Cam tab definition from build_shaft.py:
DZ_CAM = 0.90
y_axle = bs.Y_AXLE  # 9.279
z_axle = bs.Z_AXLE  # 12.590
r_hub = bs.HUB_DIAMETER / 2.0  # 2.10

poly_pts_cam = [
    (y_axle, z_axle),                          # Center of hub (9.279, 12.590)
    (y_axle, z_axle + r_hub),                  # (9.279, 14.690) - Flush tangent at hub top
    (6.80, 11.50),                             # Smooth blend from hub down toward throat
    (5.00, 9.80 - DZ_CAM),                     # (5.00, 8.90) - Lowered top ramp
    (1.50, 7.20 - DZ_CAM),                     # (1.50, 6.30) - Lowered contact tip inside throat
    (1.80, 5.00 - DZ_CAM),                     # (1.80, 4.10) - Lowered rounded nose bottom
    (4.50, 5.20 - DZ_CAM),                     # (4.50, 4.30) - Lowered beam underside
    (y_axle - 1.50, z_axle - 2.50)             # (7.779, 10.090) - Smooth return into hub belly
]

cam_y_pts = [p[0] for p in poly_pts_cam]
cam_z_pts = [p[1] for p in poly_pts_cam]
print(f"Cam Tab X: center = {bs.CAM_X_CENTER:.3f} mm, width = {bs.CAM_WIDTH_X:.3f} mm -> X in [{bs.CAM_X_CENTER - bs.CAM_WIDTH_X/2:.3f}, {bs.CAM_X_CENTER + bs.CAM_WIDTH_X/2:.3f}] mm")
print(f"Cam Tab Y range: min = {min(cam_y_pts):.3f} mm (tip at Z=6.30), max = {max(cam_y_pts):.3f} mm")
print(f"Cam Tab Top Ramp: from (Y=5.00, Z=8.90) down to (Y=1.50, Z=6.30)")

print("\n" + "=" * 60)
print("2. CURRENT HALF MOON GEOMETRY")
print("=" * 60)
curved_poly = bp.create_center_curved_feature_poly()
bounds = curved_poly.bounds
print(f"Half Moon bounds: X in [{bounds[0]:.3f}, {bounds[2]:.3f}] mm (Width = {bounds[2]-bounds[0]:.3f} mm)")
print(f"Half Moon bounds: Y in [{bounds[1]:.3f}, {bounds[3]:.3f}] mm (Depth = {bounds[3]-bounds[1]:.3f} mm)")
print(f"Half Moon Z range: 1.00 mm to 10.50 mm (Height = 9.50 mm)")
print(f"Half Moon Base Y: {bounds[1]:.3f} mm")
print(f"Half Moon Apex Y: {bounds[3]:.3f} mm")

print("\n" + "=" * 60)
print("3. SPACE BETWEEN CURRENT MOON AND CANTILEVER")
print("=" * 60)
# Gap between moon apex and cam tip:
gap_tip = 1.50 - bounds[3]
# Gap between moon apex and cam ramp at various Z:
# Ramp line equation between (Y=1.50, Z=6.30) and (Y=5.00, Z=8.90):
# slope dY/dZ = (5.00 - 1.50) / (8.90 - 6.30) = 3.50 / 2.60 = 1.346 mm/mm
# Y(Z) = 1.50 + 1.346 * (Z - 6.30)
print(f"Distance between moon apex (Y = {bounds[3]:.3f}) and cam contact tip (Y = 1.50): {gap_tip:.3f} mm")
print(f"Distance between moon apex and cam ramp at Z = 8.90 (Y = 5.00): {5.00 - bounds[3]:.3f} mm")
print(f"Distance between moon apex and cam ramp at Z = 10.50 (Y = 6.00): {6.00 - bounds[3]:.3f} mm")

print("\n" + "=" * 60)
print("4. NEMA 5-15 PLUG BLADE CALIBRATION")
print("=" * 60)
BLADE_WIDTH_Y = 6.35  # Standard 1/4" NEMA blade width
BLADE_THICK_X = 1.52  # Standard 0.060" NEMA blade thickness

print(f"Standard Blade Width in Y: {BLADE_WIDTH_Y:.2f} mm")
print(f"Standard Blade Thickness in X: {BLADE_THICK_X:.2f} mm")

# Where does the blade sit in Y?
# The blade is constrained in Y:
# 1. By the outlet faceplate plug opening (NEMA 5-15 standard slot):
# In standard duplex / round outlet receptacles:
# The hot and neutral slots are centered relative to the ground pin.
# Let's check where the ground pin center is in this model!
# Ground arch wall in build_part.py:
arch_poly = bp.create_arch_wall_poly()
arch_bounds = arch_poly.bounds
print(f"Ground Arch bounds: X in [{arch_bounds[0]:.3f}, {arch_bounds[2]:.3f}], Y in [{arch_bounds[1]:.3f}, {arch_bounds[3]:.3f}]")

# Let's check the seating ribs in Brackets 3 & 4:
print(f"Bracket seating ribs: {bp.BRACKET_SEATING_RIB_Y}")
print(f"Bracket 3 & 4 inner channel: X in [4.50, 8.00] (Width = 3.50 mm)")
print(f"Bracket 3 & 4 outer guide bounds: X in [1.77, 10.79], Y in [-7.17, 7.17]")
