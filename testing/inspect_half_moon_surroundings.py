import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

part_mesh_flat, base_poly = build_part.build_exact_3d_model()
c_feat = build_part.build_center_curved_feature_mesh()

print("Center curved feature bounds:", c_feat.bounds.tolist())

# What is behind Y = -5.05 mm?
# Baseplate floor extends in -Y down to what?
print("Baseplate bounds:", part_mesh_flat.bounds.tolist())

# Inside bracket channel 3 & 4:
# X in [2.70, 9.86]
# Y in [-6.20, 6.40]
# Half moon is at X in [4.18, 8.38], Y in [-5.05, -3.60], Z in [1.00, 10.50].
# Behind the half moon is Y in [-6.20, -5.05] (a 1.15mm gap before bracket spine ends at -6.20)
# And the floor at Z in [0, 1.00] extends everywhere!
