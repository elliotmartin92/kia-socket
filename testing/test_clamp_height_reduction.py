import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np

# Test modifying CLAMP_ROOF_THICK in build_clamp
import build_clamp as bc
bc.CLAMP_ROOF_THICK = 1.10   # 1.10mm roof thickness (Z_top = 15.190mm, -1.10mm reduction!)
bc.Z_PIN_RELIEF = 14.300      # 14.30mm ceiling (+0.31mm air gap over 13.99mm pin top)
bc.Z_KEEL = bc.Z_PIN_RELIEF

# Build unified clamp in assembly coords
c_unified = bc.build_unified_clamp_mesh(in_assembly_coords=True)

print("=== UNIFIED CLAMP MESH PROPERTIES ===")
print(f"Watertight: {c_unified.is_watertight}")
print(f"Volume: {c_unified.volume:.2f} mm³")
print(f"Bounds Z: [{c_unified.bounds[0,2]:.3f}, {c_unified.bounds[1,2]:.3f}] mm")
print(f"Bounds X: [{c_unified.bounds[0,0]:.3f}, {c_unified.bounds[1,0]:.3f}] mm")
print(f"Bounds Y: [{c_unified.bounds[0,1]:.3f}, {c_unified.bounds[1,1]:.3f}] mm")

# Load shaft rocker
from build_shaft import build_shaft_rocker_mesh
shaft = build_shaft_rocker_mesh(in_assembly_coords=True)

# Check interference with shaft
inter = c_unified.intersection(shaft, engine='manifold')
print(f"Interference with shaft rocker: {inter.volume:.4f} mm³ (expected 0.0000 mm³)")

# Load part
part = trimesh.load('part.stl')
# Check clearance to outer perimeter wall
from build_part import get_exact_base_polygon
_, outer_body_poly, _ = get_exact_base_polygon()
from shapely.geometry import Point
out_verts = [v for v in c_unified.vertices if not outer_body_poly.contains(Point(v[0], v[1]))]
print(f"Vertices outside baseplate perimeter: {len(out_verts)} (expected 0)")

# Test individual printable clamps
c_print = bc.build_unified_clamp_mesh(in_assembly_coords=False)
print(f"Printable clamp watertight: {c_print.is_watertight}, Z_min = {c_print.bounds[0,2]:.3f}, Z_max = {c_print.bounds[1,2]:.3f}")

c_left = bc.build_tower_clamp_mesh('left', in_assembly_coords=False)
c_right = bc.build_tower_clamp_mesh('right', in_assembly_coords=False)
print(f"Left clamp watertight: {c_left.is_watertight}, Right clamp watertight: {c_right.is_watertight}")

assert c_unified.is_watertight, "Unified clamp must be watertight!"
assert inter.volume < 0.001, "Interference with shaft must be zero!"
assert len(out_verts) == 0, "No vertices outside outer wall footprint!"
print("\nALL CLAMP HEIGHT REDUCTION TESTS PASSED!")
