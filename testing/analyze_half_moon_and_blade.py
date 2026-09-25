import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, Point, box, LineString
import matplotlib.pyplot as plt

import build_part as bp
import build_shaft as bs

# Load polygons
base_poly, outer_poly, _ = bp.get_exact_base_polygon()
b3 = bp.to_mm_poly(bp.bracket_3_raw_pts)
b4 = bp.to_mm_poly(bp.bracket_4_raw_pts)
curved_poly = bp.create_center_curved_feature_poly()
seating_ribs = bp.create_bracket_seating_ribs_poly()

print("=== BRACKET 3 & 4 COORDINATES ===")
print(f"Bracket 3 bounds: X in [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}], Y in [{b3.bounds[1]:.3f}, {b3.bounds[3]:.3f}]")
print(f"Bracket 4 bounds: X in [{b4.bounds[0]:.3f}, {b4.bounds[2]:.3f}], Y in [{b4.bounds[1]:.3f}, {b4.bounds[3]:.3f}]")
print(f"Channel between Brackets 3 & 4: X in [{b3.bounds[2]:.3f}, {b4.bounds[0]:.3f}] -> Width = {b4.bounds[0] - b3.bounds[2]:.3f} mm")

print("\n=== CURRENT HALF MOON (CURVED FEATURE) ===")
print(f"Half Moon bounds: X in [{curved_poly.bounds[0]:.3f}, {curved_poly.bounds[2]:.3f}], Y in [{curved_poly.bounds[1]:.3f}, {curved_poly.bounds[3]:.3f}]")
print(f"Half Moon X-span: {curved_poly.bounds[2] - curved_poly.bounds[0]:.3f} mm")
print(f"Half Moon Y-span: {curved_poly.bounds[3] - curved_poly.bounds[1]:.3f} mm")

print("\n=== SEATING RIBS IN RIGHT BRACKETS (BRACKETS 3 & 4) ===")
# Ribs Y stations: [5.25, 1.95, -1.35, -4.65]
for idx, y_st in enumerate(bp.BRACKET_SEATING_RIB_Y):
    y_min_rib = y_st - bp.BRACKET_SEATING_RIB_THICK / 2.0
    y_max_rib = y_st + bp.BRACKET_SEATING_RIB_THICK / 2.0
    print(f"  Rib {idx+1}: Y = {y_st:.2f} mm (Y in [{y_min_rib:.2f}, {y_max_rib:.2f}] mm)")

print("\n=== PLUG BLADE & CANTILEVER (CAM) ===")
# Cam tab
# In build_shaft.py:
# poly_pts_cam nose is at Y = 1.50..1.80mm, top ramp at Y = 5.00mm, X in [cam_x_c - cam_w_x/2, cam_x_c + cam_w_x/2]
print(f"Cam X center: {bs.CAM_X_CENTER:.3f} mm, width: {bs.CAM_WIDTH_X:.3f} mm (X in [{bs.CAM_X_CENTER - bs.CAM_WIDTH_X/2:.3f}, {bs.CAM_X_CENTER + bs.CAM_WIDTH_X/2:.3f}])")
print(f"Cam Nose Y: ~1.50 mm (at Z = 6.30 mm)")
print(f"Cam Axle Y: {bs.Y_AXLE:.3f} mm (at Z = {bs.Z_AXLE:.3f} mm)")

# NEMA 5-15 Plug Blade
# Width: 6.35 mm (0.250 in)
# Thickness: 1.52 mm (0.060 in)
# Centerline X = 6.279 mm (matches cam and channel centerline!)
# What is the blade Y range?
# If the blade contacts the cam tab (which has nose at Y = 1.50mm and ramp up to Y = 5.0mm):
# Where does the blade sit?
