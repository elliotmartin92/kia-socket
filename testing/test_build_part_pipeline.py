import sys
sys.path.insert(0, '.')
import trimesh
import numpy as np
import build_part

# Temporarily test building the model with monolithic hooks
full_part, base_poly = build_part.build_exact_3d_model()
print("Current build_exact_3d_model watertight:", full_part.is_watertight)
