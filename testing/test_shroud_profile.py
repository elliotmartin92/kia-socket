import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import build_part

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

cx_right = 8.453
# Let's inspect the mesh faces around cx_right in the range Y in [-12, -7], Z in [0, 4]
v = m_t.vertices
faces = m_t.faces

# Find lowest vertices of the shroud
mask = (np.abs(v[:, 0] - cx_right) <= 1.6) & (v[:, 1] >= -12.0) & (v[:, 1] <= -7.0) & (v[:, 2] <= 4.0)
v_sub = v[mask]
print(f"Right shroud vertices min Z = {v_sub[:, 2].min():.3f} at Y = {v_sub[np.argmin(v_sub[:, 2]), 1]:.3f}")

# Profile in Y-Z plane of the shroud underside at X = cx_right + 1.0 (flank)
# Let's find vertices within 0.2mm of X = cx_right + 1.0
mask_flank = (np.abs(v[:, 0] - (cx_right + 1.05)) <= 0.3) & (v[:, 1] >= -12.0) & (v[:, 1] <= -7.0) & (v[:, 2] <= 3.5)
v_flank = v[mask_flank]
sorted_flank = v_flank[np.argsort(v_flank[:, 1])]
print("Flank profile Y, Z:")
for pt in sorted_flank:
    print(f"  Y={pt[1]:.3f}, Z={pt[2]:.3f}")
