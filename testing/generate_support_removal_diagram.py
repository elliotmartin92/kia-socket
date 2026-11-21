"""
testing/generate_support_removal_diagram.py
Generates a clear, visual step-by-step diagram detailing the exact support removal sequence:
  Step 1: Break Backplate Fins
  Step 2: Break Lever Plunger Strut
  Step 3: Peel Bottom Bed Pad
  Step 4: Remove Remaining Supports (Cam Strut, Shaft Strut, Clip Trees, Slit Saddles)
  Step 5: Free Lever (Wiggle like a loose tooth)
"""
import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp
import build_shaft as bs

def render_support_removal_diagram():
    print("Generating Support Removal Sequence Diagram...")
    
    # 1. Base part and shaft
    part_flat, base_poly = bp.build_exact_3d_model()
    shaft_assembled = bs.build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    
    # Rotation for 45-degree print orientation
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    z_min = part_flat.copy().apply_transform(R).bounds[0, 2]
    
    part_45 = part_flat.copy().apply_transform(R)
    part_45.apply_translation([0, 0, -z_min])
    
    shaft_45 = shaft_assembled.copy().apply_transform(R)
    shaft_45.apply_translation([0, 0, -z_min])
    
    # 2. Extract Individual Support Sub-Meshes in 45-deg Space
    # (a) Bed Pad
    x_min, x_max = -bp.BED_PAD_WIDTH_X / 2.0, bp.BED_PAD_WIDTH_X / 2.0
    y_min, y_max = bp.BED_PAD_Y_CENTER - bp.BED_PAD_LEN_Y / 2.0, bp.BED_PAD_Y_CENTER + bp.BED_PAD_LEN_Y / 2.0
    r_corner = bp.BED_PAD_CORNER_RADIUS
    inner_box = box(x_min + r_corner, y_min + r_corner, x_max - r_corner, y_max - r_corner)
    pad_poly = inner_box.buffer(r_corner, resolution=16)
    cx_left, cx_right = -7.853, 8.453
    relief_l = box(cx_left - 0.70, -10.5, cx_left + 0.70, -8.3)
    relief_r = box(cx_right - 0.70, -10.5, cx_right + 0.70, -8.3)
    pad_poly_cut = pad_poly.difference(unary_union([relief_l, relief_r]))
    pad_mesh = trimesh.creation.extrude_polygon(pad_poly_cut, height=bp.BED_PAD_HEIGHT_Z)
    
    # (b) Backplate Fins (5 vertical fins)
    fin_thick_x = 0.80
    standoff = 0.26
    z_bed = 0.60
    tine_w_x = 0.55
    tine_l_y = 0.45
    tine_pitch = 4.50
    r2 = np.sqrt(2) / 2.0
    
    back_fins_list = []
    # 5 fin positions: inner pair, outer pair, center
    fin_configs = [
        (-14.00, -3.00, 10.00),
        (-8.00,  -5.80, 14.00),
        (0.00,   -3.00, 14.00),
        (6.80,   -5.80, 14.00),
        (14.00,  -3.00, 10.00)
    ]
    for x_c, y_start, y_end in fin_configs:
        z_start = y_start - z_min - standoff
        z_end = y_end - z_min - standoff
        pts_fin = [
            (y_start, z_bed),
            (y_start, z_start),
            (y_end, z_end),
            (y_end, z_bed)
        ]
        poly_fin = Polygon(pts_fin)
        m_fin = trimesh.creation.extrude_polygon(poly_fin, height=fin_thick_x)
        v_f = m_fin.vertices.copy()
        v_f_3d = np.column_stack([v_f[:, 2] + x_c - fin_thick_x/2.0, v_f[:, 0], v_f[:, 1]])
        fin_3d = trimesh.Trimesh(vertices=v_f_3d, faces=m_fin.faces.copy(), process=True)
        back_fins_list.append(fin_3d)
        
        # Add tines
        y_tines = np.arange(y_start + 2.0, y_end - 1.0, tine_pitch)
        for yt in y_tines:
            zt = yt - z_min
            tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
            tine.apply_translation([x_c, yt, zt - standoff/2.0 + 0.05])
            back_fins_list.append(tine)
            
    back_fins_mesh = trimesh.util.concatenate(back_fins_list)
    
    # (c) Lever Plunger Strut
    py = 10.95
    reach = 7.00
    r_tip = 1.00
    gap_p = 0.28
    dz_shift = -z_min
    y_knee = (py - r_tip) * r2 - (-reach + r_tip) * r2
    z_knee = (py - r_tip) * r2 + (-reach + r_tip) * r2
    alphas = np.linspace(np.pi, np.pi * 0.50, 16)
    tip_y = py + r_tip * np.cos(alphas)
    tip_z = -reach + r_tip * (1.0 - np.sin(alphas))
    tip_y45 = tip_y * r2 - tip_z * r2
    tip_z45 = tip_y * r2 + tip_z * r2
    y_start = 8.00
    y_slope = np.linspace(y_start, y_knee, 10)
    z_slope = z_knee + (y_knee - y_slope)
    y_pts = np.concatenate([y_slope, tip_y45[1:]])
    z_pts = np.concatenate([z_slope, tip_z45[1:]]) + dz_shift - gap_p
    y_end = y_pts[-1]
    pts_p = [(y_start, 0.60)]
    for y_v, z_v in zip(y_pts, z_pts):
        pts_p.append((y_v, max(0.80, z_v)))
    pts_p.append((y_end, 0.60))
    poly_p = Polygon(pts_p)
    m_pl = trimesh.creation.extrude_polygon(poly_p, height=0.80)
    v_pl = m_pl.vertices.copy()
    v_pl_3d = np.column_stack([v_pl[:, 2] + 8.484, v_pl[:, 0], v_pl[:, 1]])
    plunger_strut_l = trimesh.Trimesh(vertices=v_pl_3d, faces=m_pl.faces.copy(), process=True)
    v_pr_3d = np.column_stack([v_pl[:, 2] + 12.084 - 0.80, v_pl[:, 0], v_pl[:, 1]])
    plunger_strut_r = trimesh.Trimesh(vertices=v_pr_3d, faces=m_pl.faces.copy(), process=True)
    v_pc_3d = np.column_stack([v_pl[:, 2] + 10.284 - 0.45, v_pl[:, 0], v_pl[:, 1]])
    plunger_strut_c = trimesh.Trimesh(vertices=v_pc_3d, faces=m_pl.faces.copy(), process=True)
    p_web = trimesh.creation.box([3.60, 2.50, 1.40])
    p_web.apply_translation([10.284, 9.25, 0.60 + 0.70])
    plunger_strut_mesh = trimesh.util.concatenate([plunger_strut_l, plunger_strut_r, plunger_strut_c, p_web])

    # (d) Remaining Supports: Cam Strut, Shaft Stick, Clip Trees, Slit Saddles
    # Cam strut
    cam_c_x = 6.250
    cam_c_y = -2.550
    z_floor_cam = 12.110
    cam_neck = trimesh.creation.box([1.10, 1.10, 2.00])
    cam_neck.apply_translation([cam_c_x, cam_c_y, z_floor_cam + 1.00])
    cam_trunk_h = 16.00 - (z_floor_cam + 2.00)
    cam_trunk = trimesh.creation.box([1.40, 1.40, cam_trunk_h])
    cam_trunk.apply_translation([cam_c_x, cam_c_y, (z_floor_cam + 2.00) + cam_trunk_h / 2.0])
    pts_cam_tine_yz = [
        (-3.95, 16.00), (-3.95, 19.793), (-3.75, 19.611), (-3.55, 19.503),
        (-3.35, 19.430), (-3.15, 19.406), (-2.95, 19.382), (-2.75, 19.358),
        (-2.55, 19.334), (-2.35, 19.414), (-2.15, 19.494), (-1.95, 19.574),
        (-1.75, 19.654), (-1.55, 19.734), (-1.35, 19.814), (-1.15, 19.894),
        (-1.15, 16.00)
    ]
    poly_cam_h = Polygon(pts_cam_tine_yz)
    m_cl = trimesh.creation.extrude_polygon(poly_cam_h, height=0.50)
    v_cl = m_cl.vertices.copy()
    v_cl_3d = np.column_stack([v_cl[:, 2] + 5.40, v_cl[:, 0], v_cl[:, 1]])
    cam_t_l = trimesh.Trimesh(vertices=v_cl_3d, faces=m_cl.faces.copy(), process=True)
    v_cr_3d = np.column_stack([v_cl[:, 2] + 7.15 - 0.50, v_cl[:, 0], v_cl[:, 1]])
    cam_t_r = trimesh.Trimesh(vertices=v_cr_3d, faces=m_cl.faces.copy(), process=True)
    cam_strut_mesh = trimesh.util.concatenate([cam_neck, cam_trunk, cam_t_l, cam_t_r])

    # Shaft stick
    s_x = 8.85
    s_y = 1.05
    z_fl_s = 13.610
    s_neck = trimesh.creation.box([0.65, 0.65, 1.40])
    s_neck.apply_translation([s_x, s_y, z_fl_s + 0.70])
    s_trunk_h = 21.50 - (z_fl_s + 1.40)
    s_trunk = trimesh.creation.box([0.70, 0.85, s_trunk_h])
    s_trunk.apply_translation([s_x, s_y, (z_fl_s + 1.40) + s_trunk_h / 2.0])
    shaft_stick_mesh = trimesh.util.concatenate([s_neck, s_trunk])

    # Slit saddles
    slit_saddles = bp.build_insert_backside_breakaway_supports_mesh()

    # Clip supports
    clip_supports = bp.build_bottom_clip_45deg_supports_mesh(base_poly)
    clip_supports.apply_transform(R)
    clip_supports.apply_translation([0, 0, -z_min])

    # 3. Create Multi-View Plot (2 Perspective Angles: Back Under-View & Front 3/4 View)
    fig = plt.figure(figsize=(26, 13), dpi=200, facecolor='#0b1120')

    # Subplot 1: Back Under-View (Highlights Steps 1, 2, 3)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#0f172a')
    ax1.set_title("SUPPORT REMOVAL: STEPS 1 → 2 → 3\n(Underside View: Bed Pad & Backplate Fins)", 
                  color='#f8fafc', fontsize=16, fontweight='bold', pad=20)
    
    def add_mesh_collection(ax, m, color, alpha=0.85, edge='#1e293b', lw=0.1):
        if m is not None and len(m.faces) > 0:
            poly = Poly3DCollection(m.vertices[m.faces], alpha=alpha, edgecolor=edge, linewidths=lw)
            poly.set_facecolor(color)
            ax.add_collection3d(poly)

    # Render Part (translucent dark cyan)
    add_mesh_collection(ax1, part_45, '#38bdf8', alpha=0.35, edge='#0284c7', lw=0.1)
    add_mesh_collection(ax1, shaft_45, '#fbbf24', alpha=0.90, edge='#d97706', lw=0.2)

    # Color code supports in ax1:
    # 1. Back Fins -> Bright Red
    add_mesh_collection(ax1, back_fins_mesh, '#ef4444', alpha=0.95, edge='#991b1b', lw=0.3)
    # 2. Lever Strut -> Bright Orange
    add_mesh_collection(ax1, plunger_strut_mesh, '#f97316', alpha=0.95, edge='#c2410c', lw=0.3)
    # 3. Bed Pad -> Golden Amber
    add_mesh_collection(ax1, pad_mesh, '#eab308', alpha=0.80, edge='#a16207', lw=0.2)
    # 4. Slit saddles -> Soft Purple
    add_mesh_collection(ax1, slit_saddles, '#a855f7', alpha=0.85, edge='#6b21a8', lw=0.2)
    # Clip trees
    add_mesh_collection(ax1, clip_supports, '#06b6d4', alpha=0.85, edge='#0891b2', lw=0.2)

    ax1.view_init(elev=-25, azim=135) # Looking up from underneath/back
    ax1.set_xlim(-26, 26); ax1.set_ylim(-24, 24); ax1.set_zlim(-2, 34)
    ax1.set_axis_off()

    # Step Callouts on ax1
    ax1.text2D(0.50, 0.92, 
               "REMOVAL SEQUENCE (Follow in Order to Prevent Lever Damage):", 
               transform=ax1.transAxes, color='#ffffff', fontsize=12.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.4', fc='#1e293b', ec='#64748b', lw=1.5))

    ax1.text2D(0.18, 0.75, 
               "❶ BREAK BACK FINS\n"
               "• 5 vertical fins on angled backplate\n"
               "• Break away along serrated tines", 
               transform=ax1.transAxes, color='#fca5a5', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#450a0a', ec='#ef4444', lw=1.8))

    ax1.text2D(0.82, 0.75, 
               "❷ BREAK LEVER STRUT\n"
               "• Reach into floor hole\n"
               "• Snap plunger strut off bed pad", 
               transform=ax1.transAxes, color='#fed7aa', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#431407', ec='#f97316', lw=1.8))

    ax1.text2D(0.50, 0.12, 
               "❸ PEEL OFF BOTTOM BED PAD\n"
               "• With fins & lever strut disconnected, peel pad cleanly\n"
               "• Prevents any twisting or pulling load on the lever", 
               transform=ax1.transAxes, color='#fef08a', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#422006', ec='#eab308', lw=1.8))


    # Subplot 2: Front Top 3/4 View (Highlights Steps 4 & 5)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d', facecolor='#0f172a')
    ax2.set_title("SUPPORT REMOVAL: STEPS 4 → 5\n(Front View: Remaining Supports & Freeing Lever)", 
                  color='#f8fafc', fontsize=16, fontweight='bold', pad=20)

    add_mesh_collection(ax2, part_45, '#38bdf8', alpha=0.40, edge='#0284c7', lw=0.1)
    add_mesh_collection(ax2, shaft_45, '#22c55e', alpha=0.95, edge='#15803d', lw=0.3) # Highlight lever in green!

    # Remaining supports in ax2
    add_mesh_collection(ax2, cam_strut_mesh, '#06b6d4', alpha=0.95, edge='#0891b2', lw=0.3)
    add_mesh_collection(ax2, shaft_stick_mesh, '#06b6d4', alpha=0.95, edge='#0891b2', lw=0.3)
    add_mesh_collection(ax2, clip_supports, '#06b6d4', alpha=0.95, edge='#0891b2', lw=0.3)
    add_mesh_collection(ax2, slit_saddles, '#a855f7', alpha=0.95, edge='#6b21a8', lw=0.3)

    ax2.view_init(elev=38, azim=-62) # Looking down onto towers and clips
    ax2.set_xlim(-26, 26); ax2.set_ylim(-24, 24); ax2.set_zlim(-2, 34)
    ax2.set_axis_off()

    ax2.text2D(0.50, 0.92, 
               "CLEAR REMAINING SUPPORTS, THEN FREE THE LEVER:", 
               transform=ax2.transAxes, color='#ffffff', fontsize=12.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.4', fc='#1e293b', ec='#64748b', lw=1.5))

    ax2.text2D(0.20, 0.70, 
               "❹ CLEAR REMAINING SUPPORTS\n"
               "• Snap twin-tine cam strut (0.28mm gap)\n"
               "• Snap shaft barrel stick at floor neck\n"
               "• Snip bottom clip trident trees\n"
               "• Snap slit chimney saddles underneath", 
               transform=ax2.transAxes, color='#a5f3fc', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#083344', ec='#06b6d4', lw=1.8))

    ax2.text2D(0.80, 0.70, 
               "❺ FREE THE LEVER (PIVOT CHECK)\n"
               "• Wiggle back lever gently like a loose tooth\n"
               "• If stuck, grip shaft barrel with needle-nose pliers\n"
               "• Verify smooth, bind-free rotation in towers", 
               transform=ax2.transAxes, color='#bbf7d0', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#052e16', ec='#22c55e', lw=2.0))

    ax2.text2D(0.50, 0.12, 
               "✔ ALL SUPPORTS CLEARED — LEVER PIVOTS FREELY IN 360° BRIDGED TOWERS", 
               transform=ax2.transAxes, color='#4ade80', fontsize=11.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#064e3b', ec='#22c55e', lw=1.5))

    plt.tight_layout()
    out_path = 'testing/support_removal_guide.png'
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"Successfully generated: {out_path}")

if __name__ == '__main__':
    render_support_removal_diagram()
