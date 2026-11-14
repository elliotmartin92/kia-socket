import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part

def build_calibrated_saddle():
    cx_left, cx_right = -7.853, 8.453
    gap = 0.18  # 0.18mm release gap
    
    # Profile points in Y-Z plane
    pts_yz = [
        (-11.50, 0.00),                 # bed anchor back
        (-7.50,  0.00),                 # bed anchor front
        (-7.50,  1.936),                # front top (Z_part 2.116 - 0.18)
        (-9.20,  0.236),                # front bottom
        (-9.40,  0.05),                 # trough clearance
        (-9.60,  0.134),                # rear bottom
        (-11.50, 1.342),                # rear top (Z_part 1.522 - 0.18)
    ]
    poly_yz = Polygon(pts_yz)
    
    strut_w = 0.90
    offsets = [-1.15, 1.15]
    
    prongs = []
    for cx in [cx_left, cx_right]:
        for xo in offsets:
            m2d = trimesh.creation.extrude_polygon(poly_yz, height=strut_w)
            v = m2d.vertices.copy()
            v_3d = np.column_stack([v[:, 2] - strut_w/2.0 + cx + xo, v[:, 0], v[:, 1]])
            m_p = trimesh.Trimesh(vertices=v_3d, faces=m2d.faces.copy(), process=True)
            if m_p.volume < 0:
                m_p.faces = np.fliplr(m_p.faces)
            prongs.append(m_p)
            
    return trimesh.util.concatenate(prongs)

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

saddle = build_calibrated_saddle()
proximity = trimesh.proximity.ProximityQuery(m_t)
dist = proximity.signed_distance(saddle.vertices)
print(f"Max penetration: {dist.max():.4f} (<= 0.0 means 0 penetration)")
# Find minimum positive distance among all top vertices
top_verts = saddle.vertices[saddle.vertices[:, 2] > 0.1]
dist_top = -proximity.signed_distance(top_verts)
print(f"Min clearance gap at top surfaces: {dist_top.min():.4f} mm")
print(f"Max clearance gap at top surfaces: {dist_top.max():.4f} mm")
print(f"Mean clearance gap at top surfaces: {dist_top.mean():.4f} mm")
