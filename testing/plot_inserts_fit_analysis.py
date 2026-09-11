"""
testing/plot_inserts_fit_analysis.py
Generates a comprehensive multi-panel visual report of the insert fit:
1. 3D Assembled Overview (perspective view showing seated inserts).
2. Detail Z = 0.50mm: Left and Right Lip-in-Socket clearances.
3. Detail Z = 0.00mm: Shoulder seating footprint vs baseplate floor & perimeter.
4. Section View: Z stackup (floor thickness, lip depth, clearance margin).
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box
from shapely.affinity import translate, rotate

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK, BASE_THICK,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, INSERT_KEY_HEIGHT,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_CLEARANCE,
    INSERT_BODY_W_X, INSERT_BODY_LEN_Y, INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP,
    SLIT_W_X, SLIT_LEN_Y, SLIT_BOSS_HEIGHT
)

def generate_fit_plot():
    fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=150)
    fig.suptitle("Slit Inserts Fit & Assembly Clearance Analysis", fontsize=16, fontweight='bold', y=0.98)

    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    cx_left = -7.853
    cx_right = 8.453
    cy = -13.589

    # -------------------------------------------------------------
    # Panel 1: Full Baseplate Bottom View with Seated Inserts
    # -------------------------------------------------------------
    ax1 = axes[0, 0]
    ax1.set_title("1. Baseplate Underside with Seated Inserts (Z <= 0.00mm)", fontsize=12, fontweight='bold')
    
    # Baseplate perimeter
    bx, by = outer_body_poly.exterior.xy
    ax1.fill(bx, by, color='#e0e0e0', alpha=0.6, label='Baseplate Floor (Z=0)')
    ax1.plot(bx, by, color='#424242', lw=1.5)

    # Shrouds at Z = 0.00mm (shoulder)
    shroud_l = box(cx_left - INSERT_BODY_W_X/2, cy - INSERT_BODY_LEN_Y/2,
                   cx_left + INSERT_BODY_W_X/2, cy + INSERT_BODY_LEN_Y/2)
    shroud_r = box(cx_right - INSERT_BODY_W_X/2, cy - INSERT_BODY_LEN_Y/2,
                   cx_right + INSERT_BODY_W_X/2, cy + INSERT_BODY_LEN_Y/2)

    ax1.fill(*shroud_l.exterior.xy, color='#1976d2', alpha=0.7, label='Left Insert Body Shroud')
    ax1.plot(*shroud_l.exterior.xy, color='#0d47a1', lw=1.5)
    ax1.fill(*shroud_r.exterior.xy, color='#388e3c', alpha=0.7, label='Right Insert Body Shroud')
    ax1.plot(*shroud_r.exterior.xy, color='#1b5e20', lw=1.5)

    # Slit through-holes
    slit_l = box(cx_left - SLIT_W_X/2, cy - SLIT_LEN_Y/2, cx_left + SLIT_W_X/2, cy + SLIT_LEN_Y/2)
    slit_r = box(cx_right - SLIT_W_X/2, cy - SLIT_LEN_Y/2, cx_right + SLIT_W_X/2, cy + SLIT_LEN_Y/2)
    ax1.fill(*slit_l.exterior.xy, color='white', edgecolor='black', lw=1.2, label='1.2x3.4mm Through Slit')
    ax1.fill(*slit_r.exterior.xy, color='white', edgecolor='black', lw=1.2)

    ax1.set_aspect('equal')
    ax1.set_xlim(-24, 24)
    ax1.set_ylim(-20, 22)
    ax1.set_xlabel("X (mm)")
    ax1.set_ylabel("Y (mm)")
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, linestyle=':', alpha=0.5)

    # -------------------------------------------------------------
    # Panel 2: Left Insert Lip-in-Socket Fit (Z = 0.50mm)
    # -------------------------------------------------------------
    ax2 = axes[0, 1]
    ax2.set_title("2. Left Lip-in-Socket Fit (Z = 0.50mm) - Bottom-Left Chamfer", fontsize=12, fontweight='bold')

    # Left socket
    x_l_min = cx_left - SOCKET_W_X/2
    y_l_bot = cy - SOCKET_LEN_Y/2
    chamfer_l_sock = Polygon([[x_l_min + 0.75, y_l_bot - 0.05],
                              [x_l_min - 0.05, y_l_bot + 0.75],
                              [x_l_min - 0.05, y_l_bot - 0.05]])
    l_sock = box(cx_left - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2,
                 cx_left + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_l_sock)

    # Left key
    p1_l = [-INSERT_KEY_W_X/2 + 0.75, -INSERT_KEY_LEN_Y/2]
    p2_l = [-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + 0.75]
    chamfer_l_key = Polygon([[p1_l[0], p1_l[1] - 0.02],
                             [p2_l[0] - 0.02, p2_l[1]],
                             [p2_l[0] - 0.02, p1_l[1] - 0.02]])
    key_raw = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2)
    l_key = translate(key_raw.difference(chamfer_l_key), xoff=cx_left, yoff=cy)

    ax2.fill(*l_sock.exterior.xy, color='#ffcdd2', label=f'Floor Socket (2.90x5.10mm)')
    ax2.plot(*l_sock.exterior.xy, color='#c62828', lw=2)
    ax2.fill(*l_key.exterior.xy, color='#90caf9', label=f'Insert Lip (2.60x4.80mm)')
    ax2.plot(*l_key.exterior.xy, color='#1565c0', lw=2)
    ax2.fill(*slit_l.exterior.xy, color='white', edgecolor='black', lw=1.5, label='Slit (1.20x3.40mm)')

    # Clearance callouts
    ax2.annotate(f"0.15mm clearance\neverywhere", xy=(cx_left + INSERT_KEY_W_X/2, cy),
                 xytext=(cx_left + 2.2, cy + 1.0),
                 arrowprops=dict(arrowstyle="->", color='#2e7d32', lw=1.5),
                 fontsize=9, fontweight='bold', color='#2e7d32')
    ax2.annotate(f"0.75mm x 45°\nPolarized Chamfer", xy=(x_l_min + 0.35, y_l_bot + 0.35),
                 xytext=(cx_left - 3.2, cy - 2.8),
                 arrowprops=dict(arrowstyle="->", color='#d84315', lw=1.5),
                 fontsize=9, fontweight='bold', color='#d84315')

    ax2.set_aspect('equal')
    ax2.set_xlim(cx_left - 3.5, cx_left + 3.5)
    ax2.set_ylim(cy - 3.8, cy + 3.8)
    ax2.set_xlabel("X (mm)")
    ax2.set_ylabel("Y (mm)")
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, linestyle=':', alpha=0.5)

    # -------------------------------------------------------------
    # Panel 3: Right Insert Lip-in-Socket Fit (Z = 0.50mm)
    # -------------------------------------------------------------
    ax3 = axes[1, 0]
    ax3.set_title("3. Right Lip-in-Socket Fit (Z = 0.50mm) - Bottom-Right Chamfer", fontsize=12, fontweight='bold')

    # Right socket
    x_r_max = cx_right + SOCKET_W_X/2
    y_r_bot = cy - SOCKET_LEN_Y/2
    chamfer_r_sock = Polygon([[x_r_max - 0.75, y_r_bot - 0.05],
                              [x_r_max + 0.05, y_r_bot + 0.75],
                              [x_r_max + 0.05, y_r_bot - 0.05]])
    r_sock = box(cx_right - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2,
                 cx_right + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_r_sock)

    # Right key
    p1_r = [INSERT_KEY_W_X/2 - 0.75, -INSERT_KEY_LEN_Y/2]
    p2_r = [INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + 0.75]
    chamfer_r_key = Polygon([[p1_r[0], p1_r[1] - 0.02],
                             [p2_r[0] + 0.02, p2_r[1]],
                             [p2_r[0] + 0.02, p1_r[1] - 0.02]])
    r_key = translate(key_raw.difference(chamfer_r_key), xoff=cx_right, yoff=cy)

    ax3.fill(*r_sock.exterior.xy, color='#ffcdd2', label=f'Floor Socket (2.90x5.10mm)')
    ax3.plot(*r_sock.exterior.xy, color='#c62828', lw=2)
    ax3.fill(*r_key.exterior.xy, color='#a5d6a7', label=f'Insert Lip (2.60x4.80mm)')
    ax3.plot(*r_key.exterior.xy, color='#2e7d32', lw=2)
    ax3.fill(*slit_r.exterior.xy, color='white', edgecolor='black', lw=1.5, label='Slit (1.20x3.40mm)')

    # Wall boundary nearby
    coords = list(outer_body_poly.exterior.coords)
    wall_pts = [p for p in coords if -17 <= p[1] <= -10 and p[0] > 0]
    wx, wy = zip(*wall_pts)
    ax3.plot(wx, wy, color='#546e7a', lw=2.5, linestyle='--', label='Outer Perimeter Wall Edge')

    ax3.annotate(f"0.15mm clearance\nall around", xy=(cx_right - INSERT_KEY_W_X/2, cy),
                 xytext=(cx_right - 3.2, cy + 1.0),
                 arrowprops=dict(arrowstyle="->", color='#2e7d32', lw=1.5),
                 fontsize=9, fontweight='bold', color='#2e7d32')
    ax3.annotate(f"0.75mm x 45°\nPolarized Chamfer", xy=(x_r_max - 0.35, y_r_bot + 0.35),
                 xytext=(cx_right + 1.2, cy - 2.8),
                 arrowprops=dict(arrowstyle="->", color='#d84315', lw=1.5),
                 fontsize=9, fontweight='bold', color='#d84315')

    ax3.set_aspect('equal')
    ax3.set_xlim(cx_right - 3.5, cx_right + 3.5)
    ax3.set_ylim(cy - 3.8, cy + 3.8)
    ax3.set_xlabel("X (mm)")
    ax3.set_ylabel("Y (mm)")
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(True, linestyle=':', alpha=0.5)

    # -------------------------------------------------------------
    # Panel 4: Vertical Z-Axis Stackup Diagram
    # -------------------------------------------------------------
    ax4 = axes[1, 1]
    ax4.set_title("4. Vertical Z-Stackup (Cross-Section through Slit Center)", fontsize=12, fontweight='bold')

    # Baseplate floor from Z=0 to Z=1.00mm, with socket hole
    # Floor left slab: X from 4.0 to 8.453 - 2.90/2 = 7.003
    # Floor right slab: X from 8.453 + 2.90/2 = 9.903 to 13.0
    x_sock_l = cx_right - SOCKET_W_X/2
    x_sock_r = cx_right + SOCKET_W_X/2
    
    # Baseplate floor sections
    ax4.fill([4.0, x_sock_l, x_sock_l, 4.0], [0.0, 0.0, 1.0, 1.0], color='#bdbdbd', edgecolor='#424242', lw=1.5, label='Baseplate Floor (1.00mm)')
    ax4.fill([x_sock_r, 13.0, 13.0, x_sock_r], [0.0, 0.0, 1.0, 1.0], color='#bdbdbd', edgecolor='#424242', lw=1.5)
    
    # Outer wall rising above floor (X from 10.5 to 13.0, Z from 1.0 to 4.0)
    ax4.fill([10.5, 13.0, 13.0, 10.5], [1.0, 1.0, 3.5, 3.5], color='#78909c', edgecolor='#37474f', lw=1.5, label='Outer Perimeter Wall')

    # Insert body below floor (Z from -2.47 to 0.00mm)
    # Tapers from tip (X: 8.453 +/- 1.20 = [7.253, 9.653]) to shoulder (X: 8.453 +/- 1.65 = [6.803, 10.103])
    x_tip_l = cx_right - INSERT_BODY_W_TIP/2
    x_tip_r = cx_right + INSERT_BODY_W_TIP/2
    x_sh_l = cx_right - INSERT_BODY_W_X/2
    x_sh_r = cx_right + INSERT_BODY_W_X/2
    
    # Insert Lip (Z from 0.00 to 0.85mm, X from 8.453 +/- 1.30 = [7.153, 9.753])
    x_lip_l = cx_right - INSERT_KEY_W_X/2
    x_lip_r = cx_right + INSERT_KEY_W_X/2

    # Draw Insert as single poly with slit cutout
    ins_poly_x = [x_sh_l, x_lip_l, x_lip_l, cx_right - SLIT_W_X/2, cx_right - SLIT_W_X/2,
                  cx_right + SLIT_W_X/2, cx_right + SLIT_W_X/2, x_lip_r, x_lip_r, x_sh_r,
                  x_tip_r, cx_right + SLIT_W_X/2, cx_right + SLIT_W_X/2,
                  cx_right - SLIT_W_X/2, cx_right - SLIT_W_X/2, x_tip_l]
    ins_poly_z = [0.0, 0.0, 0.85, 0.85, -2.47,
                  -2.47, 0.85, 0.85, 0.0, 0.0,
                  -2.47, -2.47, -2.47,
                  -2.47, -2.47, -2.47]

    ax4.fill([x_sh_l, x_lip_l, x_lip_l, x_lip_r, x_lip_r, x_sh_r, x_tip_r, x_tip_l],
             [0.0, 0.0, 0.85, 0.85, 0.0, 0.0, -2.47, -2.47],
             color='#66bb6a', alpha=0.7, edgecolor='#1b5e20', lw=1.8, label='Seated Slit Insert')

    # Through slit hole
    ax4.fill([cx_right - SLIT_W_X/2, cx_right + SLIT_W_X/2, cx_right + SLIT_W_X/2, cx_right - SLIT_W_X/2],
             [-2.47, -2.47, 0.85, 0.85], color='white', edgecolor='black', lw=1.2, label='1.20mm Through Slit')

    # Dimensions & Annotations
    ax4.annotate("Flush Seating Shoulder\n(Z = 0.00mm)", xy=(x_sh_l + 0.15, 0.0), xytext=(4.5, -1.0),
                 arrowprops=dict(arrowstyle="->", color='#1565c0', lw=1.5),
                 fontsize=9, fontweight='bold', color='#1565c0')
    ax4.annotate("Lip Height = 0.85mm\n(0.15mm floor recess)", xy=(x_lip_r, 0.85), xytext=(10.5, 0.4),
                 arrowprops=dict(arrowstyle="->", color='#e65100', lw=1.5),
                 fontsize=9, fontweight='bold', color='#e65100')
    ax4.annotate("Shroud Height = 2.47mm\n(15.8° Draft Angle)", xy=(x_tip_l + 0.1, -1.5), xytext=(4.5, -2.0),
                 arrowprops=dict(arrowstyle="->", color='#2e7d32', lw=1.5),
                 fontsize=9, fontweight='bold', color='#2e7d32')

    ax4.axhline(0.0, color='gray', linestyle=':', alpha=0.7)
    ax4.axhline(1.0, color='gray', linestyle=':', alpha=0.7)

    ax4.set_xlim(3.5, 13.5)
    ax4.set_ylim(-3.0, 4.0)
    ax4.set_xlabel("X (mm)")
    ax4.set_ylabel("Z (mm)")
    ax4.legend(loc='upper left', fontsize=8)
    ax4.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'inserts_fit_analysis.png')
    plt.savefig(out_path, dpi=150)
    print(f"Saved fit analysis diagram to {out_path}")

if __name__ == '__main__':
    generate_fit_plot()
