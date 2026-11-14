import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from build_shaft import build_shaft_rocker_mesh

shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
base_mesh, _ = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

print("Shaft underside at X = 9.762 across Y' in [-3.5, -0.5]:")
for yp in np.linspace(-3.5, -0.5, 31):
    ray_origin = np.array([[9.762, yp, 15.0]])
    ray_dir = np.array([[0, 0, 1.0]])
    locs, _, _ = shaft_t.ray.intersects_location(ray_origin, ray_dir)
    if len(locs) > 0:
        z_min_hit = locs[:, 2].min()
        print(f"  Y' = {yp:.2f} -> Z' = {z_min_hit:.3f}")
    else:
        print(f"  Y' = {yp:.2f} -> No hit")
