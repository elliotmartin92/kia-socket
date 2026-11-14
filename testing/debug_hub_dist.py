import numpy as np
import trimesh
import os, sys
from scipy.spatial import cKDTree

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft
from test_candidate_b4_strut import build_strut_option_b, R, z_min, shaft_tilted

strut = build_strut_option_b()
hub = shaft_tilted['hub']

print("Hub bounds in tilted:")
print(hub.bounds)
print("Strut bounds in tilted:")
print(strut.bounds)

# Query distances
tree_hub = cKDTree(hub.vertices)
ds, idxs = tree_hub.query(strut.vertices)
min_idx = np.argmin(ds)
print(f"Min distance to hub: {ds[min_idx]:.3f} mm")
print(f"Closest strut vertex: {strut.vertices[min_idx]}")
print(f"Closest hub vertex:   {hub.vertices[idxs[min_idx]]}")

# Wait! What was yp_target in build_strut_option_b?
# In test_candidate_b4_strut:
# yp_target = -1.351
# zp_target = 25.483 - 0.48 = 25.003
# Where is the hub cylinder at X = 8.16?
# Center of hub cylinder in Y'Z':
# Y' = -1.351, Z' = 27.583.
# Radius = 2.10.
# Lowest point of hub cylinder at X = 8.16 is Y' = -1.351, Z' = 27.583 - 2.10 = 25.483!
# And the top of the strut was at Z' = 25.003!
# Distance in Z' should be 25.483 - 25.003 = 0.48 mm!
# Why did query return 2.166?
# Ah! Let's check hub.vertices vs surface mesh!
# Cylinder vertices: does trimesh cylinder have vertices on the lowest line of the cylinder?
# A cylinder with 32 sections: vertices are at angles 2*pi*k/32!
# Let's check!
p_test = np.array([8.16, -1.351, 25.003])
print("Distance from (8.16, -1.351, 25.003) to hub vertices:", np.min(np.linalg.norm(hub.vertices - p_test, axis=1)))
# What is closest point on hub surface (using trimesh proximity)?
prox = trimesh.proximity.ProximityQuery(hub)
d_surf, pt_surf = prox.vertex([p_test])
print("Distance to hub surface:", d_surf[0], "closest point on surface:", pt_surf[0])
