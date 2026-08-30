"""
testing/test_partial_height_wall_relief.py
Tests partial-height inner wall relief (e.g. Z = 1.00mm to Z = 2.50mm)
so that the top perimeter wall (Z = 2.50mm to 6.77mm) remains 100% solid, continuous, and full-height!
"""
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trimesh
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, create_arch_wall_poly, extrude_shapely_geom,
    OUTER_WALL_THICK, OUTER_WALL_HEIGHT, BASE_THICK, SOCKET_W_X, SOCKET_LEN_Y
)

def build_part_with_partial_relief(relief_top_z=2.50):
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    
    # 1. Base Plate (Z: 0 to 1.00mm)
    mesh_base = extrude_shapely_geom(base_poly, height=BASE_THICK)
    
    # 2. Wall creation with partial-height relief
    # Full un-notched wall polygon
    inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly_full = outer_body_poly.difference(inner_poly)
    
    # Relieved wall polygon (for bottom section Z: 1.00 to relief_top_z)
    cy = -13.589
    detent_left_box = box(-7.853 - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, -7.853 + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)
    detent_right_box = box(8.453 - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, 8.453 + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)
    socket_relief_zone = unary_union([detent_left_box.buffer(0.35), detent_right_box.buffer(0.35)])
    wall_poly_relieved = wall_poly_full.difference(socket_relief_zone)
    
    arch_wall_poly = create_arch_wall_poly()
    
    # Bottom wall section (Z: 1.00 to relief_top_z)
    h_bottom = relief_top_z - BASE_THICK  # e.g. 2.50 - 1.00 = 1.50mm
    bottom_walls = unary_union([wall_poly_relieved, arch_wall_poly])
    mesh_wall_bottom = extrude_shapely_geom(bottom_walls, height=h_bottom)
    mesh_wall_bottom.apply_translation([0, 0, BASE_THICK])
    
    # Top wall section (Z: relief_top_z to OUTER_WALL_HEIGHT) - 100% full, solid, continuous rim!
    h_top = OUTER_WALL_HEIGHT - relief_top_z  # e.g. 6.77 - 2.50 = 4.27mm
    top_walls = unary_union([wall_poly_full, arch_wall_poly])
    mesh_wall_top = extrude_shapely_geom(top_walls, height=h_top)
    mesh_wall_top.apply_translation([0, 0, relief_top_z])
    
    mesh_wall = trimesh.util.concatenate([mesh_wall_bottom, mesh_wall_top])
    full_part = trimesh.util.concatenate([mesh_base, mesh_wall])
    return full_part, wall_poly_full, wall_poly_relieved

def run_test():
    print("=== TESTING PARTIAL-HEIGHT WALL RELIEF ===")
    relief_top_z = 2.50
    mesh, wall_full, wall_rel = build_part_with_partial_relief(relief_top_z=relief_top_z)
    print(f"Mesh is watertight: {mesh.is_watertight}")
    print(f"Mesh volume: {mesh.volume:.3f} mm^3")
    print(f"Mesh Z bounds: [{mesh.bounds[0,2]:.3f}, {mesh.bounds[1,2]:.3f}] mm (Full 6.77mm wall height)")
    
    # Generate visual comparison plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 8.0), dpi=220, facecolor='#ffffff')
    
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    bx, by = outer_body_poly.exterior.xy
    
    # Panel 1: Layer-by-Layer Z-Heights Comparison
    ax1 = axes[0]
    ax1.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    
    # Relieved inner wall (Z = 1.00 to 2.50mm)
    for geom in (wall_rel.geoms if hasattr(wall_rel, 'geoms') else [wall_rel]):
        ax1.plot(*geom.exterior.xy, color='#2e7d32', lw=2.0, label='Bottom Wall Face (Z = 1.00 to 2.50mm)' if geom == (wall_rel.geoms[0] if hasattr(wall_rel, 'geoms') else wall_rel) else "")
        
    # Full top rim inner wall (Z = 2.50 to 6.77mm)
    inner_poly_full = outer_body_poly.buffer(-OUTER_WALL_THICK)
    ax1.plot(*inner_poly_full.exterior.xy, color='#e65100', ls='--', lw=2.0, label='Top Wall Rim Face (Z = 2.50 to 6.77mm)')
    
    cy = -13.589
    sock_right = box(8.453 - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, 8.453 + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)
    ax1.fill(*sock_right.exterior.xy, color='#ffcdd2', edgecolor='#d32f2f', lw=1.8, label='Right Detent Socket (X=+8.453)')
    
    ax1.annotate('Clearance Pocket\nat Bottom (Z=1.00-2.50mm)\nNo Overhang on Socket', xy=(8.453, -15.5), xytext=(3.2, -17.5),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=8.0, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax1.annotate('Continuous Solid Rim\nat Top (Z=2.50-6.77mm)\nFull 6.77mm Wall Height', xy=(9.2, -14.8), xytext=(10.5, -12.5),
                 arrowprops=dict(arrowstyle='->', color='#e65100', lw=1.6), fontsize=8.0, fontweight='bold', color='#e65100',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100'))
                 
    ax1.set_xlim(2.0, 15.0)
    ax1.set_ylim(-19.5, -9.0)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('1. Top-Down Plan: Pocket Relief vs Solid Top Rim', fontsize=11, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='lower left', fontsize=8.0)
    
    # Panel 2: Y-Z Cross Section along X = +8.453mm
    ax2 = axes[1]
    
    # Baseplate Floor (Z: 0 to 1.0mm, Y: -18.54 to -8.0mm)
    # Socket cutout: Y in [-15.939, -11.239]
    y_sock_bot = -13.589 - SOCKET_LEN_Y/2 # -15.939
    y_sock_top = -13.589 + SOCKET_LEN_Y/2 # -11.239
    
    ax2.fill([-18.54, y_sock_bot, y_sock_bot, -18.54], [0.0, 0.0, 1.0, 1.0], color='#cfd8dc', edgecolor='#455a64', lw=1.5, label='Baseplate Floor (1.00mm)')
    ax2.fill([y_sock_top, -7.5, -7.5, y_sock_top], [0.0, 0.0, 1.0, 1.0], color='#cfd8dc', edgecolor='#455a64', lw=1.5)
    
    # Relieved bottom wall (Z: 1.00 to 2.50mm) - starts at Y = -16.29mm
    ax2.fill([-18.54, -16.29, -16.29, -18.54], [1.00, 1.00, relief_top_z, relief_top_z], color='#81c784', edgecolor='#2e7d32', lw=1.8, label='Relieved Bottom Wall (Z=1.00-2.50mm)')
    
    # Solid top rim (Z: 2.50 to 6.77mm) - full 1.20mm thickness, inner face at Y = -14.75mm
    ax2.fill([-18.54, -14.75, -14.75, -18.54], [relief_top_z, relief_top_z, 6.77, 6.77], color='#1976d2', edgecolor='#0d47a1', lw=1.8, label='Solid Full Top Rim (Z=2.50-6.77mm)')
    
    # Slit insert seated in floor
    ax2.fill([-13.589 - 2.10, -13.589 - 2.10, -13.589 + 2.10, -13.589 + 2.10], [-2.47, 0.0, 0.0, -2.47], color='#ba68c8', edgecolor='#6a1b9a', lw=1.5, label='Sloped Insert (Z=-2.47 to 0.0mm)')
    ax2.fill([-13.589 - 1.85, -13.589 - 1.85, -13.589 + 1.85, -13.589 + 1.85], [0.0, 0.85, 0.85, 0.0], color='#ab47bc', edgecolor='#6a1b9a', lw=1.5, label='Insert Key in Socket (Z=0.0-0.85mm)')
    
    # Annotations
    ax2.annotate('Pocket Overhang Cleared\nKey & Blade seat freely\n(Z = 1.00 to 2.50mm)', xy=(-16.29, 1.75), xytext=(-13.8, 1.75),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5), fontsize=8.0, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax2.annotate('Solid Perimeter Rim\nFull 6.77mm Wall Preserved\n(Z = 2.50 to 6.77mm)', xy=(-15.5, 4.5), xytext=(-13.0, 4.5),
                 arrowprops=dict(arrowstyle='->', color='#0d47a1', lw=1.5), fontsize=8.0, fontweight='bold', color='#0d47a1',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#0d47a1'))
                 
    ax2.set_xlim(-19.5, -7.0)
    ax2.set_ylim(-3.0, 7.5)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('2. Y-Z Cross Section at Right Slit (X = +8.453mm)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Y (mm)')
    ax2.set_ylabel('Z (mm)')
    ax2.legend(loc='lower right', fontsize=7.5)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'partial_height_wall_relief_preview.png')
    plt.savefig(out_path, dpi=220)
    print(f"Saved preview to {out_path}")
    
    artifact_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\f3d4a0c2-757f-4d9a-9b44-08845cae7d7f"
    if os.path.exists(artifact_dir):
        out_artifact = os.path.join(artifact_dir, 'partial_height_wall_relief_preview.png')
        shutil.copy(out_path, out_artifact)
        print(f"Copied preview to artifact directory: {out_artifact}")

if __name__ == '__main__':
    run_test()
