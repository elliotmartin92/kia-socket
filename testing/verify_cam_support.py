import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part
from build_shaft import build_shaft_rocker_mesh

def build_test_cam_support():
    # Floor is at Z_floor_cam = 12.190mm
    z_floor_cam = 12.190
    cam_c_x = 6.60
    
    # Stiffened neck at floor: 1.10 x 1.10mm, with 45° chamfered base
    neck_h = 2.00
    neck = trimesh.creation.box([1.10, 1.10, neck_h])
    neck.apply_translation([cam_c_x, -2.333, z_floor_cam + neck_h/2.0])
    
    # Stabilizing trunk: 1.40 x 1.40mm from Z = 14.19 to 16.00
    trunk_h = 16.00 - 14.19
    trunk = trimesh.creation.box([1.40, 1.40, trunk_h])
    trunk.apply_translation([cam_c_x, -2.333, 14.19 + trunk_h/2.0])
    
    # Head in Y-Z plane for each tine:
    # Cam underside profile:
    # Y = -3.50 -> Z_top = 18.685
    # Y = -2.33 -> Z_top = 17.800
    # Y = -1.20 -> Z_top = 19.103
    z_fork_base = 16.00
    pts_tine_yz = [
        (-3.50, z_fork_base),
        (-3.50, 18.685),
        (-2.33, 17.800),
        (-1.20, 19.103),
        (-1.20, z_fork_base),
    ]
    poly_head_yz = Polygon(pts_tine_yz)
    
    # Twin tines in X:
    # Left: [5.65, 6.20] (w = 0.55mm)
    # Right: [7.00, 7.55] (w = 0.55mm)
    tine_w = 0.55
    m_l_2d = trimesh.creation.extrude_polygon(poly_head_yz, height=tine_w)
    vl = m_l_2d.vertices.copy()
    vl_3d = np.column_stack([vl[:, 2] + 5.65, vl[:, 0], vl[:, 1]])
    tine_l = trimesh.Trimesh(vertices=vl_3d, faces=m_l_2d.faces.copy(), process=True)
    if tine_l.volume < 0:
        tine_l.faces = np.fliplr(tine_l.faces)
        
    m_r_2d = trimesh.creation.extrude_polygon(poly_head_yz, height=tine_w)
    vr = m_r_2d.vertices.copy()
    vr_3d = np.column_stack([vr[:, 2] + 7.00, vr[:, 0], vr[:, 1]])
    tine_r = trimesh.Trimesh(vertices=vr_3d, faces=m_r_2d.faces.copy(), process=True)
    if tine_r.volume < 0:
        tine_r.faces = np.fliplr(tine_r.faces)
        
    # Central web connecting tines from z_fork_base to Z = 16.80 across X in [6.20, 7.00]
    web_h = 16.80 - z_fork_base
    web_y_w = 1.40
    web = trimesh.creation.box([0.80, web_y_w, web_h])
    web.apply_translation([cam_c_x, -2.333, z_fork_base + web_h/2.0])
    
    return trimesh.util.concatenate([neck, trunk, tine_l, tine_r, web])

base_mesh, base_poly = build_part.build_exact_3d_model()
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

cam_supp = build_test_cam_support()
print(f"Cam support bounds: {cam_supp.bounds.tolist()}, volume: {cam_supp.volume:.2f} mm^3")

prox_shaft = trimesh.proximity.ProximityQuery(shaft_t)
dist_shaft = prox_shaft.signed_distance(cam_supp.vertices)
print(f"Max penetration into shaft: {dist_shaft.max():.4f} mm (must be <= 0.0)")

top_verts = cam_supp.vertices[cam_supp.vertices[:, 2] > 17.5]
gap_to_shaft = -prox_shaft.signed_distance(top_verts)
print(f"Min gap to shaft at support face: {gap_to_shaft.min():.4f} mm")
print(f"Max gap to shaft at support face: {gap_to_shaft.max():.4f} mm")
print(f"Mean gap to shaft at support face: {gap_to_shaft.mean():.4f} mm")
