import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part
from build_shaft import build_shaft_rocker_mesh

def build_test_plunger_cradle():
    # Blade is at X in [8.484, 12.084] (center 10.284)
    # Tines at X in [8.484, 9.284] and [11.284, 12.084]
    p_x_c = 10.284
    gap = 0.20  # 0.20mm release gap
    
    # 2D profile in Y-Z plane for each tine
    # Plunger underside:
    # Y = 7.50 -> Z_blade = 19.014 -> Z_top = 18.814
    # Y = 10.75 -> Z_blade = 15.794 -> Z_top = 15.594
    # Y = 11.30 -> Z_blade = 15.632 -> Z_top = 15.432
    # Y = 12.10 -> Z_blade = 16.000 -> Z_top = 15.800
    
    pts_tine_yz = [
        (8.50, 0.60),           # bed anchor back
        (12.10, 0.60),          # bed anchor front
        (12.10, 15.80),         # front tip top
        (11.30, 15.432),        # bottom apex
        (10.75, 15.594),        # blend point
        (7.50,  18.814),        # top slope end
        (7.50,  14.00),         # back drop
        (8.50,  14.00),         # back transition
    ]
    poly_tine_yz = Polygon(pts_tine_yz)
    
    # We extrude two tines in X:
    # Left tine: [8.484, 9.284] (width 0.80)
    # Right tine: [11.284, 12.084] (width 0.80)
    # And a central stabilizing cross-brace / web at the bottom (Z in [0.60, 12.0])
    # across X in [9.284, 11.284]
    
    tine_w = 0.80
    m_l_2d = trimesh.creation.extrude_polygon(poly_tine_yz, height=tine_w)
    vl = m_l_2d.vertices.copy()
    vl_3d = np.column_stack([vl[:, 2] + 8.484, vl[:, 0], vl[:, 1]])
    tine_l = trimesh.Trimesh(vertices=vl_3d, faces=m_l_2d.faces.copy(), process=True)
    if tine_l.volume < 0:
        tine_l.faces = np.fliplr(tine_l.faces)
        
    m_r_2d = trimesh.creation.extrude_polygon(poly_tine_yz, height=tine_w)
    vr = m_r_2d.vertices.copy()
    vr_3d = np.column_stack([vr[:, 2] + 11.284, vr[:, 0], vr[:, 1]])
    tine_r = trimesh.Trimesh(vertices=vr_3d, faces=m_r_2d.faces.copy(), process=True)
    if tine_r.volume < 0:
        tine_r.faces = np.fliplr(tine_r.faces)
        
    # Central web connecting them below Z = 12.0
    pts_web_yz = [
        (8.50, 0.60),
        (12.10, 0.60),
        (12.10, 12.00),
        (8.50, 12.00)
    ]
    poly_web_yz = Polygon(pts_web_yz)
    web_w = 11.284 - 9.284  # 2.00mm
    m_w_2d = trimesh.creation.extrude_polygon(poly_web_yz, height=web_w)
    vw = m_w_2d.vertices.copy()
    vw_3d = np.column_stack([vw[:, 2] + 9.284, vw[:, 0], vw[:, 1]])
    web_center = trimesh.Trimesh(vertices=vw_3d, faces=m_w_2d.faces.copy(), process=True)
    if web_center.volume < 0:
        web_center.faces = np.fliplr(web_center.faces)
        
    cradle = trimesh.util.concatenate([tine_l, tine_r, web_center])
    return cradle

base_mesh, base_poly = build_part.build_exact_3d_model()
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

cradle = build_test_plunger_cradle()
print(f"Cradle bounds: {cradle.bounds.tolist()}, volume: {cradle.volume:.2f} mm^3")

# Check clearance to shaft
prox_shaft = trimesh.proximity.ProximityQuery(shaft_t)
dist_shaft = prox_shaft.signed_distance(cradle.vertices)
print(f"Max penetration into shaft: {dist_shaft.max():.4f} mm (must be <= 0.0)")

top_cradle = cradle.vertices[cradle.vertices[:, 2] > 14.5]
gap_to_shaft = -prox_shaft.signed_distance(top_cradle)
print(f"Min gap to shaft: {gap_to_shaft.min():.4f} mm")
print(f"Max gap to shaft at support face: {gap_to_shaft.max():.4f} mm")
print(f"Mean gap to shaft: {gap_to_shaft.mean():.4f} mm")

# Check clearance to base part
prox_base = trimesh.proximity.ProximityQuery(m_t)
dist_base = prox_base.signed_distance(cradle.vertices)
print(f"Max penetration into base part: {dist_base.max():.4f} mm (must be <= 0.0)")
print(f"Min clearance to base part: {-dist_base.max():.4f} mm")
