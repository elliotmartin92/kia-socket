import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from testing.test_slit_saddle import build_test_saddle

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

saddle = build_test_saddle()

# Check collision/clearance
# Using proximity query
proximity = trimesh.proximity.ProximityQuery(m_t)
dist = proximity.signed_distance(saddle.vertices)
print(f"Max penetration of saddle into base part: {dist.max():.4f} (must be <= 0.0 for no collision)")
print(f"Min distance from saddle to base part: {-dist.max():.4f} mm")
