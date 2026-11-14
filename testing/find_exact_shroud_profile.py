import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

cx_right = 8.453
x_test = cx_right + 1.05  # 9.503

y_vals = np.linspace(-11.5, -7.0, 46)
z_underside = []

for y in y_vals:
    # Cast a ray straight up from Z = 0
    ray_origin = np.array([[x_test, y, 0.0]])
    ray_dir = np.array([[0, 0, 1.0]])
    locs, _, _ = m_t.ray.intersects_location(ray_origin, ray_dir)
    if len(locs) > 0:
        z_min_hit = locs[:, 2].min()
        z_underside.append((y, z_min_hit))
        print(f"Y = {y:.2f} -> Z_min = {z_min_hit:.3f}")
    else:
        print(f"Y = {y:.2f} -> No hit")
