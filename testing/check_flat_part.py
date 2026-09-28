import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part

# In build_part, remove mesh_clip_supports from full_part concatenation:
# Let's inspect full_part with and without clip supports
part_mesh, base_poly = build_part.build_exact_3d_model()
print("Original flat part bounds:", part_mesh.bounds)
print("Original flat part is watertight:", part_mesh.is_watertight)
