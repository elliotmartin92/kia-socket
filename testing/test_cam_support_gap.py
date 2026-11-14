import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part
from build_shaft import build_shaft_rocker_mesh

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

# Let's inspect the cam underside points in tilted coords
prox = trimesh.proximity.ProximityQuery(shaft_t)

# Original support:
# Y' = -3.50 -> Z' = 18.685
# Y' = -2.33 -> Z' = 17.800
# Y' = -1.20 -> Z' = 19.103

for d_z in [0.00, -0.05, -0.10, -0.12, -0.15]:
    z_fork_base = 16.00
    pts_tine_yz = [
        (-3.50, z_fork_base),
        (-3.50, 18.685 + d_z),
        (-2.33, 17.800 + d_z),
        (-1.20, 19.103 + d_z),
        (-1.20, z_fork_base),
    ]
    poly_head_yz = Polygon(pts_tine_yz)
    tine_w = 0.55
    m_l_2d = trimesh.creation.extrude_polygon(poly_head_yz, height=tine_w)
    vl = m_l_2d.vertices.copy()
    vl_3d = np.column_stack([vl[:, 2] + 5.65, vl[:, 0], vl[:, 1]])
    tine_l = trimesh.Trimesh(vertices=vl_3d, faces=m_l_2d.faces.copy(), process=True)
    
    top_v = tine_l.vertices[tine_l.vertices[:, 2] > 17.0]
    gaps = -prox.signed_distance(top_v)
    print(f"d_z = {d_z:.2f} mm -> Min gap: {gaps.min():.4f} mm, Mean gap: {gaps.mean():.4f} mm, Max gap: {gaps.max():.4f} mm")
