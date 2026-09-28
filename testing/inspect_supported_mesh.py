import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, build_45deg_supported_part_mesh

part_flat, _ = build_exact_3d_model()
part_supported, part_tilted = build_45deg_supported_part_mesh(part_flat)

print(f"Supported mesh bounds:\n  X: {part_supported.bounds[0, 0]:.2f} to {part_supported.bounds[1, 0]:.2f}\n  Y: {part_supported.bounds[0, 1]:.2f} to {part_supported.bounds[1, 1]:.2f}\n  Z: {part_supported.bounds[0, 2]:.2f} to {part_supported.bounds[1, 2]:.2f}")
print("Number of bodies:", len(part_supported.split(only_watertight=False)))
