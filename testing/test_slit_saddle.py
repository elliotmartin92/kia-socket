import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

def build_test_saddle():
    cx_left, cx_right = -7.853, 8.453
    gap = 0.18  # 0.18mm release gap for PC-FR
    
    # Rear slope: from Y = -11.40, Z = 3.20 down to Y = -9.42, Z = 0.20
    # Front slope: from Y = -9.42, Z = 0.20 up to Y = -7.80, Z = 1.82
    
    # Support top profile:
    # At Y = -11.40: Z = 3.20 - gap = 3.02
    # At Y = -9.42:  Z = 0.20 - gap = 0.02 -> sits on bed at Z = 0
    # At Y = -7.80:  Z = 1.82 - gap = 1.64
    
    pts_yz = [
        (-11.50, 0.00),         # bed anchor back
        (-7.60,  0.00),         # bed anchor front
        (-7.60,  1.64),         # front slope top
        (-9.42,  0.05),         # V-notch trough (clearing tip by 0.15mm)
        (-11.40, 3.02),         # rear slope top
        (-11.50, 3.02),         # back vertical
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

saddle = build_test_saddle()
print(f"Saddle bounds: {saddle.bounds.tolist()}, volume: {saddle.volume:.2f} mm^3")
