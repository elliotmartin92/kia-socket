"""
testing/test_thin_clip_supports.py
Models thin, easily removable 45-degree breakaway supports for the bottom clips (211.3° and 327.5°):
- They do NOT fill the entire underside.
- They are thin slender struts (0.50mm beam thickness x 0.60mm tangential width).
- Twin prongs at lateral edges (t = +/- 1.30mm) prevent sagging of the 4.20mm wide clip.
- Micro-chisel contact tips (0.20mm x 0.50mm) under the shelf for crisp 1-click snap-off.
- Thin neck at the stem for clean breakaway without scarring the stem.
- Flat retention shelf on the clip remains 100% horizontal at Z = 4.97mm.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_part as bp

def build_thin_45deg_clip_supports(base_poly):
    """
    Builds thin, easily removable 45° breakaway support struts for bottom clips.
    """
    stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT  # 4.97 mm
    bottom_clip_angles = [211.3, 327.5]
    
    support_meshes = []
    
    for angle_deg in bottom_clip_angles:
        p, norm, tang = bp.find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, bp.CLIP_HOOK_DEPTH)
        
        # 45-degree angle: rise = run = hook_depth
        z_stem_start = stem_h - hook_depth
        
        # Slender strut dimensions:
        # Beam thickness in normal direction = 0.50mm
        # Tangential width = 0.60mm per prong
        # Twin prongs at t = +/- 1.30mm (leaving 2.0mm open center space)
        prong_w = 0.60
        prong_offsets = [-1.30, 1.30]
        
        # 2D cross-section of slender 45° angled strut in (radial X, vertical Z):
        # 1. Base at stem: attaches at (0, z_stem_start) with a narrow 0.35mm neck:
        #    from Z = z_stem_start - 0.35 to Z = z_stem_start
        # 2. Rises along 45°: top edge goes from (0, z_stem_start) to (hook_depth, stem_h)
        #    bottom edge goes from (0, z_stem_start - 0.35) to (hook_depth - 0.15, stem_h - 0.50)
        # 3. Tip under shelf: narrow chisel contact at (hook_depth, stem_h)
        pts_rz = [
            (0.0, z_stem_start - 0.35),
            (hook_depth - 0.20, stem_h - 0.45),
            (hook_depth, stem_h - 0.05),
            (hook_depth - 0.25, stem_h - 0.05),
            (0.0, z_stem_start)
        ]
        poly_rz = Polygon(pts_rz)
        
        prong_meshes = []
        for yo in prong_offsets:
            m_prong_2d = trimesh.creation.extrude_polygon(poly_rz, height=prong_w)
            v = m_prong_2d.vertices.copy()
            v_reorient = np.column_stack([v[:, 0], v[:, 2] - prong_w/2.0 + yo, v[:, 1]])
            m_prong = trimesh.Trimesh(vertices=v_reorient, faces=m_prong_2d.faces.copy(), process=True)
            if m_prong.volume < 0:
                m_prong.faces = np.fliplr(m_prong.faces)
            prong_meshes.append(m_prong)
            
        m_combined_local = trimesh.util.concatenate(prong_meshes)
        
        # Transform local to global baseplate coords:
        # X_local along n_dir, Y_local along tang, Z_local along +Z
        M = np.eye(4)
        M[:3, 0] = [n_dir[0], n_dir[1], 0]
        M[:3, 1] = [tang[0], tang[1], 0]
        M[:3, 2] = [0, 0, 1]
        M[:3, 3] = [p[0], p[1], 0]
        
        m_combined_local.apply_transform(M)
        support_meshes.append(m_combined_local)
        
    return trimesh.util.concatenate(support_meshes)

if __name__ == '__main__':
    base_poly, _, _ = bp.get_exact_base_polygon()
    supp = build_thin_45deg_clip_supports(base_poly)
    print(f"Thin supports watertight: {supp.is_watertight}")
    print(f"Thin supports volume: {supp.volume:.3f} mm³")
    print(f"Thin supports bounds: {supp.bounds}")
    
    # Also render together with the clip mesh
    # Re-build original clip without permanent gusset:
    # Set CLIP_HOOK_DEPTH back to standard shelf
    bp.CLIP_ANGLES = [211.3]
    part_mesh, _ = bp.build_exact_3d_model()
    
    fig = plt.figure(figsize=(14, 7), dpi=180)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    
    p211, _, _ = bp.find_boundary_point_and_normal(base_poly, 211.3)
    
    # Submesh of clip
    dists = np.linalg.norm(part_mesh.vertices[:, :2] - p211, axis=1)
    mask = dists < 4.5
    faces_mask = np.all(mask[part_mesh.faces], axis=1)
    sub_clip = trimesh.Trimesh(vertices=part_mesh.vertices, faces=part_mesh.faces[faces_mask])
    
    # Plot View 1: Looking from outside
    v_c = sub_clip.vertices
    f_c = sub_clip.faces
    col_c = Poly3DCollection(v_c[f_c], alpha=0.85, facecolor='#b0bec5', edgecolor='#455a64', lw=0.3)
    ax1.add_collection3d(col_c)
    
    v_s = supp.vertices
    f_s = supp.faces
    col_s = Poly3DCollection(v_s[f_s], alpha=0.95, facecolor='#e91e63', edgecolor='#880e4f', lw=0.5)
    ax1.add_collection3d(col_s)
    
    ax1.set_xlim(p211[0] - 3.5, p211[0] + 3.5)
    ax1.set_ylim(p211[1] - 3.5, p211[1] + 3.5)
    ax1.set_zlim(1.0, 7.5)
    ax1.set_title("Front-Side View: Thin Removable 45° Support Struts\n(Preserves Horizontal Retention Shelf, Easily Snaps Off)", fontsize=10, fontweight='bold')
    ax1.set_xlabel("X (mm)")
    ax1.set_ylabel("Y (mm)")
    ax1.set_zlabel("Z (mm)")
    ax1.view_init(elev=20, azim=40)
    
    # Plot View 2: Looking upward from underneath the shelf
    col_c2 = Poly3DCollection(v_c[f_c], alpha=0.85, facecolor='#b0bec5', edgecolor='#455a64', lw=0.3)
    ax2.add_collection3d(col_c2)
    col_s2 = Poly3DCollection(v_s[f_s], alpha=0.95, facecolor='#e91e63', edgecolor='#880e4f', lw=0.5)
    ax2.add_collection3d(col_s2)
    ax2.set_xlim(p211[0] - 3.5, p211[0] + 3.5)
    ax2.set_ylim(p211[1] - 3.5, p211[1] + 3.5)
    ax2.set_zlim(1.0, 7.5)
    ax2.set_title("Underside View: Slender Twin Prongs (0.60mm W x 0.50mm T)\n(Open 2.0mm Center Space, 100% Removable with Pliers)", fontsize=10, fontweight='bold')
    ax2.set_xlabel("X (mm)")
    ax2.set_ylabel("Y (mm)")
    ax2.set_zlabel("Z (mm)")
    ax2.view_init(elev=-25, azim=45)
    
    plt.tight_layout()
    out_png = 'testing/thin_clip_support_inspection.png'
    plt.savefig(out_png, dpi=180)
    print(f"Saved {out_png}")
