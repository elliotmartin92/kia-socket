"""
testing/test_full_shifted_assembly.py
Test complete build_part and build_shaft pipelines with towers and shaft at Y_SHAFT = 9.279mm.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh

from build_part import build_exact_3d_model, build_clean_shaft_towers_mesh, build_left_tower_struts_mesh
from build_shaft import build_shaft_rocker_mesh

# Let's verify watertightness, clearance, and alignment
print("Verifying shifted assembly components:")
towers_mesh = build_clean_shaft_towers_mesh()
print(f"Towers Mesh: Watertight={towers_mesh.is_watertight}, Bounds={towers_mesh.bounds}")

shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)
print(f"Shaft Assembled Mesh: Watertight={shaft_mesh.is_watertight}, Bounds={shaft_mesh.bounds}")
