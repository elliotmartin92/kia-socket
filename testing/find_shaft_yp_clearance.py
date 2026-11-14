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

print("Shaft underside across Y' at X = 8.5, 9.8, 11.3:")
for yp in np.linspace(-1.8, -0.9, 10):
    hits = []
    for x in [8.5, 9.8, 11.3]:
        ray_origin = np.array([[x, yp, 15.0]])
        ray_dir = np.array([[0, 0, 1.0]])
        locs, _, _ = shaft_t.ray.intersects_location(ray_origin, ray_dir)
        if len(locs) > 0:
            hits.append(f"X={x}: Z={locs[:, 2].min():.3f}")
        else:
            hits.append(f"X={x}: None")
    print(f"  Y' = {yp:.2f} -> {', '.join(hits)}")
