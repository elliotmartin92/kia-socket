import numpy as np
import trimesh
import os, sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = base_mesh.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, return_subparts=True, with_supports=False)
p_tilted = shaft_subparts['plunger'].copy().apply_transform(R)
p_tilted.apply_translation([0, 0, -z_min])
hub_tilted = shaft_subparts['hub'].copy().apply_transform(R)
hub_tilted.apply_translation([0, 0, -z_min])
cam_tilted = shaft_subparts['cam'].copy().apply_transform(R)
cam_tilted.apply_translation([0, 0, -z_min])

# Let's inspect sections at various Z' levels:
for z in [22.0, 23.0, 24.0, 25.0, 25.5]:
    sl = p_tilted.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sl is not None:
        pts = sl.vertices
        print(f"Z'={z:4.1f}: Plunger X in [{np.min(pts[:,0]):.3f}, {np.max(pts[:,0]):.3f}], Y' in [{np.min(pts[:,1]):.3f}, {np.max(pts[:,1]):.3f}]")
    else:
        print(f"Z'={z:4.1f}: Plunger None")

print("\nCam tab sections:")
for z in [22.0, 23.0, 24.0, 25.0, 25.5]:
    sl = cam_tilted.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sl is not None:
        pts = sl.vertices
        print(f"Z'={z:4.1f}: Cam     X in [{np.min(pts[:,0]):.3f}, {np.max(pts[:,0]):.3f}], Y' in [{np.min(pts[:,1]):.3f}, {np.max(pts[:,1]):.3f}]")
    else:
        print(f"Z'={z:4.1f}: Cam None")
