"""
Test new clip parameters and 3-prong anti-sag support design.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT,
    CLIP_CROWN_EASE, CLIP_BLUNT_HEIGHT
)

# New parameters
CLIP_SHELF_Z_BY_ANGLE = {
    45.0: 3.97,   # Top right: lowered 0.75mm (closes SIM tool gap)
    135.0: 3.97,  # Top left:  lowered 0.75mm (closes SIM tool gap)
    211.3: 4.35,  # Bottom left: lowered 0.37mm (closes half-SIM gap)
    327.5: 4.35,  # Bottom right: lowered 0.37mm (closes half-SIM gap)
}

CLIP_HOOK_DEPTH_BY_ANGLE = {
    45.0: 1.80,
    135.0: 1.80,
    211.3: 1.80,
    327.5: 1.85,  # User-calibrated 1.85mm adequate for full retention
}

def build_test_supports(base_poly):
    half_w = CLIP_ARM_WIDTH / 2.0           # 2.10 mm
    clip_release_gap = 0.23                 # 0.23mm tuned release gap for PC-FR
    bottom_clip_angles = [211.3, 327.5]
    
    # 3-prong layout: Left, Center, Right
    prongs_spec = [
        (-1.25, 0.80), # (tangential offset, width)
        ( 0.00, 0.90), # Center prong directly under apex!
        ( 1.25, 0.80)
    ]
    
    support_meshes = []
    
    for angle_deg in bottom_clip_angles:
        stem_h = CLIP_SHELF_Z_BY_ANGLE[angle_deg]
        hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE[angle_deg]
        z_shelf_contact = stem_h - clip_release_gap
        z_stem = stem_h - hook_depth
        rad = math.radians(angle_deg)
        u_r = np.array([math.cos(rad), math.sin(rad)])
        u_t = np.array([-math.sin(rad), math.cos(rad)])
        p, _, _ = find_boundary_point_and_normal(base_poly, angle_deg)
        
        prongs = []
        for yo, pw in prongs_spec:
            eff_depth = hook_depth - CLIP_CROWN_EASE * ((abs(yo) / half_w) ** 2.0)
            pts_rz = [
                (-0.25, z_stem - 0.35),               # root inside stem wall (0.60mm vertical neck)
                (-0.25, z_stem + 0.25),               # root inside stem wall
                (0.00,  z_stem + 0.25),               # stem outer face (top of neck)
                (eff_depth - 0.55, z_shelf_contact),  # shelf contact start with release gap
                (eff_depth, z_shelf_contact),         # shelf contact end (outer edge)
                (eff_depth, z_shelf_contact - 0.25),  # outer chamfer
                (0.00,  z_stem - 0.35),               # stem outer face (bottom of neck)
            ]
            poly_rz = Polygon(pts_rz)
            m2d = trimesh.creation.extrude_polygon(poly_rz, height=pw)
            v = m2d.vertices.copy()
            v_local = np.column_stack([v[:, 0], v[:, 2] - pw/2.0 + yo, v[:, 1]])
            m_p = trimesh.Trimesh(vertices=v_local, faces=m2d.faces.copy(), process=True)
            if m_p.volume < 0:
                m_p.faces = np.fliplr(m_p.faces)
            prongs.append(m_p)
            
        m_group = trimesh.util.concatenate(prongs)
        M = np.eye(4)
        M[:3, 0] = [u_r[0], u_r[1], 0]
        M[:3, 1] = [u_t[0], u_t[1], 0]
        M[:3, 2] = [0, 0, 1]
        M[:3, 3] = [p[0], p[1], 0]
        m_group.apply_transform(M)
        support_meshes.append(m_group)
        
    return trimesh.util.concatenate(support_meshes)

def test_run():
    base_poly, outer_poly, _ = get_exact_base_polygon()
    supp = build_test_supports(base_poly)
    print(f"Generated support mesh successfully! Volume = {supp.volume:.2f} mm^3, is_watertight = {supp.is_watertight}")
    comps = supp.split()
    print(f"Total separate prong bodies = {len(comps)} (expected 6: 3 per clip)")
    for i, c in enumerate(comps):
        print(f"  Prong {i+1}: Centroid = {c.centroid}, Volume = {c.volume:.3f} mm^3, bounds Z = [{c.bounds[0,2]:.2f}, {c.bounds[1,2]:.2f}]")

if __name__ == '__main__':
    test_run()
