import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part
from build_shaft import build_shaft_rocker_mesh

# Let's inspect the underside of the shaft rocker around Y' = -1.35 across X in [8.0, 12.0]
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

# Sample underside profile at Y' = -1.35 across X in [8.0, 12.0]
print("Shaft underside at Y' = -1.35:")
for x in np.linspace(8.0, 12.0, 17):
    ray_origin = np.array([[x, -1.35, 15.0]])
    ray_dir = np.array([[0, 0, 1.0]])
    locs, _, _ = shaft_t.ray.intersects_location(ray_origin, ray_dir)
    if len(locs) > 0:
        print(f"  X = {x:.2f} -> Z = {locs[:, 2].min():.3f}")
    else:
        print(f"  X = {x:.2f} -> No hit")
