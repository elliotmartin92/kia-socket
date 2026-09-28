import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

part_flat, base_poly = bp.build_exact_3d_model()
bodies = part_flat.split(only_watertight=False)
print(f"Total bodies in part_flat: {len(bodies)}")

for i, b in enumerate(bodies):
    print(f"Body {i:2d}: watertight={b.is_watertight}, volume={b.volume:.4f}, bounds Z: [{b.bounds[0,2]:.2f}, {b.bounds[1,2]:.2f}]")
