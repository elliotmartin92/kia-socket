"""
testing/render_prototype_plate.py
Renders high-resolution multi-view 3D visualizations of the 5-pack prototype plate:
- Test 1 [I]:     Commit [b4877a9] Exact (Baseline)
- Test 2 [II]:    Commit [b4877a9] Tuned (Pre-travel 1.25mm, Apex Z=7.75mm)
- Test 3 [III]:   V1 Ultra-Sensitive (Apex Y=1.65, Plunger Y=11.25)
- Test 4 [IIII]:  V3 Balanced Nominal (Apex Y=2.10, Plunger Y=10.95)
- Test 5 [IIIII]: V4 Smooth Progressive (Apex Y=2.30, Plunger Y=10.80)
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testing.build_prototype_levers import (
    get_test_suite, build_bed_pad_with_notches,
    build_b4877a9_rocker_mesh,
    build_variant_lever_45deg, build_variant_supports_45deg,
    PROTO_AXLE_LEN, R_PIP_45, LEVER_PITCH_X
)

def render_3d_plate(out_path="testing/prototype_5pack_3d_render.png"):
    test_suite = get_test_suite()
    pad_mesh, x_offsets = build_bed_pad_with_notches(test_suite, pitch_x=LEVER_PITCH_X)
    
    colors = [
        '#e11d48',  # Red: b4877a9 Exact
        '#f59e0b',  # Amber: b4877a9 Tuned
        '#38bdf8',  # Sky Blue: V1 Ultra-Sens
        '#a855f7',  # Purple: V3 Nominal
        '#10b981',  # Emerald: V4 Smooth
    ]
    supp_color = '#64748b'  # Slate gray for breakaway supports
    pad_color = '#334155'   # Dark slate for bed pad raft
    
    fig = plt.figure(figsize=(20, 11), facecolor='#0f172a')
    
    # 2 Subplots: Isometric view & Front-Elevated view
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    
    for ax in [ax1, ax2]:
        ax.set_facecolor('#0f172a')
        ax.grid(False)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('#1e293b')
        ax.yaxis.pane.set_edgecolor('#1e293b')
        ax.zaxis.pane.set_edgecolor('#1e293b')
        ax.tick_params(colors='#94a3b8', labelsize=8)
        
    def add_mesh_to_ax(ax, mesh, facecolor, alpha=1.0, edgecolor=None):
        # Downsample mesh faces for fast, clean rendering if large
        v = mesh.vertices
        f = mesh.faces
        if len(f) > 4000:
            step = int(np.ceil(len(f) / 3500))
            f = f[::step]
        polys = v[f]
        poly_col = Poly3DCollection(polys, facecolors=facecolor, alpha=alpha, edgecolors=edgecolor, linewidths=0.1)
        ax.add_collection3d(poly_col)
        
    print("Rendering bed pad...")
    add_mesh_to_ax(ax1, pad_mesh, pad_color, alpha=0.85)
    add_mesh_to_ax(ax2, pad_mesh, pad_color, alpha=0.85)
    
    x_lever_center = 9.25
    for i, test in enumerate(test_suite):
        cx = x_offsets[i]
        c = colors[i]
        print(f"Rendering lever {i+1}/5: {test['short_name']}...")
        
        if test['is_b4877a9']:
            p_y = test['plunger_y']
            c_pts = test['cam_pts']
            m_raw = build_b4877a9_rocker_mesh(axle_len=PROTO_AXLE_LEN, plunger_y=p_y, cam_pts=c_pts)
            m_lever = m_raw.apply_transform(R_PIP_45)
        else:
            cfg = test['cfg']
            m_lever = build_variant_lever_45deg(cfg, axle_len=PROTO_AXLE_LEN)
            
        m_supp = build_variant_supports_45deg(test)
            
        m_lever.apply_translation([-x_lever_center + cx, 0, 0])
        m_supp.apply_translation([-x_lever_center + cx, 0, 0])
        
        add_mesh_to_ax(ax1, m_supp, supp_color, alpha=0.6)
        add_mesh_to_ax(ax1, m_lever, c, alpha=0.95)
        
        add_mesh_to_ax(ax2, m_supp, supp_color, alpha=0.6)
        add_mesh_to_ax(ax2, m_lever, c, alpha=0.95)
        
        # Add labels above each lever
        ax1.text(cx, -2.0, 19.5, f"[{test['bars']}] {test['short_name']}", color=c, fontsize=8.5, fontweight='bold', ha='center')
        ax2.text(cx, -2.0, 19.5, f"[{test['bars']}] {test['short_name']}", color=c, fontsize=8.5, fontweight='bold', ha='center')
        
    for ax in [ax1, ax2]:
        ax.set_xlim(-46, 46)
        ax.set_ylim(-10, 18)
        ax.set_zlim(0, 22)
        ax.set_xlabel("X (mm)", color='#94a3b8', labelpad=4)
        ax.set_ylabel("Y (mm)", color='#94a3b8', labelpad=4)
        ax.set_zlabel("Z (mm)", color='#94a3b8', labelpad=4)
        
    ax1.view_init(elev=28, azim=-55)
    ax1.set_title("Isometric View (+45° PIP Production Tilt & Breakaway Supports)", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    
    ax2.view_init(elev=18, azim=-80)
    ax2.set_title("Front-Quarter View (Embossed I, II, III, IV, V Identification Notches)", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    
    plt.suptitle("5-TEST RAPID-PROTOTYPE RETROFIT PLATE (Shortened Axle: 9.80mm, Bed Pad: 87 x 23 mm)",
                 color='#f8fafc', fontsize=14, fontweight='bold', y=0.97)
    
    plt.tight_layout()
    abs_out = os.path.normpath(os.path.abspath(out_path))
    plt.savefig(abs_out, dpi=200, facecolor='#0f172a')
    plt.close()
    print(f"Render saved to: {abs_out}")

def render_combined_master_plate(out_path="testing/combined_master_plate_3d_render.png"):
    plate_path = os.path.join(os.path.dirname(__file__), "complete_assembly_plus_5levers_plate.stl")
    if not os.path.exists(plate_path):
        return
        
    m = trimesh.load(plate_path)
    fig = plt.figure(figsize=(16, 10), facecolor='#0f172a')
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.set_facecolor('#0f172a')
    ax.grid(False)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.tick_params(colors='#94a3b8', labelsize=8)
    
    v = m.vertices
    f = m.faces
    step = int(np.ceil(len(f) / 6000))
    f_sub = f[::step]
    polys = v[f_sub]
    poly_col = Poly3DCollection(polys, facecolors='#38bdf8', alpha=0.9, edgecolors='#0f172a', linewidths=0.1)
    ax.add_collection3d(poly_col)
    
    ax.set_xlim(-50, 50)
    ax.set_ylim(-40, 50)
    ax.set_zlim(0, 35)
    ax.set_xlabel("X (mm)", color='#94a3b8')
    ax.set_ylabel("Y (mm)", color='#94a3b8')
    ax.set_zlabel("Z (mm)", color='#94a3b8')
    ax.view_init(elev=32, azim=-60)
    
    plt.title("COMBINED MASTER PRINT PLATE (Production Assembly + 5 Prototype Levers)\nFootprint: 87 x 71 mm on Build Plate",
              color='#f8fafc', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    abs_out = os.path.normpath(os.path.abspath(out_path))
    plt.savefig(abs_out, dpi=200, facecolor='#0f172a')
    plt.close()
    print(f"Combined master render saved to: {abs_out}")

if __name__ == '__main__':
    render_3d_plate()
    render_combined_master_plate()
