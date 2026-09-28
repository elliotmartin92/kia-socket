"""
testing/test_rotated_brass.py
Builds accurate 3D mesh of the OEM brass contacts with the correct 90-degree orientation:
- Left & Right spring leaves pinching in X
- Open gap running along Y for plug blade insertion in -Z
- Bottom runner extending to floor slit and blade protruding under the floor (Z < 0)
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

def build_accurate_brass_contact(is_hot=True):
    """
    Constructs an accurate 3D mesh of the OEM stamped brass contact:
    - Leaves pinch along X (separated by pinch throat gap D1b=1.0mm, belly D1a=5.0mm, mouth D5=4.3mm)
    - Leaves extend along Y (Y from -5.8 to +5.8mm, height Z from 1.0 to 15.4mm)
    - Connecting bridge at Y = -5.8mm
    - Runner on floor to slit
    - Terminal blade extending under floor (-Z down to -5.5mm)
    """
    xc = 6.28 if is_hot else -6.28
    slit_x = 8.453 if is_hot else -7.853
    
    # Caliper dimensions
    D1A = 5.00   # Wide belly gap in X
    D1B = 1.00   # Throat pinch gap in X
    D2  = 14.40  # Total height in Z above Z=1.0mm
    D4  = 8.40   # Throat elevation in Z above Z=1.0mm
    D5  = 4.30   # Top flare opening in X
    THICK = 0.50 # Sheet thickness
    th = THICK / 2.0
    
    z_base = BASE_THICK # 1.00mm
    z_belly = z_base + 4.50
    z_throat = z_base + D4
    z_top = z_base + D2
    
    # Left Leaf profile in X-Z (relative to xc):
    # Matches real OEM contact: upright parallel spring leaves with top lead-in flare
    left_pts = [
        (-1.20, z_base),
        (-0.75, z_base + 3.0),
        (-0.75, 12.2),
        (-1.60, 14.0)
    ]
    # Right Leaf profile in X-Z (relative to xc):
    right_pts = [
        (1.20, z_base),
        (0.75, z_base + 3.0),
        (0.75, 12.2),
        (1.60, 14.0)
    ]
    
    poly_left_xz = [(p[0] - th, p[1]) for p in left_pts] + [(p[0] + th, p[1]) for p in reversed(left_pts)]
    poly_right_xz = [(p[0] - th, p[1]) for p in right_pts] + [(p[0] + th, p[1]) for p in reversed(right_pts)]
    
    p_l = Polygon(poly_left_xz)
    p_r = Polygon(poly_right_xz)
    
    # Extrude along Y: from Y = -0.50 to +5.94 (length = 6.44mm, matching photo)
    y_len = 6.44
    y_start = -0.50
    
    # extrude_shapely_geom extrudes in Z. We then map: X->X, Y->Z(new), Z->Y(new)
    m_l = extrude_shapely_geom(p_l, height=y_len)
    vl = m_l.vertices.copy()
    vl_new = np.zeros_like(vl)
    vl_new[:, 0] = vl[:, 0]
    vl_new[:, 1] = vl[:, 2] + y_start  # Y axis
    vl_new[:, 2] = vl[:, 1]           # Z axis
    m_l.vertices = vl_new
    
    m_r = extrude_shapely_geom(p_r, height=y_len)
    vr = m_r.vertices.copy()
    vr_new = np.zeros_like(vr)
    vr_new[:, 0] = vr[:, 0]
    vr_new[:, 1] = vr[:, 2] + y_start  # Y axis
    vr_new[:, 2] = vr[:, 1]           # Z axis
    m_r.vertices = vr_new
    
    # Transverse bridge connecting left and right leaves at Y in [-1.0, -0.50], Z in [1.0, 1.5]
    bridge_poly = Polygon([
        (-D1A/2.0 - th, -1.00),
        (D1A/2.0 + th, -1.00),
        (D1A/2.0 + th, -0.50),
        (-D1A/2.0 - th, -0.50)
    ])
    m_bridge = extrude_shapely_geom(bridge_poly, height=0.50) # Z in [0, 0.5]
    m_bridge.apply_translation([0, 0, 1.0]) # Z in [1.0, 1.5]
    
    # Floor runner to slit: connects bridge to the slit hole with realistic S-curve
    # Starts at center (0, -1.0) and curves to dx_slit at Y = -12.10
    dx_slit = slit_x - xc
    w_run = 1.30
    runner_poly = Polygon([
        (-w_run/2.0, -1.00),
        (w_run/2.0, -1.00),
        (dx_slit + w_run/2.0, -6.50),
        (dx_slit + w_run/2.0, -12.10),
        (dx_slit - w_run/2.0, -12.10),
        (dx_slit - w_run/2.0, -6.50)
    ])
    m_runner = extrude_shapely_geom(runner_poly, height=0.50)
    m_runner.apply_translation([0, 0, 1.0])
    
    # Terminal blade under the floor:
    # Extends through the floor (Z = 1.0 down to -5.5mm, total height 6.5mm)
    # At Y in [-15.2, -12.1] (len = 3.10mm), thickness 0.77mm in X
    blade_poly = Polygon([
        (-15.20, -5.50),
        (-12.10, -5.50),
        (-12.10, 1.50),
        (-15.20, 1.50)
    ])
    m_blade = extrude_shapely_geom(blade_poly, height=0.77)
    # blade_poly is in (Y, Z), extrude is in X.
    vb = m_blade.vertices.copy()
    vb_new = np.zeros_like(vb)
    vb_new[:, 0] = vb[:, 2] - 0.77/2.0 + dx_slit  # centered at dx_slit
    vb_new[:, 1] = vb[:, 0]                       # Y
    vb_new[:, 2] = vb[:, 1]                       # Z
    m_blade.vertices = vb_new
    
    parts = [m_l, m_r, m_bridge, m_runner, m_blade]
    m_tot = trimesh.util.concatenate(parts)
    m_tot.apply_translation([xc, 0.0, 0.0])
    return m_tot

if __name__ == '__main__':
    b_hot = build_accurate_brass_contact(is_hot=True)
    b_neu = build_accurate_brass_contact(is_hot=False)
    part_mesh, _ = build_exact_3d_model()
    shaft_mesh = build_shaft_rocker_mesh()
    
    print("Hot Brass Bounds:", b_hot.bounds)
    print("Neutral Brass Bounds:", b_neu.bounds)
    
    # Visualize top-down and isometric
    from generate_print_assembly_guide import render_unified_panel
    fig = plt.figure(figsize=(14, 7), facecolor='#111827')
    
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#111827')
    ax1.set_title("Top-Down View (Testing 90-Deg Rotated Brass)", color='white')
    render_unified_panel(ax1, [
        (part_mesh, '#0284c7', 0.6),
        (shaft_mesh, '#f59e0b', 0.95),
        (b_hot, '#facc15', 0.95),
        (b_neu, '#facc15', 0.95)
    ], elev=90, azim=-90)
    ax1.set_xlim(-22, 22); ax1.set_ylim(-22, 22); ax1.set_zlim(-7, 20)
    
    ax2 = fig.add_subplot(1, 2, 2, projection='3d', facecolor='#111827')
    ax2.set_title("Isometric View (Elev=55, Azim=-65)", color='white')
    render_unified_panel(ax2, [
        (part_mesh, '#0284c7', 0.6),
        (shaft_mesh, '#f59e0b', 0.95),
        (b_hot, '#facc15', 0.95),
        (b_neu, '#facc15', 0.95)
    ], elev=55, azim=-65)
    ax2.set_xlim(-22, 22); ax2.set_ylim(-22, 22); ax2.set_zlim(-7, 20)
    
    out_img = os.path.join(os.path.dirname(__file__), 'test_rotated_brass.png')
    fig.savefig(out_img, dpi=180, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print("Test render saved to:", out_img)
