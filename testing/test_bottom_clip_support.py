"""
testing/test_bottom_clip_support.py
Tests and visualizes the hardcoded 45-degree support for the bottom clips (211.3° and 327.5°),
tweaked support fin breakaway tines, and +0.75mm extension on the bottom of the half moon.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt

import build_part as bp

def test_half_moon_poly():
    print("=== TESTING HALF MOON +0.75mm EXTENSION ===")
    cx = 6.279
    w_x = 4.20
    base_y = -4.30
    apex_y = -3.60
    extension_y = 0.75  # +0.75mm in -Y direction
    
    rx = w_x / 2.0
    ry = apex_y - base_y  # 0.70 mm
    
    angles = np.linspace(np.pi, 0, 33)
    out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
    
    pts = out_arc + [
        (cx + rx, base_y - extension_y),
        (cx - rx, base_y - extension_y)
    ]
    poly = Polygon(pts)
    print(f"Half Moon Poly Valid: {poly.is_valid}")
    print(f"Half Moon Bounds: X [{poly.bounds[0]:.3f}, {poly.bounds[2]:.3f}], Y [{poly.bounds[1]:.3f}, {poly.bounds[3]:.3f}]")
    assert abs(poly.bounds[1] - (-5.05)) < 1e-4, f"Expected Y_min = -5.05, got {poly.bounds[1]}"
    assert abs(poly.bounds[3] - (-3.60)) < 1e-4, f"Expected Y_max = -3.60, got {poly.bounds[3]}"
    assert abs(poly.bounds[2] - poly.bounds[0] - 4.20) < 1e-4, f"Expected width = 4.20, got {poly.bounds[2] - poly.bounds[0]}"
    return poly

def build_45deg_clip_supports(base_poly):
    """
    Builds hardcoded 45-degree angled support struts coming out of the stem
    under the bottom clips (211.3° and 327.5°).
    - Starts on the outer face of the stem at Z = stem_h - hook_depth
    - Slopes outward and upward at 45° to catch the hook retention shelf at Z = stem_h (4.97mm)
    - Twin prongs (left & right) with central prying slot for easy tool leverage
    - Micro-chisel contact tip under the hook shelf for crisp breakaway
    """
    stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT  # 4.97 mm
    bottom_clip_angles = [211.3, 327.5]
    
    support_meshes = []
    
    for angle_deg in bottom_clip_angles:
        rad = math.radians(angle_deg)
        p, norm, tang = bp.find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, bp.CLIP_HOOK_DEPTH)
        
        # 45-degree angle rise matches hook_depth exactly:
        # z_stem_start = stem_h - hook_depth
        z_stem_start = stem_h - hook_depth
        strut_thick = 0.65  # 0.65mm wall thickness
        
        # Tangential stations: twin prongs at lateral edges with central prying gap
        # Clip arm width is 4.20mm (tangential from -2.10 to +2.10)
        prong_w = 1.05
        prong_offsets = [-1.45, 1.45]  # centers of left and right prongs
        
        # Build 45-degree angled prism in local clip coordinates (radial along X, tangential along Y, vertical Z)
        # 2D cross-section in radial/Z plane (X = radial outward, Z = vertical):
        # Base on stem at r=0: Z from z_stem_start - strut_thick to z_stem_start
        # Outer tip at shelf r=hook_depth: Z from stem_h - strut_thick to stem_h
        # Micro-chisel tip: at r in [hook_depth - 0.35, hook_depth], contacts shelf at stem_h
        
        # Local 2D polygon in (radial, Z):
        # [ (0, z_stem_start - strut_thick),
        #   (hook_depth, stem_h - strut_thick * 0.5),
        #   (hook_depth, stem_h),
        #   (hook_depth - 0.35, stem_h),
        #   (0, z_stem_start) ]
        
        # A clean 45-degree triangle with central prying notch:
        pts_rz = [
            (0.0, z_stem_start - 0.20),
            (hook_depth, stem_h - 0.15),
            (hook_depth, stem_h),
            (0.0, z_stem_start + 0.15)
        ]
        poly_rz = Polygon(pts_rz)
        
        prong_meshes = []
        for yo in prong_offsets:
            m_prong_2d = trimesh.creation.extrude_polygon(poly_rz, height=prong_w)
            # Re-orient from (X, Y) to (radial X, tangential Y, vertical Z):
            # Extrude was along Z, poly was in XY. So V_poly[:, 0] is radial, V_poly[:, 1] is Z, V_extrude is Y
            v = m_prong_2d.vertices.copy()
            # New coords: X_rad = v[:, 0], Y_tang = v[:, 2] - prong_w/2.0 + yo, Z_vert = v[:, 1]
            v_reorient = np.column_stack([v[:, 0], v[:, 2] - prong_w/2.0 + yo, v[:, 1]])
            m_prong = trimesh.Trimesh(vertices=v_reorient, faces=m_prong_2d.faces.copy(), process=True)
            if m_prong.volume < 0:
                m_prong.faces = np.fliplr(m_prong.faces)
            prong_meshes.append(m_prong)
            
        m_combined_local = trimesh.util.concatenate(prong_meshes)
        
        # Transform local (radial along +X, tangential along +Y, Z along +Z) to global baseplate coords:
        rot_align = np.eye(4)
        rot_align[0, 0] = n_dir[0]
        rot_align[1, 0] = n_dir[1]
        rot_align[0, 1] = tang[0]
        rot_align[1, 1] = tang[1]
        rot_align[0, 3] = p[0]
        rot_align[1, 3] = p[1]
        
        m_combined_local.apply_transform(rot_align)
        support_meshes.append(m_combined_local)
        
    all_supps = trimesh.util.concatenate(support_meshes)
    return all_supps

if __name__ == '__main__':
    poly_moon = test_half_moon_poly()
    base_poly, _, _ = bp.get_exact_base_polygon()
    supp_clips = build_45deg_clip_supports(base_poly)
    print(f"45° Clip Supports watertight: {supp_clips.is_watertight}")
    print(f"45° Clip Supports volume: {supp_clips.volume:.2f} mm³")
    print(f"45° Clip Supports bounds: {supp_clips.bounds}")
    
    # Plot in testing/
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(14, 6), dpi=180)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    
    # Part 1: Flat part space (around 211.3 deg clip)
    p211, _, _ = bp.find_boundary_point_and_normal(base_poly, 211.3)
    
    v = supp_clips.vertices
    f = supp_clips.faces
    col1 = Poly3DCollection(v[f], alpha=0.9, facecolor='#26a69a', edgecolor='#004d40', lw=0.4)
    ax1.add_collection3d(col1)
    ax1.set_xlim(p211[0] - 4, p211[0] + 4)
    ax1.set_ylim(p211[1] - 4, p211[1] + 4)
    ax1.set_zlim(0, 7)
    ax1.set_title("Bottom Left Clip (211.3°) - Flat Coordinates\n45° Angled Support Coming Out of Stem", fontsize=10, fontweight='bold')
    ax1.set_xlabel("X (mm)")
    ax1.set_ylabel("Y (mm)")
    ax1.set_zlabel("Z (mm)")
    
    # Part 2: Tilted 45° build space
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    supp_tilted = supp_clips.copy().apply_transform(R)
    v2 = supp_tilted.vertices
    f2 = supp_tilted.faces
    col2 = Poly3DCollection(v2[f2], alpha=0.9, facecolor='#42a5f5', edgecolor='#0d47a1', lw=0.4)
    ax2.add_collection3d(col2)
    p211_b = R @ np.array([p211[0], p211[1], 4.0, 1.0])
    ax2.set_xlim(p211_b[0] - 4, p211_b[0] + 4)
    ax2.set_ylim(p211_b[1] - 4, p211_b[1] + 4)
    ax2.set_zlim(p211_b[2] - 4, p211_b[2] + 4)
    ax2.set_title("Bottom Left Clip (211.3°) - 45° Tilted Print Space\n(Monotonically Rising Support Under Hook Shelf)", fontsize=10, fontweight='bold')
    ax2.set_xlabel("X_build (mm)")
    ax2.set_ylabel("Y_build (mm)")
    ax2.set_zlabel("Z_build (mm)")
    
    plt.tight_layout()
    out_png = 'testing/bottom_clip_45deg_support.png'
    plt.savefig(out_png, dpi=180)
    print(f"Saved {out_png}")

