"""
testing/render_support_updates_inspection.py
Visual verification render of:
1. Bottom snap clip 45° support showing the 0.28mm release gap under the shelf.
2. Insert backside breakaway struts showing the 0.28mm sloped release gap.
3. Plunger fork support protruding from base pad (Z=0.60mm) supporting both lateral edges.
4. Cantilever fork support rising from floor with easy-snap neck supporting both lateral edges.
"""

import sys, os
import matplotlib.pyplot as plt
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import build_shaft

def render_support_inspection():
    fig = plt.figure(figsize=(24, 6.5), dpi=150)

    # -------------------------------------------------------------
    # Panel 1: Bottom Clip 45° Support Profile with 0.28mm Gap
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(1, 4, 1)
    stem_h = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT  # 4.97 mm
    hook_depth = build_part.CLIP_HOOK_DEPTH            # 1.85 mm
    half_w = build_part.CLIP_ARM_WIDTH / 2.0           # 2.10 mm
    z_stem = stem_h - hook_depth                       # 3.12 mm
    clip_release_gap = 0.28
    z_shelf_contact = stem_h - clip_release_gap        # 4.69 mm
    yo = 1.20
    eff_depth = hook_depth - build_part.CLIP_CROWN_EASE * ((abs(yo) / half_w) ** 2.0)

    clip_r = [0.0, eff_depth, eff_depth, 0.0]
    clip_z = [stem_h, stem_h, stem_h + 1.80, stem_h + 1.80]
    ax1.plot(clip_r, clip_z, 'r-', lw=2.5, label='Clip Shelf (Z = 4.97mm)')
    ax1.fill_between([0.0, eff_depth], [stem_h, stem_h], [stem_h + 1.80, stem_h + 1.80], color='red', alpha=0.15)

    pts_rz = np.array([
        (-0.25, z_stem - 0.25),
        (-0.25, z_stem + 0.15),
        (0.00,  z_stem + 0.15),
        (eff_depth - 0.35, z_shelf_contact),
        (eff_depth, z_shelf_contact),
        (eff_depth, z_shelf_contact - 0.20),
        (0.00,  z_stem - 0.25),
        (-0.25, z_stem - 0.25),
    ])
    ax1.plot(pts_rz[:, 0], pts_rz[:, 1], 'g-', lw=2, label='45° Breakaway Strut')
    ax1.fill(pts_rz[:, 0], pts_rz[:, 1], color='lightgreen', alpha=0.5)

    ax1.annotate(f'Gap: {clip_release_gap:.2f}mm\n(Effortless snap-off)',
                 xy=(eff_depth / 2, z_shelf_contact), xytext=(eff_depth / 2 - 0.8, 3.9),
                 arrowprops=dict(facecolor='blue', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='blue', fontsize=9.5)
    ax1.axvline(0, color='gray', linestyle='--', label='Clip Stem Face')
    ax1.set_xlabel('Radial Depth (mm)', fontweight='bold')
    ax1.set_ylabel('Z Elevation (mm)', fontweight='bold')
    ax1.set_title('1. Clip Strut: 0.28mm Gap', fontweight='bold', fontsize=11.5)
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_xlim(-0.5, 2.2)
    ax1.set_ylim(2.5, 7.2)

    # -------------------------------------------------------------
    # Panel 2: Insert Backside Support with 0.28mm Gap
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(1, 4, 2)
    y_tip, z_tip = -9.418, 0.198
    y_floor, z_floor = -11.553, 1.556
    gap_insert = 0.28
    z_end_slope = z_floor - gap_insert

    ax2.plot([y_tip, y_floor], [z_tip, z_floor], 'r-', lw=3, label='Insert 32.5° Overhang')
    ax2.plot([y_floor, -12.5], [z_floor, z_floor + 0.947], 'r--', lw=1.5, label='Floor Backside')

    pts_insert_yz = np.array([
        (-11.55, 0.00),
        (-9.60,  0.00),
        (y_floor, z_end_slope),
        (-11.55, z_end_slope),
        (-11.55, 0.00),
    ])
    ax2.plot(pts_insert_yz[:, 0], pts_insert_yz[:, 1], 'g-', lw=2, label='Breakaway Strut (0.60mm W)')
    ax2.fill(pts_insert_yz[:, 0], pts_insert_yz[:, 1], color='lightgreen', alpha=0.5)
    ax2.axhline(0, color='black', lw=1.5, label='Print Bed (Z = 0.00mm)')

    ax2.annotate(f'Gap: {gap_insert:.2f}mm\n(Non-fusing overhang)',
                 xy=(-10.5, 0.70), xytext=(-12.3, 0.35),
                 arrowprops=dict(facecolor='blue', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='blue', fontsize=9.5)
    ax2.set_xlabel("Y' Tilted (mm)", fontweight='bold')
    ax2.set_ylabel("Z' Tilted (mm)", fontweight='bold')
    ax2.set_title('2. Slit Insert: 0.28mm Gap', fontweight='bold', fontsize=11.5)
    ax2.legend(loc='upper right', fontsize=8.5)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_xlim(-12.8, -9.0)
    ax2.set_ylim(-0.2, 2.8)

    # -------------------------------------------------------------
    # Panel 3: Plunger Fork Support & Shifted Back Fin (X-Z)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(1, 4, 3)
    p_x_c = 10.284
    p_y_c = 11.30
    z_plunger_lowest = 15.630
    gap_plunger = 0.28
    z_p_stick_top = z_plunger_lowest - gap_plunger  # 15.350mm
    z_bed = 0.60
    z_p_fork_base = 13.00
    z_p_notch = 13.80

    # Plunger blade edge (X in [8.484, 12.084], Z = 15.63mm)
    ax3.plot([8.484, 12.084], [z_plunger_lowest, z_plunger_lowest], 'r-', lw=4, label='Plunger Blade (X: 8.48-12.08mm)')
    ax3.fill_between([8.484, 12.084], [z_plunger_lowest, z_plunger_lowest], [17.5, 17.5], color='red', alpha=0.15)

    # 1. Base Bed Pad (Z: 0 to 0.60mm)
    ax3.fill_between([5.5, 13.0], 0, z_bed, color='darkgray', alpha=0.6, label='Bed Pad (Base Z=0.60mm)')
    
    # 2. Shifted Back Support Fin (shifted from X=+8.0mm to X=+6.80mm, X in [6.40, 7.20])
    ax3.fill_between([6.40, 7.20], z_bed, 16.5, color='royalblue', alpha=0.7, label='Shifted Back Fin (X=6.80mm)')
    ax3.axvline(7.61, color='gray', linestyle=':', label='Through-Hole Wall (X=7.61)')

    # 3. Central Trunk rising from base pad (1.80mm W)
    ax3.fill_between([p_x_c - 0.90, p_x_c + 0.90], z_bed, z_p_fork_base, color='lightgreen', alpha=0.8, label='Column from Base (1.8x1.8mm)')
    # 4. Plunger Fork Head with V-notch
    pts_p_fork = np.array([
        [8.484, z_p_fork_base],
        [8.484, z_p_stick_top],
        [9.284, z_p_stick_top],
        [p_x_c,  z_p_notch],
        [11.284, z_p_stick_top],
        [12.084, z_p_stick_top],
        [12.084, z_p_fork_base],
        [8.484, z_p_fork_base]
    ])
    ax3.plot(pts_p_fork[:, 0], pts_p_fork[:, 1], 'g-', lw=2.5, label='Fork Tines (Both Edges)')
    ax3.fill(pts_p_fork[:, 0], pts_p_fork[:, 1], color='forestgreen', alpha=0.6)

    ax3.annotate('Shifted from X=8.0\n+1.28mm Clearance\nto Lever Blade!', xy=(7.20, 15.0), xytext=(5.60, 15.6),
                 arrowprops=dict(facecolor='blue', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='blue', fontsize=8.5)
    ax3.annotate('Left Blade Tine\n(X: 8.48-9.28mm)', xy=(8.88, z_p_stick_top), xytext=(7.80, 17.0),
                 arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.2, headwidth=5),
                 fontweight='bold', color='darkgreen', fontsize=8.5)
    ax3.annotate('Right Blade Tine\n(X: 11.28-12.08mm)', xy=(11.68, z_p_stick_top), xytext=(11.10, 17.0),
                 arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.2, headwidth=5),
                 fontweight='bold', color='darkgreen', fontsize=8.5)
    ax3.annotate('2.00mm Open Window', xy=(p_x_c, z_p_notch), xytext=(8.80, 12.0),
                 arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.2, headwidth=5),
                 fontweight='bold', color='darkgreen', fontsize=8.5)

    ax3.set_xlabel('X Coordinate (mm)', fontweight='bold')
    ax3.set_ylabel("Z' Tilted (mm)", fontweight='bold')
    ax3.set_title('3. Plunger Fork & Shifted Fin (X-Z)', fontweight='bold', fontsize=11.5)
    ax3.legend(loc='lower right', fontsize=7.5)
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.set_xlim(5.4, 13.2)
    ax3.set_ylim(0.0, 18.5)

    # -------------------------------------------------------------
    # Panel 4: Cantilever Fork Support on Floor (X-Z)
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(1, 4, 4)
    cam_c_x = 6.600
    cam_c_y = -2.333
    z_cam_lowest = 17.988
    gap_cam = 0.28
    z_cam_stick_top = z_cam_lowest - gap_cam
    z_floor_cam = cam_c_y + 14.523

    # Lever Cam Tab Edge (X in [5.65, 7.55], Z = 17.988mm)
    ax4.plot([5.65, 7.55], [z_cam_lowest, z_cam_lowest], 'r-', lw=4, label='Cam Edge (1.90mm W)')
    ax4.fill_between([5.65, 7.55], [z_cam_lowest, z_cam_lowest], [19.0, 19.0], color='red', alpha=0.15)

    # Floor Neck
    ax4.fill_between([cam_c_x - 0.35, cam_c_x + 0.35], z_floor_cam - 0.30, z_floor_cam + 0.60, color='orange', alpha=0.9, label='Floor Neck (0.7x0.7mm)')
    # Trunk
    z_fork_base = 15.50
    ax4.fill_between([cam_c_x - 0.65, cam_c_x + 0.65], z_floor_cam + 0.60, z_fork_base, color='lightgreen', alpha=0.7, label='Trunk (1.30mm W)')
    # Fork Head
    z_notch = 16.30
    pts_fork_xz = np.array([
        [5.65, z_fork_base],
        [5.65, z_cam_stick_top],
        [6.15, z_cam_stick_top],
        [6.60, z_notch],
        [7.05, z_cam_stick_top],
        [7.55, z_cam_stick_top],
        [7.55, z_fork_base],
        [5.65, z_fork_base]
    ])
    ax4.plot(pts_fork_xz[:, 0], pts_fork_xz[:, 1], 'g-', lw=2.5, label='Fork Tines')
    ax4.fill(pts_fork_xz[:, 0], pts_fork_xz[:, 1], color='forestgreen', alpha=0.6)

    ax4.annotate('Left Tine (X=5.65)', xy=(5.90, z_cam_stick_top), xytext=(5.10, 18.3),
                 arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='darkgreen', fontsize=9)
    ax4.annotate('Right Tine (X=7.55)', xy=(7.30, z_cam_stick_top), xytext=(7.10, 18.3),
                 arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='darkgreen', fontsize=9)
    ax4.annotate('0.90mm Open Window', xy=(6.60, z_notch), xytext=(5.80, 14.8),
                 arrowprops=dict(facecolor='blue', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='blue', fontsize=9)

    ax4.set_xlabel('X Coordinate (mm)', fontweight='bold')
    ax4.set_ylabel("Z' Tilted (mm)", fontweight='bold')
    ax4.set_title('4. Cam Fork on Floor (X-Z)', fontweight='bold', fontsize=11.5)
    ax4.legend(loc='lower right', fontsize=8)
    ax4.grid(True, linestyle=':', alpha=0.6)
    ax4.set_xlim(4.8, 8.4)
    ax4.set_ylim(11.5, 19.5)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'support_updates_inspection.png')
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved {out_path} successfully!")

if __name__ == '__main__':
    render_support_inspection()
