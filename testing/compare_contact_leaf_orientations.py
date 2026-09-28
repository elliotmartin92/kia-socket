"""
testing/compare_contact_leaf_orientations.py
Renders candidate orientations for the contact leaves with the S-curve completely under the floor:
- Orientation A: Leaves pinching in Y (Front & Back prongs, transverse slot in X)
- Orientation B: Leaves pinching in X (Left & Right prongs, longitudinal slot in Y)
- Orientation C: Leaves forming flat horizontal wiping jaws matching photo_with_grid.png
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, extrude_shapely_geom, BASE_THICK
from build_shaft import build_shaft_rocker_mesh
from generate_print_assembly_guide import render_unified_panel

def build_option_a_mesh(is_hot=True):
    """Option A: Leaves pinch in Y (Front/Back), opening along X. S-curve hidden under floor."""
    xc = 6.28 if is_hot else -6.28
    slit_x = 8.453 if is_hot else -7.853
    # 2D cross section in Y-Z
    y_center = 1.45
    t_half = 0.25
    front_pts = [(-1.05, 1.0), (-1.05, 5.2), (0.95, 9.4), (-0.70, 14.5)]
    rear_pts  = [(3.95, 1.0), (3.95, 5.2), (1.95, 9.4), (3.60, 14.5)]
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    b_pts = [(front_pts[0][0] - t_half, 1.0), (rear_pts[0][0] + t_half, 1.0),
             (rear_pts[0][0] + t_half, 1.5), (front_pts[0][0] - t_half, 1.5)]
    brass_2d = Polygon(f_poly_pts).union(Polygon(r_poly_pts)).union(Polygon(b_pts))
    w_clip = 6.0
    m_clip = extrude_shapely_geom(brass_2d, height=w_clip)
    v = m_clip.vertices.copy()
    v_new = np.zeros_like(v)
    v_new[:, 0] = v[:, 2] - w_clip / 2.0
    v_new[:, 1] = v[:, 0]
    v_new[:, 2] = v[:, 1]
    m_clip.vertices = v_new
    
    # Terminal blade UNDER the floor (Z in [-5.5, 0.0])
    p_blade = Polygon([(-15.2, -5.5), (-12.1, -5.5), (-12.1, 0.5), (-15.2, 0.5)])
    m_blade = extrude_shapely_geom(p_blade, height=0.77)
    vb = m_blade.vertices.copy()
    vb_new = np.zeros_like(vb)
    vb_new[:, 0] = vb[:, 2] - 0.77 / 2.0 + (slit_x - xc)
    vb_new[:, 1] = vb[:, 0]
    vb_new[:, 2] = vb[:, 1]
    m_blade.vertices = vb_new
    
    m_tot = trimesh.util.concatenate([m_clip, m_blade])
    m_tot.apply_translation([xc, 0.0, 0.0])
    return m_tot

def build_option_b_mesh(is_hot=True):
    """Option B: Leaves pinch in X (Left/Right), opening along Y. S-curve hidden under floor."""
    xc = 6.28 if is_hot else -6.28
    slit_x = 8.453 if is_hot else -7.853
    th = 0.25
    left_pts = [(-1.20, 1.0), (-0.75, 4.0), (-0.75, 12.2), (-1.60, 14.0)]
    right_pts = [(1.20, 1.0), (0.75, 4.0), (0.75, 12.2), (1.60, 14.0)]
    p_l = Polygon([(p[0]-th, p[1]) for p in left_pts] + [(p[0]+th, p[1]) for p in reversed(left_pts)])
    p_r = Polygon([(p[0]-th, p[1]) for p in right_pts] + [(p[0]+th, p[1]) for p in reversed(right_pts)])
    
    y_len = 6.0
    m_l = extrude_shapely_geom(p_l, height=y_len)
    vl = m_l.vertices.copy(); vl_new = np.zeros_like(vl)
    vl_new[:, 0] = vl[:, 0]; vl_new[:, 1] = vl[:, 2] - y_len/2.0 + 2.0; vl_new[:, 2] = vl[:, 1]
    m_l.vertices = vl_new
    
    m_r = extrude_shapely_geom(p_r, height=y_len)
    vr = m_r.vertices.copy(); vr_new = np.zeros_like(vr)
    vr_new[:, 0] = vr[:, 0]; vr_new[:, 1] = vr[:, 2] - y_len/2.0 + 2.0; vr_new[:, 2] = vr[:, 1]
    m_r.vertices = vr_new
    
    # Bridge at base
    bridge = Polygon([(-1.20-th, 2.0-y_len/2.0), (1.20+th, 2.0-y_len/2.0),
                      (1.20+th, 2.0-y_len/2.0+0.5), (-1.20-th, 2.0-y_len/2.0+0.5)])
    m_br = extrude_shapely_geom(bridge, height=0.50)
    m_br.apply_translation([0, 0, 1.0])
    
    # Blade under floor
    p_blade = Polygon([(-15.2, -5.5), (-12.1, -5.5), (-12.1, 0.5), (-15.2, 0.5)])
    m_blade = extrude_shapely_geom(p_blade, height=0.77)
    vb = m_blade.vertices.copy(); vb_new = np.zeros_like(vb)
    vb_new[:, 0] = vb[:, 2] - 0.77 / 2.0 + (slit_x - xc)
    vb_new[:, 1] = vb[:, 0]; vb_new[:, 2] = vb[:, 1]
    m_blade.vertices = vb_new
    
    m_tot = trimesh.util.concatenate([m_l, m_r, m_br, m_blade])
    m_tot.apply_translation([xc, 0.0, 0.0])
    return m_tot

def build_option_c_mesh(is_hot=True):
    """
    Option C: Direct 3D representation matching photo_with_grid.png:
    - Base sits in bracket at Z=1.0..2.0
    - Two curved spring prongs extend vertically along the bracket walls
    - No S-curve visible above floor (passes directly through floor into -Z)
    """
    xc = 6.28 if is_hot else -6.28
    slit_x = 8.453 if is_hot else -7.853
    # Two wide wiping plates facing each other along Y, each plate 4.5mm wide in X
    w_plate = 4.5
    th = 0.50
    # Left & right formed wiping pads
    p1 = Polygon([(-w_plate/2.0, -1.0), (w_plate/2.0, -1.0), (w_plate/2.0, -1.0+th), (-w_plate/2.0, -1.0+th)])
    p2 = Polygon([(-w_plate/2.0, 4.0), (w_plate/2.0, 4.0), (w_plate/2.0, 4.0+th), (-w_plate/2.0, 4.0+th)])
    m1 = extrude_shapely_geom(p1, height=12.0)
    m1.apply_translation([0, 0, 1.0])
    m2 = extrude_shapely_geom(p2, height=12.0)
    m2.apply_translation([0, 0, 1.0])
    
    # Base connecting floor plate (inside bracket pocket only, Y in [-2, 5])
    p_base = Polygon([(-w_plate/2.0, -1.5), (w_plate/2.0, -1.5), (w_plate/2.0, -0.5), (-w_plate/2.0, -0.5)])
    m_base = extrude_shapely_geom(p_base, height=0.50)
    m_base.apply_translation([0, 0, 1.0])
    
    # Under-floor spade terminal
    p_blade = Polygon([(-15.2, -5.5), (-12.1, -5.5), (-12.1, 0.5), (-15.2, 0.5)])
    m_blade = extrude_shapely_geom(p_blade, height=0.77)
    vb = m_blade.vertices.copy(); vb_new = np.zeros_like(vb)
    vb_new[:, 0] = vb[:, 2] - 0.77 / 2.0 + (slit_x - xc)
    vb_new[:, 1] = vb[:, 0]; vb_new[:, 2] = vb[:, 1]
    m_blade.vertices = vb_new
    
    m_tot = trimesh.util.concatenate([m1, m2, m_base, m_blade])
    m_tot.apply_translation([xc, 0.0, 0.0])
    return m_tot

def run():
    part_mesh, _ = build_exact_3d_model()
    shaft_mesh = build_shaft_rocker_mesh()
    
    fig = plt.figure(figsize=(24, 8), dpi=180, facecolor='#111827')
    
    # Panel 1: Option A (Front & Back leaves pinching along Y)
    ax1 = fig.add_subplot(1, 3, 1, projection='3d', facecolor='#111827')
    ax1.set_title("Option A: Front & Back Leaves\n(Pinching along Y-axis, slot along X)\nZero S-curve above floor", color='#facc15', fontsize=13, fontweight='bold')
    a_hot = build_option_a_mesh(True)
    a_neu = build_option_a_mesh(False)
    render_unified_panel(ax1, [(part_mesh, '#0284c7', 0.6), (shaft_mesh, '#f59e0b', 0.95), (a_hot, '#facc15', 0.95), (a_neu, '#facc15', 0.95)], elev=55, azim=-65)
    ax1.set_xlim(-24, 24); ax1.set_ylim(-24, 24); ax1.set_zlim(-7, 24)
    
    # Panel 2: Option B (Left & Right leaves pinching along X)
    ax2 = fig.add_subplot(1, 3, 2, projection='3d', facecolor='#111827')
    ax2.set_title("Option B: Left & Right Leaves\n(Pinching along X-axis, slot along Y)\nZero S-curve above floor", color='#38bdf8', fontsize=13, fontweight='bold')
    b_hot = build_option_b_mesh(True)
    b_neu = build_option_b_mesh(False)
    render_unified_panel(ax2, [(part_mesh, '#0284c7', 0.6), (shaft_mesh, '#f59e0b', 0.95), (b_hot, '#facc15', 0.95), (b_neu, '#facc15', 0.95)], elev=55, azim=-65)
    ax2.set_xlim(-24, 24); ax2.set_ylim(-24, 24); ax2.set_zlim(-7, 24)
    
    # Panel 3: Option C (Parallel Wiping Pads across bracket width)
    ax3 = fig.add_subplot(1, 3, 3, projection='3d', facecolor='#111827')
    ax3.set_title("Option C: Transverse Formed Blades\n(Full-width wiping pads in bracket)\nZero S-curve above floor", color='#4ade80', fontsize=13, fontweight='bold')
    c_hot = build_option_c_mesh(True)
    c_neu = build_option_c_mesh(False)
    render_unified_panel(ax3, [(part_mesh, '#0284c7', 0.6), (shaft_mesh, '#f59e0b', 0.95), (c_hot, '#facc15', 0.95), (c_neu, '#facc15', 0.95)], elev=55, azim=-65)
    ax3.set_xlim(-24, 24); ax3.set_ylim(-24, 24); ax3.set_zlim(-7, 24)
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "compare_contact_leaf_orientations.png")
    fig.savefig(out_png, dpi=180, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print("Saved comparison to:", out_png)

if __name__ == '__main__':
    run()
