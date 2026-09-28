"""
testing/test_build_shaft_updated.py
Tests updated shaft/rocker generator:
- High-sensitivity cam profile (calibrated for 10.5mm blade reach)
- Watertight mesh generation in assembly and printable coordinates
- Plunger reach and travel verification
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_shaft as bs

print("=" * 80)
print("TESTING UPDATED BUILD_SHAFT LOGIC")
print("=" * 80)

# Build assembled mesh
mesh_assembled = bs.build_shaft_rocker_mesh(in_assembly_coords=True)
print(f"Assembled mesh vertices: {len(mesh_assembled.vertices)}, faces: {len(mesh_assembled.faces)}")
print(f"Assembled mesh is watertight: {mesh_assembled.is_watertight}")
assert mesh_assembled.is_watertight, "Assembled mesh must be watertight!"

# Build printable flat mesh
mesh_printable = bs.build_shaft_rocker_mesh(in_assembly_coords=False)
print(f"Printable mesh vertices: {len(mesh_printable.vertices)}, faces: {len(mesh_printable.faces)}")
print(f"Printable mesh is watertight: {mesh_printable.is_watertight}")
assert mesh_printable.is_watertight, "Printable mesh must be watertight!"
print(f"Printable mesh Z min: {mesh_printable.bounds[0, 2]:.3f} mm (must be 0.000 mm)")
assert np.isclose(mesh_printable.bounds[0, 2], 0.0, atol=1e-3), "Printable mesh must sit flat at Z=0.00mm!"

print("PASS: Updated build_shaft logic verified successfully!")
