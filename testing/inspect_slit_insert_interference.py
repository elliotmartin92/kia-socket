"""
testing/inspect_slit_insert_interference.py
Investigates the right slit socket geometry, alignment, interference, and tolerances.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trimesh
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union

from build_part import (
    build_exact_3d_model, get_exact_base_polygon, create_all_brackets_poly,
    create_bracket_seating_ribs_poly, create_arch_wall_poly,
    create_center_curved_feature_poly, build_slit_insert_mesh,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_KEY_W_X, INSERT_KEY_LEN_Y, INSERT_CLEARANCE,
    INSERT_BODY_W_X, INSERT_BODY_LEN_Y, SLIT_W_X, SLIT_LEN_Y, BASE_THICK
)

def inspect_slits():
    print("=== INSPECTING SLIT INSERTS & INTERFERENCES ===")
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    
    # 1. Detent socket positions in base_poly
    # Let's inspect the holes in base_poly
    print(f"Number of interior holes in base_poly: {len(base_poly.interiors)}")
    for idx, interior in enumerate(base_poly.interiors):
        p_int = Polygon(interior)
        b = p_int.bounds
        print(f"  Hole {idx+1}: center=({(b[0]+b[2])/2:.3f}, {(b[1]+b[3])/2:.3f}), size=({b[2]-b[0]:.3f} x {b[3]-b[1]:.3f})")
        
    # 2. Check outer body boundaries near the right slit
    # Right slit center is cx_right = 8.453, cy = -13.589
    # Right socket bounds: X in [7.328, 9.578], Y in [-15.864, -11.314]
    # Right body bounds: X in [8.453 - 3.8/2, 8.453 + 3.8/2] = [6.553, 10.353]
    # Y in [-13.589 - 5.6/2, -13.589 + 5.6/2] = [-16.389, -10.789]
    print(f"\nRight Detent Socket (Key fits into floor):")
    print(f"  Center: (8.453, -13.589)")
    print(f"  Socket Size in Floor: {SOCKET_W_X:.3f} x {SOCKET_LEN_Y:.3f} mm")
    print(f"  Male Key Size on Insert: {INSERT_KEY_W_X:.3f} x {INSERT_KEY_LEN_Y:.3f} mm")
    print(f"  Clearance: {INSERT_CLEARANCE:.3f} mm ({INSERT_CLEARANCE/2:.3f} mm per side)")
    
    print(f"\nRight Insert Outer Body Shroud (When pressed against bottom face):")
    print(f"  Shroud Size: {INSERT_BODY_W_X:.3f} x {INSERT_BODY_LEN_Y:.3f} mm")
    print(f"  Shroud X range: [{8.453 - INSERT_BODY_W_X/2:.3f}, {8.453 + INSERT_BODY_W_X/2:.3f}] mm")
    print(f"  Shroud Y range: [{-13.589 - INSERT_BODY_LEN_Y/2:.3f}, {-13.589 + INSERT_BODY_LEN_Y/2:.3f}] mm")
    
    # Check if Shroud overlaps with perimeter wall, bottom tabs, or bottom notch
    shroud_right = box(8.453 - INSERT_BODY_W_X/2, -13.589 - INSERT_BODY_LEN_Y/2,
                       8.453 + INSERT_BODY_W_X/2, -13.589 + INSERT_BODY_LEN_Y/2)
    shroud_left = box(-7.853 - INSERT_BODY_W_X/2, -13.589 - INSERT_BODY_LEN_Y/2,
                      -7.853 + INSERT_BODY_W_X/2, -13.589 + INSERT_BODY_LEN_Y/2)
                      
    print(f"\nDistance from Right Shroud to Baseplate Outer Edge:")
    # Distance to outer perimeter
    dist_right_to_edge = outer_body_poly.exterior.distance(shroud_right)
    print(f"  Right Shroud distance to outer edge: {dist_right_to_edge:.3f} mm")
    
    # 3. Check Brass Contact Alignment vs Right Slit!
    # Where does the right brass contact terminal leg exit Bracket 3/4?
    # Bracket 3 is at X in [1.766, 4.500], Bracket 4 is at X in [8.000, 10.791]
    # Channel center between B3 & B4: X = (4.500 + 8.000)/2 = 6.250 mm or (2.701 + 9.857)/2 = 6.279 mm!
    # The bottom step opening between B3 & B4 is at X in [4.350, 8.150] (center = 6.250 mm).
    # The brass part center is at X = 6.279 mm (or X = 6.28 mm).
    # The S-curve terminal leg of the OEM brass part offsets to the right or left?
    # Look at cropped_bracket_photo.jpg:
    # Left contact leg S-curves to the LEFT (towards X = -7.853 mm).
    # Right contact leg S-curves to the RIGHT (towards X = +8.453 mm).
    print(f"\nBracket Bottom Step & Contact Centers:")
    print(f"  Left Bracket Step Opening:  X in [{-8.150:.3f}, {-4.350:.3f}] (Center: {-6.250:.3f} mm)")
    print(f"  Left Detent Socket Center:  X = -7.853 mm (offset = {-7.853 - (-6.250):.3f} mm to the left)")
    print(f"  Right Bracket Step Opening: X in [{4.350:.3f}, {8.150:.3f}] (Center: {6.250:.3f} mm)")
    print(f"  Right Detent Socket Center: X = +8.453 mm (offset = {8.453 - 6.250:.3f} mm to the right)")
    print(f"  Note: Right socket X max = {8.453 + SOCKET_W_X/2:.3f} mm, while Bracket 4 bottom wall inner edge is at X = 8.150 mm!")
    
    # 4. Check 3D mesh slicing across the slits!
    part_mesh, _ = build_exact_3d_model()
    # Check if any geometry covers the top of the right socket (Z in [1.0, 5.0])
    right_socket_box = box(8.453 - SOCKET_W_X/2, -13.589 - SOCKET_LEN_Y/2, 8.453 + SOCKET_W_X/2, -13.589 + SOCKET_LEN_Y/2)
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)
    
    # Plot 1: Bottom view with Detent Sockets and Shrouds
    ax = axes[0]
    bx, by = outer_body_poly.exterior.xy
    ax.plot(bx, by, color='#1565c0', lw=2.0, label='Perimeter')
    
    for interior in base_poly.interiors:
        ax.plot(*interior.xy, color='#d32f2f', lw=2.0)
        
    ax.fill(*shroud_left.exterior.xy, color='#9c27b0', alpha=0.4, label='Left Shroud Footprint')
    ax.fill(*shroud_right.exterior.xy, color='#9c27b0', alpha=0.4, label='Right Shroud Footprint')
    
    # Overlay brackets
    b_poly = create_all_brackets_poly()
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        ax.plot(*g.exterior.xy, color='#2e7d32', lw=1.5, ls='--')
        
    # Overlay bottom arch
    arch = create_arch_wall_poly()
    ax.plot(*arch.exterior.xy, color='#0d47a1', lw=1.5)
    
    ax.set_xlim(-15, 15)
    ax.set_ylim(-20, -5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title('Bottom View: Detent Sockets, Inserts & Surrounding Features', fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend(loc='upper right', fontsize=8)
    
    # Plot 2: Close-up on Right Slit / Socket Area
    ax2 = axes[1]
    ax2.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Wall')
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        if min(ix) > 0:
            ax2.fill(ix, iy, color='#ffcdd2', edgecolor='#d32f2f', lw=2.0, label='Right Detent Socket (Floor Cutout)')
            
    ax2.fill(*shroud_right.exterior.xy, color='#e1bee7', alpha=0.6, edgecolor='#7b1fa2', lw=1.8, ls='--', label='Right Insert Shroud Body')
    
    # Draw right bracket bottom wall
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        gx, gy = g.exterior.xy
        if min(gx) > 0:
            ax2.plot(gx, gy, color='#2e7d32', lw=2.0, label='Bracket 3 / 4' if max(gy) > 0 else "")
            
    # Draw arch outer wall
    ax2.plot(*arch.exterior.xy, color='#0d47a1', lw=2.0, label='Arch Outer Wall')
    
    ax2.set_xlim(2.0, 16.0)
    ax2.set_ylim(-19.0, -5.0)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('Right Slit & Detent Socket Region Close-Up', fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'slit_insert_interference_analysis.png')
    plt.savefig(out_path, dpi=180)
    print(f"Saved interference analysis plot to: {out_path}")

if __name__ == '__main__':
    inspect_slits()
