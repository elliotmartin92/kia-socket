"""
testing/model_exact_zoom_bracket_brass.py
Models the OEM brass contact exactly matching zoom_bracket34_photo.png:
1. Two horizontal contact leaves with curled inner wiping edges and rounded outer corners
2. Stepped-down U-bracket bridge at Y ~ -2.5mm
3. S-curved brass runner clearly visible above the floor extending to the slit
4. Vertical spade blade plunging through floor slit into -Z under the floor
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, extrude_shapely_geom, BASE_THICK
from build_shaft import build_shaft_rocker_mesh
from generate_print_assembly_guide import render_unified_panel

def build_zoom_matched_brass(is_hot=True):
    xc = 6.28 if is_hot else -6.28
    slit_x = 8.453 if is_hot else -7.853
    
    parts = []
    
    # 1. Left and Right horizontal contact leaves (Z ~ 4.5 to 5.0mm)
    # Matching the two rounded rectangular pads in zoom_bracket34_photo.png
    y_start = -1.0
    y_end   =  5.8
    y_len   = y_end - y_start # 6.8mm
    
    w_pad = 2.20
    gap   = 1.10 # pinch slit gap
    
    # Left Pad: X in [-(gap/2 + w_pad), -gap/2] -> [-2.75, -0.55] relative to xc
    # Right Pad: X in [gap/2, gap/2 + w_pad] -> [0.55, 2.75] relative to xc
    
    # Pad top flat plate (Z = 4.5 to 5.0)
    p_left_flat = Polygon([
        (-(gap/2.0 + w_pad), y_start),
        (-gap/2.0, y_start),
        (-gap/2.0, y_end),
        (-(gap/2.0 + w_pad), y_end)
    ])
    m_left_flat = extrude_shapely_geom(p_left_flat, height=0.50)
    m_left_flat.apply_translation([0, 0, 4.5])
    
    p_right_flat = Polygon([
        (gap/2.0, y_start),
        (gap/2.0 + w_pad, y_start),
        (gap/2.0 + w_pad, y_end),
        (gap/2.0, y_end)
    ])
    m_right_flat = extrude_shapely_geom(p_right_flat, height=0.50)
    m_right_flat.apply_translation([0, 0, 4.5])
    
    # Inner curled wiping edges (curling down from Z=4.5 to Z=2.0 along the gap)
    p_left_curl = Polygon([
        (-gap/2.0 - 0.40, y_start),
        (-gap/2.0, y_start),
        (-gap/2.0, y_end),
        (-gap/2.0 - 0.40, y_end)
    ])
    m_left_curl = extrude_shapely_geom(p_left_curl, height=2.50)
    m_left_curl.apply_translation([0, 0, 2.0])
    
    p_right_curl = Polygon([
        (gap/2.0, y_start),
        (gap/2.0 + 0.40, y_start),
        (gap/2.0 + 0.40, y_end),
        (gap/2.0, y_end)
    ])
    m_right_curl = extrude_shapely_geom(p_right_curl, height=2.50)
    m_right_curl.apply_translation([0, 0, 2.0])
    
    # Outer side walls (curling down to seating shelf at Z=1.5)
    p_left_wall = Polygon([
        (-(gap/2.0 + w_pad), y_start),
        (-(gap/2.0 + w_pad) + 0.50, y_start),
        (-(gap/2.0 + w_pad) + 0.50, y_end),
        (-(gap/2.0 + w_pad), y_end)
    ])
    m_left_wall = extrude_shapely_geom(p_left_wall, height=3.00)
    m_left_wall.apply_translation([0, 0, 1.5])
    
    p_right_wall = Polygon([
        (gap/2.0 + w_pad - 0.50, y_start),
        (gap/2.0 + w_pad, y_start),
        (gap/2.0 + w_pad, y_end),
        (gap/2.0 + w_pad - 0.50, y_end)
    ])
    m_right_wall = extrude_shapely_geom(p_right_wall, height=3.00)
    m_right_wall.apply_translation([0, 0, 1.5])
    
    # 2. U-shaped step-down bridge at Y in [-2.5, -1.0], Z in [1.0, 1.5]
    # Stepped risers at Y in [-1.5, -1.0] connecting leaves down to floor
    p_riser_l = Polygon([(-(gap/2.0 + w_pad), -1.5), (-(gap/2.0 + w_pad - 0.6), -1.5),
                         (-(gap/2.0 + w_pad - 0.6), -1.0), (-(gap/2.0 + w_pad), -1.0)])
    m_riser_l = extrude_shapely_geom(p_riser_l, height=3.00)
    m_riser_l.apply_translation([0, 0, 1.5])
    
    p_riser_r = Polygon([(gap/2.0 + w_pad - 0.6, -1.5), (gap/2.0 + w_pad, -1.5),
                         (gap/2.0 + w_pad, -1.0), (gap/2.0 + w_pad - 0.6, -1.0)])
    m_riser_r = extrude_shapely_geom(p_riser_r, height=3.00)
    m_riser_r.apply_translation([0, 0, 1.5])
    
    # Horizontal crossbar at Y in [-2.5, -1.5], Z in [1.0, 1.5]
    p_crossbar = Polygon([
        (-(gap/2.0 + w_pad), -2.5),
        (gap/2.0 + w_pad, -2.5),
        (gap/2.0 + w_pad, -1.5),
        (-(gap/2.0 + w_pad), -1.5)
    ])
    m_crossbar = extrude_shapely_geom(p_crossbar, height=0.50)
    m_crossbar.apply_translation([0, 0, 1.0])
    
    # 3. S-curved runner clearly visible on the floor (Z = 1.0 to 1.5mm)
    # Runs from crossbar (Y = -2.5) to the slit (Y = -12.10)
    dx_slit = slit_x - xc
    w_run = 1.80
    
    # Smooth S-curve profile
    y_pts = np.linspace(-2.5, -12.1, 15)
    # S-curve interpolation from x=0 to x=dx_slit
    t = (y_pts - (-2.5)) / (-12.1 - (-2.5))
    # Smoothstep curve: 3*t^2 - 2*t^3
    s = 3*t**2 - 2*t**3
    x_centerline = s * dx_slit
    
    # Construct polygon
    poly_left_edge = [(x_centerline[i] - w_run/2.0, y_pts[i]) for i in range(len(y_pts))]
    poly_right_edge = [(x_centerline[i] + w_run/2.0, y_pts[i]) for i in reversed(range(len(y_pts)))]
    p_runner = Polygon(poly_left_edge + poly_right_edge)
    m_runner = extrude_shapely_geom(p_runner, height=0.50)
    m_runner.apply_translation([0, 0, 1.0])
    
    # 4. Terminal blade plunging through floor slit into -Z under the floor
    # At Y in [-15.2, -12.1], extending from Z = 1.5 down to Z = -5.5
    p_blade = Polygon([
        (-15.2, -5.5),
        (-12.1, -5.5),
        (-12.1, 1.5),
        (-15.2, 1.5)
    ])
    m_blade = extrude_shapely_geom(p_blade, height=0.77)
    vb = m_blade.vertices.copy()
    vb_new = np.zeros_like(vb)
    vb_new[:, 0] = vb[:, 2] - 0.77 / 2.0 + dx_slit
    vb_new[:, 1] = vb[:, 0]
    vb_new[:, 2] = vb[:, 1]
    m_blade.vertices = vb_new
    
    all_pieces = [m_left_flat, m_right_flat, m_left_curl, m_right_curl,
                  m_left_wall, m_right_wall, m_riser_l, m_riser_r,
                  m_crossbar, m_runner, m_blade]
    m_tot = trimesh.util.concatenate(all_pieces)
    m_tot.apply_translation([xc, 0.0, 0.0])
    return m_tot

if __name__ == '__main__':
    part_mesh, _ = build_exact_3d_model()
    shaft_mesh = build_shaft_rocker_mesh()
    b_hot = build_zoom_matched_brass(True)
    b_neu = build_zoom_matched_brass(False)
    
    fig = plt.figure(figsize=(16, 8), dpi=180, facecolor='#111827')
    
    # Panel 1: Top-down matching photo
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#111827')
    ax1.set_title("Top-Down (Matches zoom_bracket34_photo.png)", color='white', fontsize=14)
    render_unified_panel(ax1, [
        (part_mesh, '#0284c7', 0.55),
        (shaft_mesh, '#f59e0b', 0.95),
        (b_hot, '#facc15', 0.95),
        (b_neu, '#facc15', 0.95)
    ], elev=90, azim=-90)
    ax1.set_xlim(-24, 24); ax1.set_ylim(-24, 24); ax1.set_zlim(-7, 20)
    
    # Panel 2: Isometric
    ax2 = fig.add_subplot(1, 2, 2, projection='3d', facecolor='#111827')
    ax2.set_title("Isometric View (Elev=55, Azim=-65)", color='white', fontsize=14)
    render_unified_panel(ax2, [
        (part_mesh, '#0284c7', 0.65),
        (shaft_assembled := build_shaft_rocker_mesh(in_assembly_coords=True), '#f59e0b', 0.95),
        (b_hot, '#facc15', 0.95),
        (b_neu, '#facc15', 0.95)
    ], elev=55, azim=-65)
    ax2.set_xlim(-24, 24); ax2.set_ylim(-24, 24); ax2.set_zlim(-7, 20)
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "test_zoom_matched_brass.png")
    fig.savefig(out_png, dpi=180, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print("Saved test render to:", out_png)
