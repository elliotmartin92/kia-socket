import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from build_shaft import build_shaft_rocker_mesh

base_mesh, base_poly = build_part.build_exact_3d_model()
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)

R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

# Plunger blade is at X = 10.284. Let's sample along X = 9.0 (left tine) and X = 11.5 (right tine)
y_vals = np.linspace(6.0, 12.5, 27)

print("Plunger underside profile at X = 10.284:")
for y in y_vals:
    ray_origin = np.array([[10.284, y, 0.0]])
    ray_dir = np.array([[0, 0, 1.0]])
    locs, _, _ = shaft_t.ray.intersects_location(ray_origin, ray_dir)
    if len(locs) > 0:
        # Lowest point on shaft
        z_hit = locs[:, 2].min()
        print(f"  Y = {y:.2f} -> Z = {z_hit:.3f}")
    else:
        print(f"  Y = {y:.2f} -> No hit")
