"""
testing/generate_slit_insert_fix_diagram.py
Generates the 4-panel visual diagram with the right slit kept at its exact original position (X = +8.453mm):
- Panel 1: Original Position Layout (Left: X=-7.853mm, Right: X=+8.453mm)
- Panel 2: Inner Wall Relief Fix (Resolving the 0.96mm wall overhang blocking the right socket)
- Panel 3: 3D Sloped Slit Insert (2.20mm Wide End + Tapered Key)
- Panel 4: Cross-Sectional Seating & Tolerances
"""
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import trimesh

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly, create_arch_wall_poly,
    OUTER_WALL_THICK, SLIT_BOSS_HEIGHT, BASE_THICK
)

CX_LEFT = -7.853
CX_RIGHT = +8.453   # Exact original location
CY_SLIT = -13.589

SLIT_W = 1.35   # Expanded slit width (+0.58mm clearance for 0.77mm blade)
SLIT_L = 3.65   # Expanded slit length (+0.55mm clearance for 3.10mm blade)

BODY_W_TIP = 2.20   # Exact 2.20mm wide end
BODY_L_TIP = 4.20
BODY_W_BASE = 2.70  # Sits flush within perimeter wall edge (X_max = 8.453 + 1.35 = 9.803 <= 9.812)
BODY_L_BASE = 4.80

KEY_W_BASE = 1.90
KEY_L_BASE = 4.20
KEY_W_TOP = 1.40
KEY_L_TOP = 3.70
KEY_H = 0.85

SOCKET_W = KEY_W_BASE + 0.50  # 2.40mm (0.50mm clearance)
SOCKET_L = KEY_L_BASE + 0.50  # 4.70mm

def create_frustum_mesh(w_bot, l_bot, w_top, l_top, z_bot, z_top):
    v_bot = np.array([
        [-w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2,  l_bot/2, z_bot],
        [-w_bot/2,  l_bot/2, z_bot],
    ])
    v_top = np.array([
        [-w_top/2, -l_top/2, z_top],
        [ w_top/2, -l_top/2, z_top],
        [ w_top/2,  l_top/2, z_top],
        [-w_top/2,  l_top/2, z_top],
    ])
    verts = np.vstack([v_bot, v_top])
    faces = [
        [0, 3, 2], [0, 2, 1],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7],
    ]
    return trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)

def build_sloped_insert_solid():
    z0 = 0.00
    z1 = SLIT_BOSS_HEIGHT  # 2.47mm
    z2 = z1 + KEY_H        # 3.32mm
    
    m_body = create_frustum_mesh(BODY_W_TIP, BODY_L_TIP, BODY_W_BASE, BODY_L_BASE, z0, z1)
    m_key = create_frustum_mesh(KEY_W_BASE, KEY_L_BASE, KEY_W_TOP, KEY_L_TOP, z1, z2)
    m_solid = m_body.union(m_key, engine='manifold')
    
    hole_cutter = trimesh.creation.box([SLIT_W, SLIT_L, z2 + 2.0])
    hole_cutter.apply_translation([0, 0, (z2 + 2.0)/2.0 - 0.5])
    return m_solid.difference(hole_cutter, engine='manifold')

def generate_diagram():
    fig = plt.figure(figsize=(24, 7.0), dpi=220, facecolor='#ffffff')
    gs = fig.add_gridspec(1, 4, width_ratios=[1.0, 1.0, 1.05, 1.15], wspace=0.28, left=0.04, right=0.96, top=0.88, bottom=0.10)
    
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    bx, by = outer_body_poly.exterior.xy
    arch_poly = create_arch_wall_poly()
    b_poly = create_all_brackets_poly()
    
    # --------------------------------------------------------------------------
    # Panel 1: Original Position Layout (Left: X=-7.85, Right: X=+8.45)
    # --------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#fafafa')
    ax1.plot(bx, by, color='#1565c0', lw=2.2, label='Perimeter Wall')
    
    shroud_left = box(CX_LEFT - BODY_W_BASE/2, CY_SLIT - BODY_L_BASE/2, CX_LEFT + BODY_W_BASE/2, CY_SLIT + BODY_L_BASE/2)
    shroud_right = box(CX_RIGHT - BODY_W_BASE/2, CY_SLIT - BODY_L_BASE/2, CX_RIGHT + BODY_W_BASE/2, CY_SLIT + BODY_L_BASE/2)
    
    ax1.fill(*shroud_left.exterior.xy, color='#ab47bc', alpha=0.45, edgecolor='#6a1b9a', lw=1.5, label='Left Slit (X=-7.85)')
    ax1.fill(*shroud_right.exterior.xy, color='#ab47bc', alpha=0.45, edgecolor='#6a1b9a', lw=1.5, label='Right Slit (X=+8.45)')
    
    sock_left = box(CX_LEFT - SOCKET_W/2, CY_SLIT - SOCKET_L/2, CX_LEFT + SOCKET_W/2, CY_SLIT + SOCKET_L/2)
    sock_right = box(CX_RIGHT - SOCKET_W/2, CY_SLIT - SOCKET_L/2, CX_RIGHT + SOCKET_W/2, CY_SLIT + SOCKET_L/2)
    
    ax1.plot(*sock_left.exterior.xy, color='#d32f2f', lw=1.8, label='Sockets (2.4x4.7mm)')
    ax1.plot(*sock_right.exterior.xy, color='#d32f2f', lw=1.8)
    
    ax1.plot(*arch_poly.exterior.xy, color='#0d47a1', lw=1.6)
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        ax1.plot(*g.exterior.xy, color='#2e7d32', lw=1.2, ls='--')
        
    ax1.set_xlim(-15.5, 15.5)
    ax1.set_ylim(-20.5, -4.5)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('1. Slits at Exact OEM Positions', fontsize=11, fontweight='bold', pad=8)
    ax1.set_xlabel('X (mm)', fontsize=9)
    ax1.set_ylabel('Y (mm)', fontsize=9)
    ax1.legend(loc='upper right', fontsize=7.5)
    
    # --------------------------------------------------------------------------
    # Panel 2: Inner Wall Relief Fix (Resolving the Wall Overhang Interference)
    # --------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#ffffff')
    ax2.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    
    inner_poly_raw = outer_body_poly.buffer(-OUTER_WALL_THICK)
    ax2.plot(*inner_poly_raw.exterior.xy, color='#d32f2f', ls=':', lw=2.0, label='Old Wall (Overhung Socket!)')
    
    wall_poly_raw = outer_body_poly.difference(inner_poly_raw)
    socket_relief_zone = unary_union([sock_left.buffer(0.40), sock_right.buffer(0.40)])
    wall_poly_relieved = wall_poly_raw.difference(socket_relief_zone)
    for geom in (wall_poly_relieved.geoms if hasattr(wall_poly_relieved, 'geoms') else [wall_poly_relieved]):
        ax2.plot(*geom.exterior.xy, color='#2e7d32', lw=1.8)
        
    ax2.fill(*sock_right.exterior.xy, color='#ffcdd2', edgecolor='#d32f2f', lw=2.0, label='Right Detent Socket (X=+8.45)')
    ax2.plot(*shroud_right.exterior.xy, color='#7b1fa2', ls='--', lw=1.8, label='Insert Base (2.7x4.8mm)')
    
    shroud_right_tip = box(CX_RIGHT - BODY_W_TIP/2, CY_SLIT - BODY_L_TIP/2, CX_RIGHT + BODY_W_TIP/2, CY_SLIT + BODY_L_TIP/2)
    ax2.plot(*shroud_right_tip.exterior.xy, color='#4a148c', ls='-', lw=2.0, label='Sloped Tip (2.2x4.2mm)')
    
    ax2.annotate('Relieved Inner Wall\n(Zero Vertical Overhang)', xy=(8.453, -15.5), xytext=(3.0, -17.5),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=7.5, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32', lw=0.8))
                 
    ax2.set_xlim(2.5, 15.5)
    ax2.set_ylim(-19.5, -9.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('2. Inner Wall Relief at X = +8.45mm', fontsize=11, fontweight='bold', pad=8)
    ax2.set_xlabel('X (mm)', fontsize=9)
    ax2.set_ylabel('Y (mm)', fontsize=9)
    ax2.legend(loc='lower left', fontsize=7.0)
    
    # --------------------------------------------------------------------------
    # Panel 3: 3D Sloped Slit Insert (2.20mm Wide End + Tapered Key)
    # --------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[2], projection='3d')
    ax3.set_facecolor('#ffffff')
    
    insert_mesh = build_sloped_insert_solid()
    v = insert_mesh.vertices
    f = insert_mesh.faces
    
    poly3d = Poly3DCollection(v[f], facecolor='#ab47bc', edgecolor='#4a148c', linewidths=0.4, alpha=0.85)
    ax3.add_collection3d(poly3d)
    
    ax3.set_xlim(-2.8, 2.8)
    ax3.set_ylim(-3.2, 3.2)
    ax3.set_zlim(0.0, 3.8)
    ax3.view_init(elev=26, azim=-45)
    ax3.set_title('3. 3D Sloped Insert (2.2mm End)', fontsize=11, fontweight='bold', pad=8)
    ax3.set_xlabel('X (mm)', fontsize=8)
    ax3.set_ylabel('Y (mm)', fontsize=8)
    ax3.set_zlabel('Z (mm)', fontsize=8)
    
    # --------------------------------------------------------------------------
    # Panel 4: Cross-Section Fit Diagram (Insert Seating in Floor)
    # --------------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[3])
    ax4.set_facecolor('#ffffff')
    
    # Baseplate Floor (Z in [0, 1.0mm], with socket cutout X in [-1.20, +1.20])
    ax4.fill([-5.5, -SOCKET_W/2, -SOCKET_W/2, -5.5], [0.0, 0.0, 1.0, 1.0], color='#cfd8dc', edgecolor='#455a64', lw=1.5, label='Baseplate Floor (1.0mm)')
    ax4.fill([SOCKET_W/2, 5.5, 5.5, 1.25], [0.0, 0.0, 1.0, 1.0], color='#cfd8dc', edgecolor='#455a64', lw=1.5)
    
    # Insert Shroud Body (Z in [-2.47, 0.0], 2.20mm at tip, 2.70mm at base) & Tapered Key (Z in [0, 0.85])
    ax4.fill([-BODY_W_TIP/2, -SLIT_W/2, -SLIT_W/2, -KEY_W_TOP/2, -KEY_W_BASE/2, -BODY_W_BASE/2],
             [-SLIT_BOSS_HEIGHT, -SLIT_BOSS_HEIGHT, KEY_H, KEY_H, 0.0, 0.0],
             color='#ba68c8', edgecolor='#6a1b9a', lw=1.8, label='Sloped Insert (2.2mm Tip)')
    ax4.fill([SLIT_W/2, BODY_W_TIP/2, BODY_W_BASE/2, KEY_W_BASE/2, KEY_W_TOP/2, SLIT_W/2],
             [-SLIT_BOSS_HEIGHT, -SLIT_BOSS_HEIGHT, 0.0, 0.0, KEY_H, KEY_H],
             color='#ba68c8', edgecolor='#6a1b9a', lw=1.8)
             
    # Annotations
    ax4.annotate('Tapered Key in Socket\n(0.25mm Clearance / side)', xy=(1.0, 0.5), xytext=(2.0, 1.4),
                 arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.4), fontsize=7.5, fontweight='bold', color='#d32f2f',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#d32f2f', lw=0.8))
                 
    ax4.annotate('2.20mm Wide End Tip\n(15.8° Sloped Walls)', xy=(BODY_W_TIP/2, -1.2), xytext=(2.2, -1.7),
                 arrowprops=dict(arrowstyle='->', color='#6a1b9a', lw=1.4), fontsize=7.5, fontweight='bold', color='#6a1b9a',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#6a1b9a', lw=0.8))
                 
    ax4.annotate('Expanded Slit\n(1.35x3.65mm)', xy=(0.0, -1.0), xytext=(-2.5, -1.7),
                 ha='center', fontsize=7.0, fontweight='bold', color='#0d47a1',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#0d47a1', lw=0.8))
                 
    ax4.set_xlim(-4.2, 4.2)
    ax4.set_ylim(-3.0, 2.2)
    ax4.set_aspect('equal')
    ax4.grid(True, linestyle=':', alpha=0.6)
    ax4.set_title('4. Cross-Section Seating & Tolerances', fontsize=11, fontweight='bold', pad=8)
    ax4.set_xlabel('X (mm)', fontsize=9)
    ax4.set_ylabel('Z (mm)', fontsize=9)
    ax4.legend(loc='lower left', fontsize=7.0)
    
    out_testing = os.path.join(os.path.dirname(__file__), 'slit_insert_fix_diagram.png')
    plt.savefig(out_testing, dpi=220)
    print(f"Saved polished diagram to: {out_testing}")
    
    artifact_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\f3d4a0c2-757f-4d9a-9b44-08845cae7d7f"
    if os.path.exists(artifact_dir):
        out_artifact = os.path.join(artifact_dir, 'slit_insert_fix_diagram.png')
        shutil.copy(out_testing, out_artifact)
        print(f"Copied polished diagram to artifact directory: {out_artifact}")

if __name__ == '__main__':
    generate_diagram()
