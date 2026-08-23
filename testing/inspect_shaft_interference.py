import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE, X_LEFT_TOWER_INNER, X_LEFT_TOWER_OUTER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER, HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN, PLUNGER_WIDTH_X, PLUNGER_THICK_Y, INPUT_CAM_WIDTH_X, INPUT_CAM_X_CENTER
from build_part import get_exact_base_polygon, OUTER_WALL_THICK
import trimesh
import numpy as np

# Load main part mesh
part_mesh = trimesh.load('part.stl')
shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)

print("--- Shaft Rocker Mesh Bounds ---")
print(f"X range: [{shaft_mesh.bounds[0, 0]:.3f}, {shaft_mesh.bounds[1, 0]:.3f}] mm (Total Span in X = {shaft_mesh.bounds[1, 0] - shaft_mesh.bounds[0, 0]:.3f} mm)")
print(f"Y range: [{shaft_mesh.bounds[0, 1]:.3f}, {shaft_mesh.bounds[1, 1]:.3f}] mm")
print(f"Z range: [{shaft_mesh.bounds[0, 2]:.3f}, {shaft_mesh.bounds[1, 2]:.3f}] mm")

hole_x_min = HOLE_X_CENTER - HOLE_X_WIDTH/2.0
hole_x_max = HOLE_X_CENTER + HOLE_X_WIDTH/2.0
hole_y_min = HOLE_Y_CENTER - HOLE_Y_LEN/2.0
hole_y_max = HOLE_Y_CENTER + HOLE_Y_LEN/2.0

print("\n--- Key Landmarks ---")
print(f"Left Tower:  Outer X = {X_LEFT_TOWER_OUTER:.3f}, Inner X = {X_LEFT_TOWER_INNER:.3f}")
print(f"Right Tower: Inner X = {X_RIGHT_TOWER_INNER:.3f}, Outer X = {X_RIGHT_TOWER_OUTER:.3f}")
print(f"Between Towers Clearance: {X_RIGHT_TOWER_INNER - X_LEFT_TOWER_INNER:.3f} mm")
print(f"Through-Hole: X in [{hole_x_min:.3f}, {hole_x_max:.3f}], Y in [{hole_y_min:.3f}, {hole_y_max:.3f}]")

# Let us check the distance between Right Tower Outer face and Outer Wall at Y = Y_AXLE (7.67mm):
base_poly, outer_poly, _ = get_exact_base_polygon()
inner_poly = outer_poly.buffer(-OUTER_WALL_THICK)
from shapely.geometry import LineString
y_line = LineString([(-30, Y_AXLE), (30, Y_AXLE)])
inter_out = outer_poly.exterior.intersection(y_line)
inter_in = inner_poly.exterior.intersection(y_line)
out_pts = [p.x for p in inter_out.geoms] if hasattr(inter_out, 'geoms') else [inter_out.x]
in_pts = [p.x for p in inter_in.geoms] if hasattr(inter_in, 'geoms') else [inter_in.x]
print(f"\nAt Y_AXLE = {Y_AXLE:.3f} mm:")
print(f"Outer Wall X coords: {out_pts}")
print(f"Inner Wall X coords: {in_pts}")

print(f"Gap from Right Tower Outer Face ({X_RIGHT_TOWER_OUTER:.3f} mm) to Inner Wall ({max(in_pts):.3f} mm): {max(in_pts) - X_RIGHT_TOWER_OUTER:.3f} mm")
print(f"Current Right Axle Tip X = {shaft_mesh.bounds[1, 0]:.3f} mm (Gap to Inner Wall = {max(in_pts) - shaft_mesh.bounds[1, 0]:.3f} mm)")

