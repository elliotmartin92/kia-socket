import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import create_all_brackets_poly, get_exact_base_polygon, bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, HOLE_X_CENTER, HOLE_X_WIDTH
import shapely.geometry as sg
import numpy as np

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

print("--- Bracket 3 Bounds ---")
print(f"X: [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}], Y: [{b3.bounds[1]:.3f}, {b3.bounds[3]:.3f}]")

print("--- Bracket 4 Bounds ---")
print(f"X: [{b4.bounds[0]:.3f}, {b4.bounds[2]:.3f}], Y: [{b4.bounds[1]:.3f}, {b4.bounds[3]:.3f}]")

print(f"Guide channel between B3 (right wall {b3.bounds[2]:.3f}) and B4 (left wall {b4.bounds[0]:.3f}):")
print(f"Channel X span: [{b3.bounds[2]:.3f}, {b4.bounds[0]:.3f}] mm (Width = {b4.bounds[0] - b3.bounds[2]:.3f} mm)")

print(f"\nThrough-Hole X span: [{HOLE_X_CENTER - HOLE_X_WIDTH/2:.3f}, {HOLE_X_CENTER + HOLE_X_WIDTH/2:.3f}] mm (Width = {HOLE_X_WIDTH:.3f} mm)")
print(f"Between Towers X span: [{X_LEFT_TOWER_INNER:.3f}, {X_RIGHT_TOWER_INNER:.3f}] mm (Clearance = {X_RIGHT_TOWER_INNER - X_LEFT_TOWER_INNER:.3f} mm)")
