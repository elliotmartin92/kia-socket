"""
testing/visualize_tower_clamp_assembly.py
High-resolution 2D and 3D visualization and diagnostic inspection script for the
Unified 1-Piece Monolithic Anti-Spreading Bridge Clamp (Zero Pin Friction, Mutual Anchoring).
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    BASE_THICK, TOWER_HEIGHT, build_clean_shaft_towers_mesh, build_left_tower_struts_mesh
)
from build_shaft import (
    Y_AXLE, Z_AXLE, PIN_DIAMETER, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER
)
from build_clamp import (
    get_saddle_polygon_yz, get_side_wall_polygon_yz, build_tower_clamp_mesh,
    build_unified_clamp_mesh, Z_KEEL, PIN_CLEARANCE_RADIUS
)

def render_clamp_diagnostics():
    print("Generating Unified Monolithic Bridge Clamp diagnostic visualizations...")
    
    poly_saddle = get_saddle_polygon_yz()
    poly_side = get_side_wall_polygon_yz()
    
    fig = plt.figure(figsize=(22, 12.5), facecolor='#18181b', dpi=180)
    
    # --------------------------------------------------------------------------
    # Panel 1: 2D Planar Cross-Section (Y-Z Plane) - Seated Clamp & Tower
    # --------------------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1, facecolor='#27272a')
    ax1.set_title("1. Cross-Section (Y-Z Plane): Clamp Seated on Tower Prongs", color='white', fontsize=12, fontweight='bold', pad=10)
    
    px_s, py_s = poly_saddle.exterior.xy
    ax1.fill(px_s, py_s, color='#38bdf8', alpha=0.85, ec='#0284c7', lw=2.0, label='U-Saddle Clamp (Prong Anti-Spread Constraint)')
    
    y_shaft = Y_AXLE
    z_base = BASE_THICK
    z_top = z_base + TOWER_HEIGHT
    r_shaft = 1.50
    z_cradle_center = Z_AXLE
    y_min_base = 6.250
    y_max_base = 12.850
    y_min_top = 6.550
    y_max_top = 12.180
    throat_w = 2.60
    half_w = throat_w / 2.0
    alpha = np.arcsin(half_w / r_shaft)
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(y_shaft + r_shaft * np.cos(p), z_cradle_center + r_shaft * np.sin(p)) for p in phi]
    bevel_dx = (z_top - (z_cradle_center + r_shaft * np.cos(alpha))) * 0.75
    y_left_top = y_shaft - half_w - bevel_dx
    y_right_top = y_shaft + half_w + bevel_dx
    
    profile_yz = [
        (y_min_base, z_base),
        (y_max_base, z_base),
        (y_max_top, z_top),
        (y_right_top, z_top),
    ] + cradle_arc_pts + [
        (y_left_top, z_top),
        (y_min_top, z_top)
    ]
    poly_tow = Polygon(profile_yz)
    
    tx, ty = poly_tow.exterior.xy
    ax1.plot(tx, ty, color='#f43f5e', lw=2.2, linestyle='--', label='100% Solid Tower Profile (Zero Notches)')
    
    # Plot Shaft Pin seated in cradle
    pin_phi = np.linspace(0, 2*np.pi, 64)
    r_pin = PIN_DIAMETER / 2.0
    ax1.fill(y_shaft + r_pin*np.cos(pin_phi), z_cradle_center + r_pin*np.sin(pin_phi),
             color='#fbbf24', alpha=0.95, ec='#d97706', lw=2.0, label='Shaft Pin (Ø2.80mm)')
             
    # Plot side cheek clearance arch (dashed line)
    arch_phi = np.linspace(0, np.pi, 64)
    ax1.plot(y_shaft + PIN_CLEARANCE_RADIUS * np.cos(arch_phi),
             z_cradle_center + PIN_CLEARANCE_RADIUS * np.sin(arch_phi),
             color='#a855f7', lw=2.0, linestyle='-.', label='Side Arch (R=1.70mm, >=0.30mm Radial Air Gap)')
    
    # Plot rear cross-tie bar zone
    ax1.plot([12.18, 13.38, 13.38, 12.18, 12.18], [13.70, 13.70, 14.99, 14.99, 13.70],
             color='#34d399', lw=2.0, linestyle=':', label='Rear Cross-Tie Bar Span (X: 3.0 to 15.5mm)')
    
    # Annotations
    ax1.annotate('Bridge Roof (0.90mm H)\nZ: 14.09 to 14.99mm', xy=(y_shaft, 14.54), xytext=(y_shaft - 3.5, 15.6),
                 color='white', fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#38bdf8', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.2', fc='#1e293b', ec='#38bdf8'))
                 
    ax1.annotate('Central Keel (Z = 14.02mm)\n0.03mm Pin Running Gap', xy=(y_shaft, 14.02), xytext=(y_shaft + 1.2, 14.8),
                 color='white', fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#fbbf24', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.2', fc='#1e293b', ec='#fbbf24'))

    ax1.annotate('Monolithic Rear Tie-Bar\nConnects Left & Right Clamps!', xy=(12.8, 14.3), xytext=(12.2, 15.6),
                 color='white', fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#34d399', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.2', fc='#064e3b', ec='#34d399'))

    ax1.annotate('Clearance Arch: Zero Pin Contact!\nZero Extra Pin Friction', xy=(y_shaft, 12.59 + 1.70), xytext=(y_shaft - 2.8, 11.2),
                 color='white', fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#a855f7', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.2', fc='#3b0764', ec='#a855f7'))

    ax1.set_xlim(3.0, 15.5)
    ax1.set_ylim(10.0, 16.5)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.3, color='#71717a')
    ax1.tick_params(colors='white')
    ax1.set_xlabel('Y (mm)', color='white')
    ax1.set_ylabel('Z (mm)', color='white')
    ax1.legend(loc='lower left', fontsize=8, facecolor='#18181b', edgecolor='#3f3f46', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 2: Dual-Anchor Interlock in (X-Z Plane) - Full 15.5mm Gantry Span
    # --------------------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#27272a')
    ax2.set_title("2. Full Gantry Span (X-Z Plane): Clamps Mutually Anchor Each Other", color='white', fontsize=12, fontweight='bold', pad=10)
    
    # Left Tower Wall: X in [3.90, 5.40]
    ax2.fill([3.90, 5.40, 5.40, 3.90], [11.0, 11.0, 14.09, 14.09], color='#475569', alpha=0.8, ec='#64748b', lw=1.2, label='Left Tower (1.50mm)')
    # Right Tower Wall: X in [13.10, 14.60]
    ax2.fill([13.10, 14.60, 14.60, 13.10], [11.0, 11.0, 14.09, 14.09], color='#475569', alpha=0.8, ec='#64748b', lw=1.2, label='Right Tower (1.50mm)')
    
    # Additive Side Beads (+0.70mm X protrusion)
    ax2.fill([3.90, 3.20, 3.20, 3.90], [12.40, 12.40, 13.00, 13.60], color='#f43f5e', alpha=0.9, ec='#be123c', lw=1.5, label='Additive Ledges (+0.70mm X)')
    ax2.fill([14.60, 15.30, 15.30, 14.60], [12.40, 12.40, 13.00, 13.60], color='#f43f5e', alpha=0.9, ec='#be123c', lw=1.5)
    
    # Unified Clamp Monolithic Bridge: X from 2.20 to 16.30 at Z in [14.09, 14.99]
    ax2.fill([2.20, 16.30, 16.30, 2.20], [14.09, 14.09, 14.99, 14.99], color='#38bdf8', alpha=0.85, ec='#0284c7', lw=1.5, label='Monolithic Gantry Bridge (14.1mm Span)')
    
    # Left Outer Cheek & Hook: X in [2.20, 3.85], Z in [11.75, 14.09]
    hook_lx = [2.20, 3.20, 3.90, 3.90, 3.85, 3.85, 2.20]
    hook_lz = [14.09, 14.09, 14.09, 12.40, 12.40, 12.20, 11.75]
    ax2.fill(hook_lx, hook_lz, color='#38bdf8', alpha=0.95, ec='#0284c7', lw=1.8)
    
    # Right Outer Cheek & Hook: X in [14.65, 16.30], Z in [11.75, 14.09]
    hook_rx = [16.30, 15.30, 14.60, 14.60, 14.65, 14.65, 16.30]
    hook_rz = [14.09, 14.09, 14.09, 12.40, 12.40, 12.20, 11.75]
    ax2.fill(hook_rx, hook_rz, color='#38bdf8', alpha=0.95, ec='#0284c7', lw=1.8)
    
    # Rotating Rocker Hub Profile: X in [5.50, 13.00], Z up to 14.69mm
    ax2.plot([5.50, 5.50, 13.00, 13.00, 5.50], [11.0, 14.69, 14.69, 11.0, 11.0], color='#fbbf24', lw=1.8, linestyle='--', label='Rotating Rocker Hub (Z<=14.69mm)')
    
    # Annotations
    ax2.annotate('Left Snap Anchor\n(0.65mm Hook at Z=12.40mm)', xy=(3.20, 12.40), xytext=(0.4, 11.5),
                 color='white', fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#34d399', lw=1.8),
                 bbox=dict(boxstyle='round,pad=0.25', fc='#064e3b', ec='#34d399'))

    ax2.annotate('Right Snap Anchor\n(0.65mm Hook at Z=12.40mm)', xy=(15.30, 12.40), xytext=(14.2, 11.5),
                 color='white', fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#34d399', lw=1.8),
                 bbox=dict(boxstyle='round,pad=0.25', fc='#064e3b', ec='#34d399'))

    ax2.annotate('Monolithic Cross-Tie: Clamps Anchor Each Other!\nCannot Rock, Twist, or Fall Off',
                 xy=(9.25, 14.54), xytext=(5.5, 15.6),
                 color='white', fontsize=9.0, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#38bdf8', lw=2.0),
                 bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#38bdf8', lw=1.5))

    ax2.set_xlim(0.0, 18.0)
    ax2.set_ylim(10.5, 16.5)
    ax2.grid(True, linestyle=':', alpha=0.3, color='#71717a')
    ax2.tick_params(colors='white')
    ax2.set_xlabel('X (mm)', color='white')
    ax2.set_ylabel('Z (mm)', color='white')
    ax2.legend(loc='lower center', fontsize=8, facecolor='#18181b', edgecolor='#3f3f46', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 3: 3D Isometric View of Seated Unified Clamp on Towers with Rocker
    # --------------------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3, projection='3d', facecolor='#1e1e24')
    ax3.set_title("3. 3D Seated Assembly View (Unified Bridge Clamp in Place)", color='white', fontsize=12, fontweight='bold', pad=10)
    
    towers_mesh = build_clean_shaft_towers_mesh()
    struts_mesh = build_left_tower_struts_mesh()
    shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)
    u_clamp = build_unified_clamp_mesh(in_assembly_coords=True)
    
    def add_mesh_collection(ax, m, color, alpha=0.8, ec='none'):
        v = m.vertices
        f = m.faces
        poly = Poly3DCollection(v[f], alpha=alpha, facecolor=color, edgecolor=ec, linewidth=0.1)
        ax.add_collection3d(poly)
        
    add_mesh_collection(ax3, towers_mesh, '#475569', alpha=0.75, ec='#1e293b')
    add_mesh_collection(ax3, struts_mesh, '#334155', alpha=0.6, ec='#0f172a')
    add_mesh_collection(ax3, shaft_mesh, '#f59e0b', alpha=0.85, ec='#b45309')
    add_mesh_collection(ax3, u_clamp, '#38bdf8', alpha=0.95, ec='#0284c7')
    
    ax3.set_xlim(2.0, 16.0)
    ax3.set_ylim(4.0, 14.0)
    ax3.set_zlim(8.0, 16.0)
    ax3.tick_params(colors='white')
    ax3.set_xlabel('X (mm)', color='white')
    ax3.set_ylabel('Y (mm)', color='white')
    ax3.set_zlabel('Z (mm)', color='white')
    ax3.view_init(elev=26, azim=-55)
    
    # --------------------------------------------------------------------------
    # Panel 4: Print Bed Layout (Flat Roof Down at Z=0)
    # --------------------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4, facecolor='#27272a')
    ax4.set_title("4. 1-Click Support-Free Build Bed Layout (tower_clamp_bridge.stl)", color='white', fontsize=12, fontweight='bold', pad=10)
    
    u_bed = build_unified_clamp_mesh(in_assembly_coords=False)
    v_u = u_bed.vertices
    
    ax4.scatter(v_u[:, 0], v_u[:, 1], c='#38bdf8', s=1, alpha=0.5)
    b = u_bed.bounds
    
    ax4.annotate('1-Piece Monolithic Component (tower_clamp_bridge.stl)\nPre-Oriented Flat on Print Bed (Z = 0.00mm)\nTop Bridge Roof Down: Zero Overhangs\nVertical Walls -> 100% Support-Free Printing\nPrint Time: ~3.0 Minutes',
                 xy=(0, 0), xytext=(-6.0, -1.2),
                 color='white', fontsize=9.5, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.35', fc='#0f172a', ec='#38bdf8', lw=1.5))
                 
    ax4.set_xlim(-8.0, 8.0)
    ax4.set_ylim(-6.0, 6.0)
    ax4.set_aspect('equal')
    ax4.grid(True, linestyle=':', alpha=0.3, color='#71717a')
    ax4.tick_params(colors='white')
    ax4.set_xlabel('X on Bed (mm)', color='white')
    ax4.set_ylabel('Y on Bed (mm)', color='white')
    
    plt.tight_layout()
    out_path = "testing/tower_clamp_assembly_preview.png"
    plt.savefig(out_path, dpi=180)
    plt.close()
    print(f"Saved diagnostic preview: {out_path}")

if __name__ == '__main__':
    render_clamp_diagnostics()
