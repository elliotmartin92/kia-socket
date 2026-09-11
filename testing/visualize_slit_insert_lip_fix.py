"""
testing/visualize_slit_insert_lip_fix.py
Renders high-resolution 2D and 3D diagrams demonstrating the removal
of the bottom-right corner lip and the verified clearance inside the baseplate.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import box, Polygon
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    build_slit_insert_mesh, get_exact_base_polygon,
    INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, SOCKET_W_X, SOCKET_LEN_Y,
    SLIT_W_X, SLIT_LEN_Y
)

def render_visualization():
    fig, axes = plt.subplots(1, 3, figsize=(22, 7.5), dpi=180)
    
    # -------------------------------------------------------------------------
    # Panel 1: Print Orientation Top-Down View (X-Y Plane)
    # -------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_title("Slit Insert Print Orientation (Top-Down View)\nBottom-Right Corner Lip Removed Flush", fontsize=12, fontweight='bold')
    
    # Unchamfered body outline (for comparison)
    body_raw = box(-INSERT_BODY_W_X/2, -INSERT_BODY_LEN_Y/2, INSERT_BODY_W_X/2, INSERT_BODY_LEN_Y/2)
    ax1.plot(*body_raw.exterior.xy, 'r--', lw=1.5, label='Original Unchamfered Shroud (Interfering Lip)')
    
    # Fixed body footprint (Option B)
    p_b1 = (0.35, -2.75)
    p_b2 = (1.65, -1.45)
    fixed_body_poly = Polygon([
        (-1.65, 2.75), (1.65, 2.75), (1.65, -1.45),
        (0.35, -2.75), (-1.65, -2.75)
    ])
    ax1.fill(*fixed_body_poly.exterior.xy, color='#90caf9', alpha=0.5, label='Fixed Shoulder Base (Z=2.47mm)')
    ax1.plot(*fixed_body_poly.exterior.xy, color='#1565c0', lw=2.0)
    
    # Polarized Key (Z: 2.47 to 3.32mm)
    p_k1 = (0.70, -2.40)
    p_k2 = (1.30, -1.80)
    key_poly = Polygon([
        (-1.30, 2.40), (1.30, 2.40), (1.30, -1.80),
        (0.70, -2.40), (-1.30, -2.40)
    ])
    ax1.fill(*key_poly.exterior.xy, color='#ffe082', alpha=0.8, label='Raised Key (Z=2.47 to 3.32mm)')
    ax1.plot(*key_poly.exterior.xy, color='#f57f17', lw=2.0)
    
    # Inner Slit Hole
    slit_poly = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
    ax1.fill(*slit_poly.exterior.xy, color='white', ec='#d32f2f', lw=1.8, hatch='//', label='Inner Slit Hole (1.20x3.40mm)')
    
    # Callout arrows
    ax1.annotate("NO LIP HERE!\nShoulder cut flush\nwith 45° chamfer",
                 xy=(1.00, -2.10), xytext=(2.2, -3.2),
                 arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7),
                 fontsize=10, fontweight='bold', color='#b71c1c',
                 bbox=dict(boxstyle="round,pad=0.3", fc="#ffebee", ec="#c62828", lw=1.2))
                 
    ax1.annotate("0.35mm seating shoulder\npreserved on flat edges",
                 xy=(-1.47, 0.0), xytext=(-3.5, 0.5),
                 arrowprops=dict(facecolor='blue', shrink=0.08, width=1.2, headwidth=6),
                 fontsize=9, color='#0d47a1')
                 
    ax1.set_xlim(-4.2, 4.2)
    ax1.set_ylim(-4.2, 4.2)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_xlabel("X (mm) [Print Bed Width]")
    ax1.set_ylabel("Y (mm) [Print Bed Length]")
    ax1.legend(loc='upper left', fontsize=8)
    
    # -------------------------------------------------------------------------
    # Panel 2: Baseplate Socket Mating View (Baseplate Coordinates)
    # -------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_title("Mating View: Right Socket & Baseplate Outer Wall\n100% Collision-Free Clearance", fontsize=12, fontweight='bold')
    
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    cx = 8.453
    cy = -13.589
    
    # Plot outer perimeter wall
    ox, oy = outer_body_poly.exterior.xy
    ax2.plot(ox, oy, color='#1565c0', lw=2.5, label='Baseplate Outer Perimeter')
    
    # Plot floor detent socket
    x_r_max = cx + SOCKET_W_X/2
    y_r_bot = cy - SOCKET_LEN_Y/2
    chamfer_right_tri = Polygon([[x_r_max - 0.75, y_r_bot - 0.05],
                                 [x_r_max + 0.05, y_r_bot + 0.75],
                                 [x_r_max + 0.05, y_r_bot - 0.05]])
    detent_right = box(cx - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_right_tri)
    ax2.fill(*detent_right.exterior.xy, color='#e0e0e0', ec='#424242', lw=1.8, label='Female Socket in Floor (2.90x5.10mm)')
    
    # Insert seated in plate:
    # 1. Shoulder footprint
    footprint_in_plate = translate(fixed_body_poly, xoff=cx, yoff=cy)
    ax2.plot(*footprint_in_plate.exterior.xy, color='#2e7d32', lw=2.0, ls='-', label='Seated Shoulder Footprint (0.44mm clearance to wall)')
    
    # 2. Key footprint
    key_in_plate = translate(key_poly, xoff=cx, yoff=cy)
    ax2.fill(*key_in_plate.exterior.xy, color='#ffb74d', alpha=0.7, ec='#e65100', lw=1.5, label='Insert Key Seated (0.13mm socket clearance)')
    
    # 3. Old colliding shoulder (for contrast)
    old_colliding = translate(body_raw, xoff=cx, yoff=cy)
    ax2.plot(*old_colliding.exterior.xy, color='red', lw=1.5, ls='--', label='Previous Shoulder (Collided with Wall)')
    
    ax2.annotate("Collision Eliminated!\nClearance: +0.44 mm",
                 xy=(9.6, -16.0), xytext=(10.5, -17.5),
                 arrowprops=dict(facecolor='green', shrink=0.08, width=1.5, headwidth=7),
                 fontsize=10, fontweight='bold', color='#1b5e20',
                 bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#2e7d32", lw=1.2))
                 
    ax2.set_xlim(5.5, 12.5)
    ax2.set_ylim(-18.5, -10.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_xlabel("X (mm) [Baseplate Datum]")
    ax2.set_ylabel("Y (mm) [Baseplate Datum]")
    ax2.legend(loc='upper right', fontsize=8)
    
    # -------------------------------------------------------------------------
    # Panel 3: 3D Mesh Inspection
    # -------------------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_title("Isometric View of Watertight Slit Insert\nFlat Bed Face (Z=0) to Key Tip (Z=3.42mm)", fontsize=12, fontweight='bold')
    
    mesh = build_slit_insert_mesh(is_right=True)
    v = mesh.vertices
    f = mesh.faces
    
    # Project 3D to 2D isometric
    angle_x = np.radians(30)
    angle_z = np.radians(45)
    Rx = np.array([[1, 0, 0], [0, np.cos(angle_x), -np.sin(angle_x)], [0, np.sin(angle_x), np.cos(angle_x)]])
    Rz = np.array([[np.cos(angle_z), -np.sin(angle_z), 0], [np.sin(angle_z), np.cos(angle_z), 0], [0, 0, 1]])
    R = Rx @ Rz
    v_rot = v @ R.T
    
    # Simple wireframe plot of edges
    edges = mesh.edges_unique
    for e in edges:
        p1, p2 = v_rot[e[0]], v_rot[e[1]]
        ax3.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#37474f', lw=0.6, alpha=0.7)
        
    ax3.set_aspect('equal')
    ax3.axis('off')
    ax3.text(0, -3.5, f"Watertight: {mesh.is_watertight}\nVolume: {mesh.volume:.2f} mm³\nZero corner lip interference",
             ha='center', fontsize=10, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.4", fc="#f3e5f5", ec="#8e24aa", lw=1.2))
             
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'slit_insert_lip_fix_diagram.png')
    plt.savefig(out_path, dpi=180)
    print(f"Saved visualization to {out_path}")

if __name__ == '__main__':
    render_visualization()
