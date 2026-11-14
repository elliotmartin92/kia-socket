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

# Check what base_mesh has at X = 10.284 for Y in [7.0, 12.0], Z in [0.60, 16.0]
for y in np.linspace(7.0, 12.0, 11):
    ray_origin = np.array([[10.284, y, 0.60]])
    ray_dir = np.array([[0, 0, 1.0]])
    locs, _, _ = m_t.ray.intersects_location(ray_origin, ray_dir)
    if len(locs) > 0:
        print(f"Y={y:.1f}: hits base part at Z = {locs[:, 2].tolist()}")
    else:
        print(f"Y={y:.1f}: completely clear!")
