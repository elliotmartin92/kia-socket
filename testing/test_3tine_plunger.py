import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part
from build_shaft import build_shaft_rocker_mesh

def test_3tine_plunger():
    pts_plunger_tine_yz = [
        (8.50, 0.60),
        (12.10, 0.60),
        (12.10, 15.80),
        (11.30, 15.432),
        (10.75, 15.594),
        (7.50,  18.814),
        (7.50,  14.00),
        (8.50,  14.00),
    ]
    poly_plunger_tine_yz = Polygon(pts_plunger_tine_yz)
    
    p_tine_w = 0.80
    m_p_l = trimesh.creation.extrude_polygon(poly_plunger_tine_yz, height=p_tine_w)
    vl = m_p_l.vertices.copy()
    vl_3d = np.column_stack([vl[:, 2] + 8.484, vl[:, 0], vl[:, 1]])
    p_tine_l = trimesh.Trimesh(vertices=vl_3d, faces=m_p_l.faces.copy(), process=True)
    if p_tine_l.volume < 0:
        p_tine_l.faces = np.fliplr(p_tine_l.faces)
        
    m_p_r = trimesh.creation.extrude_polygon(poly_plunger_tine_yz, height=p_tine_w)
    vr = m_p_r.vertices.copy()
    vr_3d = np.column_stack([vr[:, 2] + 11.284, vr[:, 0], vr[:, 1]])
    p_tine_r = trimesh.Trimesh(vertices=vr_3d, faces=m_p_r.faces.copy(), process=True)
    if p_tine_r.volume < 0:
        p_tine_r.faces = np.fliplr(p_tine_r.faces)
        
    # Center tine
    p_center_w = 0.70
    x_c_start = 10.284 - p_center_w / 2.0
    m_p_c = trimesh.creation.extrude_polygon(poly_plunger_tine_yz, height=p_center_w)
    vc = m_p_c.vertices.copy()
    vc_3d = np.column_stack([vc[:, 2] + x_c_start, vc[:, 0], vc[:, 1]])
    p_tine_c = trimesh.Trimesh(vertices=vc_3d, faces=m_p_c.faces.copy(), process=True)
    if p_tine_c.volume < 0:
        p_tine_c.faces = np.fliplr(p_tine_c.faces)
        
    # Web connecting below Z = 12.0
    pts_p_web_yz = [
        (8.50, 0.60),
        (12.10, 0.60),
        (12.10, 12.00),
        (8.50, 12.00)
    ]
    poly_p_web_yz = Polygon(pts_p_web_yz)
    p_web_w = 11.284 - 9.284
    m_pw = trimesh.creation.extrude_polygon(poly_p_web_yz, height=p_web_w)
    vw = m_pw.vertices.copy()
    vw_3d = np.column_stack([vw[:, 2] + 9.284, vw[:, 0], vw[:, 1]])
    p_web_mesh = trimesh.Trimesh(vertices=vw_3d, faces=m_pw.faces.copy(), process=True)
    if p_web_mesh.volume < 0:
        p_web_mesh.faces = np.fliplr(p_web_mesh.faces)
        
    return trimesh.util.concatenate([p_tine_l, p_tine_r, p_tine_c, p_web_mesh])

cradle = test_3tine_plunger()
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
base_mesh, _ = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

prox = trimesh.proximity.ProximityQuery(shaft_t)
dist = prox.signed_distance(cradle.vertices)
print(f"Max penetration: {dist.max():.4f} mm (must be <= 0.0)")

# Check at Note 6: [10.5003, 11.4189, 15.6378]
pt6 = np.array([10.5003, 11.4189, 15.6378])
d_pt6 = np.linalg.norm(cradle.vertices - pt6, axis=1).min()
print(f"Distance from Note 6 to cradle support: {d_pt6:.3f} mm")

# Check top faces of center tine directly below pt6
top_c_verts = p_tine_c = cradle.vertices[(cradle.vertices[:, 0] >= 9.9) & (cradle.vertices[:, 0] <= 10.7) & (cradle.vertices[:, 2] > 14.5)]
print(f"Center tine top vertices count: {len(top_c_verts)}, min Z = {top_c_verts[:, 2].min():.2f}, max Z = {top_c_verts[:, 2].max():.2f}")
