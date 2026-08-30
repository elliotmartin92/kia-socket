"""
testing/generate_complete_bracket_update_diagram.py
Generates a comprehensive, publication-quality 4-panel visual diagram:
- Panel 1: Full Housing Top-Down Overview with Highlighted Bracket Pairs
- Panel 2: Left Bracket Pair (Brackets 1 & 2) with Looser Tolerances & 4 Sets of 1.15mm Seating Ribs (Rib 1 bottom corner meets hook corner at Y=4.95mm)
- Panel 3: Right Bracket Pair (Brackets 3 & 4) with Looser Tolerances & 4 Sets of 1.15mm Seating Ribs (Rib 1 bottom corner meets hook corner at Y=4.95mm)
- Panel 4: 3D Isometric View showing 1.15mm Elevation Profile & Seating Shelves
"""
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK, create_arch_wall_poly,
    create_center_curved_feature_poly, BASE_THICK, BRACKET_HEIGHT
)

# 1. Looser Bracket Coordinates
b1_looser_pts = [
    (-10.791,  7.136), (-8.000,  7.136), (-8.000,  4.950), (-8.900,  4.950),
    (-8.900,  6.400), (-9.857,  6.400), (-9.857, -6.200), (-8.150, -6.200),
    (-8.150, -7.171), (-10.791, -7.171), (-10.791,  7.136)
]

b2_looser_pts = [
    (-1.766,  7.171), (-4.500,  7.171), (-4.500,  4.950), (-3.650,  4.950),
    (-3.650,  6.400), (-2.701,  6.400), (-2.701, -6.200), (-4.350, -6.200),
    (-4.350, -7.136), (-1.766, -7.136), (-1.766,  7.171)
]

b3_looser_pts = [
    (1.766,  7.171), (4.500,  7.171), (4.500,  4.950), (3.650,  4.950),
    (3.650,  6.400), (2.701,  6.400), (2.701, -6.200), (4.350, -6.200),
    (4.350, -7.171), (1.766, -7.171), (1.766,  7.171)
]

b4_looser_pts = [
    (10.791,  7.171), (8.000,  7.171), (8.000,  4.950), (8.900,  4.950),
    (8.900,  6.400), (9.857,  6.400), (9.857, -6.200), (8.150, -6.200),
    (8.150, -7.136), (10.791, -7.136), (10.791,  7.171)
]

# 2. 1.15mm Tall Brass Seating Ribs (1.80mm extension, Rib 1 bottom corner meets hook corner at Y = 4.95mm)
BRACKET_SEATING_RIB_HEIGHT = 1.15
BRACKET_SEATING_RIB_EXT = 1.80
BRACKET_SEATING_RIB_THICK = 0.60
Y_RIB_POSITIONS = [5.25, 1.95, -1.35, -4.65]

def create_seating_ribs_poly(ext=BRACKET_SEATING_RIB_EXT, thick=BRACKET_SEATING_RIB_THICK):
    boxes = []
    # Left Pair
    b1_spine = -9.857
    b2_spine = -2.701
    # Right Pair
    b3_spine = 2.701
    b4_spine = 9.857
    
    for y in Y_RIB_POSITIONS:
        y_min = y - thick/2.0
        y_max = y + thick/2.0
        # Left pair: B1 (ext into +X), B2 (ext into -X)
        boxes.append(box(b1_spine, y_min, b1_spine + ext, y_max))
        boxes.append(box(b2_spine - ext, y_min, b2_spine, y_max))
        # Right pair: B3 (ext into +X), B4 (ext into -X)
        boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
        boxes.append(box(b4_spine - ext, y_min, b4_spine, y_max))
        
    return unary_union(boxes)

def generate_diagram():
    fig = plt.figure(figsize=(28, 9.5), dpi=200, facecolor='#ffffff')
    gs = fig.add_gridspec(1, 4, width_ratios=[1.0, 1.1, 1.1, 1.1], wspace=0.22, left=0.03, right=0.97, top=0.90, bottom=0.08)
    
    # --------------------------------------------------------------------------
    # Panel 1: Full Baseplate Housing Context
    # --------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor('#fafafa')
    
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    bx, by = outer_body_poly.exterior.xy
    ax1.plot(bx, by, color='#1565c0', lw=2.2, label='Perimeter Wall')
    
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        ax1.plot(ix, iy, color='#d32f2f', lw=1.2)
        
    arch_poly = create_arch_wall_poly()
    ax1.plot(*arch_poly.exterior.xy, color='#0d47a1', lw=1.6)
    
    curved_poly = create_center_curved_feature_poly()
    for geom in (curved_poly.geoms if hasattr(curved_poly, 'geoms') else [curved_poly]):
        ax1.fill(*geom.exterior.xy, color='#ce93d8', alpha=0.5)
        ax1.plot(*geom.exterior.xy, color='#8e24aa', lw=1.2)
        
    p1_new = Polygon(b1_looser_pts)
    p2_new = Polygon(b2_looser_pts)
    p3_new = Polygon(b3_looser_pts)
    p4_new = Polygon(b4_looser_pts)
    
    ax1.fill(*p1_new.exterior.xy, color='#1976d2', alpha=0.35)
    ax1.plot(*p1_new.exterior.xy, color='#0d47a1', lw=1.8)
    ax1.fill(*p2_new.exterior.xy, color='#388e3c', alpha=0.35)
    ax1.plot(*p2_new.exterior.xy, color='#1b5e20', lw=1.8)
    ax1.fill(*p3_new.exterior.xy, color='#388e3c', alpha=0.35)
    ax1.plot(*p3_new.exterior.xy, color='#1b5e20', lw=1.8)
    ax1.fill(*p4_new.exterior.xy, color='#1976d2', alpha=0.35)
    ax1.plot(*p4_new.exterior.xy, color='#0d47a1', lw=1.8)
    
    # Draw seating ribs
    seating_ribs = create_seating_ribs_poly()
    for geom in (seating_ribs.geoms if hasattr(seating_ribs, 'geoms') else [seating_ribs]):
        ax1.fill(*geom.exterior.xy, color='#d32f2f', alpha=0.85)
        
    # Envelopes
    rect_left = patches.Rectangle((-11.5, -8.0), 10.5, 16.0, fill=False, ec='#e65100', lw=2.0, ls='--')
    rect_right = patches.Rectangle((1.0, -8.0), 10.5, 16.0, fill=False, ec='#e65100', lw=2.0, ls='--')
    ax1.add_patch(rect_left)
    ax1.add_patch(rect_right)
    
    ax1.text(-6.28, 9.0, 'Left Pair\n(Panel 2)', color='#e65100', fontweight='bold', ha='center', fontsize=9,
             bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100', lw=0.8))
    ax1.text(6.28, 9.0, 'Right Pair\n(Panel 3)', color='#e65100', fontweight='bold', ha='center', fontsize=9,
             bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100', lw=0.8))
    
    ax1.set_xlim(-24, 24)
    ax1.set_ylim(-22, 23)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('1. Baseplate Overview', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('X (mm)', fontsize=9.5)
    ax1.set_ylabel('Y (mm)', fontsize=9.5)
    
    # --------------------------------------------------------------------------
    # Panel 2: Left Bracket Pair (Brackets 1 & 2) Close-Up
    # --------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor('#ffffff')
    
    p1_orig = Polygon(bracket_1_raw_pts)
    p2_orig = Polygon(bracket_2_raw_pts)
    
    brass_left_rect = patches.Rectangle((-6.28 - 3.37, -5.80), 6.74, 11.80,
                                        facecolor='#ffd54f', alpha=0.35, edgecolor='#f57f17', lw=1.8, ls='-', label='Brass Contact (6.74mm W)')
    ax2.add_patch(brass_left_rect)
    
    ax2.plot(*p1_orig.exterior.xy, color='#d32f2f', ls='--', lw=1.8, alpha=0.7, label='Previous Bracket (6.86mm Gap)')
    ax2.plot(*p2_orig.exterior.xy, color='#d32f2f', ls='--', lw=1.8, alpha=0.7)
    
    ax2.fill(*p1_new.exterior.xy, color='#1976d2', alpha=0.18)
    ax2.plot(*p1_new.exterior.xy, color='#0d47a1', lw=2.2, label='Looser Bracket (7.16mm Gap)')
    ax2.fill(*p2_new.exterior.xy, color='#388e3c', alpha=0.18)
    ax2.plot(*p2_new.exterior.xy, color='#1b5e20', lw=2.2)
    
    # Seating ribs
    for geom in (seating_ribs.geoms if hasattr(seating_ribs, 'geoms') else [seating_ribs]):
        gx, gy = geom.exterior.xy
        if max(gx) < 0:
            ax2.fill(gx, gy, color='#d32f2f', alpha=0.85, edgecolor='#b71c1c', lw=1.0, label='1.15mm Seating Rib (1.8mm ext)' if min(gy) < -4.0 else "")
            
    # Annotations
    ax2.annotate('', xy=(-9.857, 0.0), xytext=(-2.701, 0.0), arrowprops=dict(arrowstyle='<->', color='#0d47a1', lw=2.0))
    ax2.text((-9.857 + -2.701)/2, 0.3, 'Spine Gap: 7.16mm\n(+0.42mm Clearance)', ha='center', va='bottom',
             color='#0d47a1', fontweight='bold', fontsize=8, bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#0d47a1', lw=0.8))
    
    ax2.annotate('Rib 1 Bottom Corner Meets\nHook Corner at Y=4.95mm', xy=(-9.857 + 1.80, 4.95), xytext=(-12.3, 3.8),
                 arrowprops=dict(arrowstyle='->', color='#b71c1c', lw=1.5), fontsize=7.5, fontweight='bold', color='#b71c1c',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#b71c1c', lw=0.8))
    
    ax2.annotate('4x 1.15mm Tall Ribs\n(1.8mm ext from walls)', xy=(-9.857 + 1.80, 1.95), xytext=(-12.3, 1.8),
                 arrowprops=dict(arrowstyle='->', color='#b71c1c', lw=1.2), fontsize=7.5, fontweight='bold', color='#b71c1c',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#b71c1c', lw=0.8))
    
    ax2.annotate('Top Throat: 3.50mm (+0.32mm)', xy=(-6.28, 4.95), xytext=(-6.28, 5.7),
                 ha='center', fontsize=7.5, fontweight='bold', color='#e65100',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100', lw=0.8))
    
    ax2.set_xlim(-12.8, 0.2)
    ax2.set_ylim(-9.8, 9.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('2. Left Bracket Pair (Neutral)', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('X (mm)', fontsize=9.5)
    ax2.set_ylabel('Y (mm)', fontsize=9.5)
    ax2.legend(loc='lower left', fontsize=7.5)
    
    # --------------------------------------------------------------------------
    # Panel 3: Right Bracket Pair (Brackets 3 & 4) Close-Up
    # --------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[2])
    ax3.set_facecolor('#ffffff')
    
    p3_orig = Polygon(bracket_3_raw_pts)
    p4_orig = Polygon(bracket_4_raw_pts)
    
    brass_right_rect = patches.Rectangle((6.28 - 3.37, -5.80), 6.74, 11.80,
                                         facecolor='#ffd54f', alpha=0.35, edgecolor='#f57f17', lw=1.8, ls='-', label='Brass Contact (6.74mm W)')
    ax3.add_patch(brass_right_rect)
    
    ax3.plot(*p3_orig.exterior.xy, color='#d32f2f', ls='--', lw=1.8, alpha=0.7, label='Previous Bracket (6.86mm Gap)')
    ax3.plot(*p4_orig.exterior.xy, color='#d32f2f', ls='--', lw=1.8, alpha=0.7)
    
    ax3.fill(*p3_new.exterior.xy, color='#388e3c', alpha=0.18)
    ax3.plot(*p3_new.exterior.xy, color='#1b5e20', lw=2.2, label='Looser Bracket (7.16mm Gap)')
    ax3.fill(*p4_new.exterior.xy, color='#1976d2', alpha=0.18)
    ax3.plot(*p4_new.exterior.xy, color='#0d47a1', lw=2.2)
    
    # Seating ribs
    for geom in (seating_ribs.geoms if hasattr(seating_ribs, 'geoms') else [seating_ribs]):
        gx, gy = geom.exterior.xy
        if min(gx) > 0:
            ax3.fill(gx, gy, color='#d32f2f', alpha=0.85, edgecolor='#b71c1c', lw=1.0, label='1.15mm Seating Rib (1.8mm ext)' if min(gy) < -4.0 else "")
            
    # Annotations
    ax3.annotate('', xy=(2.701, 0.0), xytext=(9.857, 0.0), arrowprops=dict(arrowstyle='<->', color='#0d47a1', lw=2.0))
    ax3.text((2.701 + 9.857)/2, 0.3, 'Spine Gap: 7.16mm\n(+0.42mm Clearance)', ha='center', va='bottom',
             color='#0d47a1', fontweight='bold', fontsize=8, bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#0d47a1', lw=0.8))
    
    ax3.annotate('Rib 1 Bottom Corner Meets\nHook Corner at Y=4.95mm', xy=(9.857 - 1.80, 4.95), xytext=(8.0, 3.8),
                 arrowprops=dict(arrowstyle='->', color='#b71c1c', lw=1.5), fontsize=7.5, fontweight='bold', color='#b71c1c',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#b71c1c', lw=0.8))
    
    ax3.annotate('4x 1.15mm Tall Ribs\n(1.8mm ext from walls)', xy=(9.857 - 1.80, 1.95), xytext=(8.0, 1.8),
                 arrowprops=dict(arrowstyle='->', color='#b71c1c', lw=1.2), fontsize=7.5, fontweight='bold', color='#b71c1c',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#b71c1c', lw=0.8))
    
    ax3.annotate('Top Throat: 3.50mm (+0.35mm)', xy=(6.28, 4.95), xytext=(6.28, 5.7),
                 ha='center', fontsize=7.5, fontweight='bold', color='#e65100',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100', lw=0.8))
    
    ax3.set_xlim(-0.2, 12.8)
    ax3.set_ylim(-9.8, 9.0)
    ax3.set_aspect('equal')
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.set_title('3. Right Bracket Pair (Hot)', fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel('X (mm)', fontsize=9.5)
    ax3.set_ylabel('Y (mm)', fontsize=9.5)
    ax3.legend(loc='lower right', fontsize=7.5)
    
    # --------------------------------------------------------------------------
    # Panel 4: 3D Isometric View of Seating Rib Elevation & Shelves
    # --------------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[3], projection='3d')
    ax4.set_facecolor('#ffffff')
    
    # Base floor rectangle
    xx, yy = np.meshgrid(np.linspace(1.5, 11.0, 2), np.linspace(-7.5, 7.5, 2))
    ax4.plot_surface(xx, yy, np.ones_like(xx) * 1.0, color='#e0e0e0', alpha=0.4)
    
    # Bracket walls extruded to Z=5.60 (4.6mm tall on 1.0mm floor)
    b3_verts = np.array(b3_looser_pts)
    b4_verts = np.array(b4_looser_pts)
    
    for poly_pts, col in [(b3_verts, '#388e3c'), (b4_verts, '#1976d2')]:
        N = len(poly_pts)
        for i in range(N - 1):
            x_w = [poly_pts[i, 0], poly_pts[i+1, 0], poly_pts[i+1, 0], poly_pts[i, 0]]
            y_w = [poly_pts[i, 1], poly_pts[i+1, 1], poly_pts[i+1, 1], poly_pts[i, 1]]
            z_w = [1.0, 1.0, 5.6, 5.6]
            verts_quad = [list(zip(x_w, y_w, z_w))]
            poly3d = Poly3DCollection(verts_quad, facecolor=col, edgecolor='#333333', linewidths=0.3, alpha=0.35)
            ax4.add_collection3d(poly3d)
            
    # Draw 4 sets of 1.15mm ribs in 3D (Z: 1.0 to 2.15mm)
    z_rib_top = 1.00 + BRACKET_SEATING_RIB_HEIGHT  # 2.15 mm
    ext = BRACKET_SEATING_RIB_EXT
    for y in Y_RIB_POSITIONS:
        # B3 rib (X in [2.701, 2.701+ext], Y in [y-0.3, y+0.3], Z in [1.0, 2.15])
        # B4 rib (X in [9.857-ext, 9.857], Y in [y-0.3, y+0.3], Z in [1.0, 2.15])
        for x_start, x_end in [(2.701, 2.701 + ext), (9.857 - ext, 9.857)]:
            xr = [x_start, x_end, x_end, x_start]
            yr = [y - 0.3, y - 0.3, y + 0.3, y + 0.3]
            zr_top = [z_rib_top, z_rib_top, z_rib_top, z_rib_top]
            verts_top = [list(zip(xr, yr, zr_top))]
            poly_top = Poly3DCollection(verts_top, facecolor='#d32f2f', edgecolor='#b71c1c', linewidths=0.5, alpha=0.85)
            ax4.add_collection3d(poly_top)
            
            # Side faces
            for xi, yi in [([x_start, x_end], [y-0.3, y-0.3]), ([x_start, x_end], [y+0.3, y+0.3]),
                           ([x_start, x_start], [y-0.3, y+0.3]), ([x_end, x_end], [y-0.3, y+0.3])]:
                xs = [xi[0], xi[1], xi[1], xi[0]]
                ys = [yi[0], yi[1], yi[1], yi[0]]
                zs = [1.0, 1.0, z_rib_top, z_rib_top]
                verts_side = [list(zip(xs, ys, zs))]
                poly_side = Poly3DCollection(verts_side, facecolor='#d32f2f', edgecolor='#b71c1c', linewidths=0.5, alpha=0.75)
                ax4.add_collection3d(poly_side)
                
    # Draw Brass Part seating on top (Z = 2.15mm)
    xb = [6.28 - 3.37, 6.28 + 3.37, 6.28 + 3.37, 6.28 - 3.37]
    yb = [-5.80, -5.80, 6.00, 6.00]
    zb = [z_rib_top + 0.05, z_rib_top + 0.05, z_rib_top + 0.05, z_rib_top + 0.05]
    verts_brass = [list(zip(xb, yb, zb))]
    poly_brass = Poly3DCollection(verts_brass, facecolor='#ffd54f', edgecolor='#f57f17', linewidths=1.0, alpha=0.55)
    ax4.add_collection3d(poly_brass)
    
    ax4.set_xlim(1.0, 11.5)
    ax4.set_ylim(-8.0, 8.0)
    ax4.set_zlim(0.0, 7.0)
    ax4.view_init(elev=28, azim=-55)
    ax4.set_title('4. 3D Seating Ribs (1.15mm H)', fontsize=12, fontweight='bold', pad=10)
    ax4.set_xlabel('X (mm)', fontsize=8)
    ax4.set_ylabel('Y (mm)', fontsize=8)
    ax4.set_zlabel('Z (mm)', fontsize=8)
    
    out_testing = os.path.join(os.path.dirname(__file__), 'complete_bracket_update_diagram.png')
    plt.savefig(out_testing, dpi=200)
    print(f"Saved complete diagram to: {out_testing}")
    
    # Copy to artifact directory
    artifact_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\f3d4a0c2-757f-4d9a-9b44-08845cae7d7f"
    if os.path.exists(artifact_dir):
        out_artifact = os.path.join(artifact_dir, 'complete_bracket_update_diagram.png')
        shutil.copy(out_testing, out_artifact)
        print(f"Copied complete diagram to artifact directory: {out_artifact}")

if __name__ == '__main__':
    generate_diagram()
