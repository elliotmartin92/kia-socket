import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np
import build_clamp as bc

bc.CLAMP_ROOF_THICK = 1.00   # 1.00mm roof thickness (Z_top = 15.090mm, -1.20mm reduction!)
bc.Z_PIN_RELIEF = 14.280      # 14.28mm ceiling (+0.29mm air gap over 13.99mm pin top)
bc.Z_KEEL = bc.Z_PIN_RELIEF

c_unified = bc.build_unified_clamp_mesh(in_assembly_coords=True)

print("=== 1.00MM ROOF UNIFIED CLAMP MESH PROPERTIES ===")
print(f"Watertight: {c_unified.is_watertight}")
print(f"Volume: {c_unified.volume:.2f} mm³")
print(f"Bounds Z: [{c_unified.bounds[0,2]:.3f}, {c_unified.bounds[1,2]:.3f}] mm")

from build_shaft import build_shaft_rocker_mesh
shaft = build_shaft_rocker_mesh(in_assembly_coords=True)

inter = c_unified.intersection(shaft, engine='manifold')
print(f"Interference with shaft rocker: {inter.volume:.4f} mm³")

c_print = bc.build_unified_clamp_mesh(in_assembly_coords=False)
print(f"Printable clamp watertight: {c_print.is_watertight}, Z_max = {c_print.bounds[1,2]:.3f}")

c_left = bc.build_tower_clamp_mesh('left', in_assembly_coords=False)
c_right = bc.build_tower_clamp_mesh('right', in_assembly_coords=False)
print(f"Left clamp watertight: {c_left.is_watertight}, Right clamp watertight: {c_right.is_watertight}")
