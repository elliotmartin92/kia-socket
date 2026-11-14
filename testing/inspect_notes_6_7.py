import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from build_shaft import build_shaft_rocker_mesh

mesh = trimesh.load('part.stl')

notes = [
    {"id": 6, "at": [10.5003, 11.4189, 15.6378], "desc": "Note 6"},
    {"id": 7, "at": [9.76224, -2.20633, 25.6702], "desc": "Note 7"},
]

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

for n in notes:
    pt = np.array(n["at"])
    print(f"\n=== {n['desc']} (id {n['id']}): {n['at']} ===")
    
    # Distance to base part vs shaft
    d_base = np.min(np.linalg.norm(m_t.vertices - np.array([0, 0, -z_min]) - pt, axis=1)) # wait, m_t was not translated yet
    # let's properly translate m_t
    m_t_trans = m_t.copy()
    m_t_trans.apply_translation([0, 0, -z_min])
    
    d_base = np.min(np.linalg.norm(m_t_trans.vertices - pt, axis=1))
    d_shaft = np.min(np.linalg.norm(shaft_t.vertices - pt, axis=1))
    
    print(f"Dist to base part: {d_base:.3f} mm")
    print(f"Dist to shaft: {d_shaft:.3f} mm")
    
    # Untilted flat coords
    p_tilted_no_trans = pt + np.array([0, 0, z_min])
    p_flat = np.linalg.inv(R[:3, :3]) @ p_tilted_no_trans
    print(f"Flat coords: {p_flat.round(3).tolist()}")
