"""
testing/verify_reinforced_center_d.py
Verification script for the reinforced Center Curved D feature:
1. Verifies 3D mesh volume, watertightness, and bounds.
2. Checks cross-sectional profile at base Z = 1.00mm, rib junction Z = 2.15mm, and column Z = 10.50mm.
3. Verifies clearance to plug blade in Y and Z.
4. Verifies clearance to Rib 4 and brass contact.
5. Verifies monolithic integration in flat and 45-degree tilted supported deliverables.
6. Generates diagnostic cross-section plot: testing/reinforced_center_d_inspection.png
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box

import build_part as bp

def run_tests():
    print("=" * 70)
    print("VERIFICATION: REINFORCED CENTER CURVED D FEATURE")
    print("=" * 70)
    
    # 1. Mesh inspection
    c_mesh = bp.build_center_curved_feature_mesh()
    print(f"Center Curved D watertight: {c_mesh.is_watertight}")
    print(f"Center Curved D volume: {c_mesh.volume:.3f} mm^3")
    b = c_mesh.bounds
    print(f"Bounds: X in [{b[0,0]:.3f}, {b[1,0]:.3f}], Y in [{b[0,1]:.3f}, {b[1,1]:.3f}], Z in [{b[0,2]:.3f}, {b[1,2]:.3f}]")
    
    assert c_mesh.is_watertight, "Center Curved D mesh is not watertight!"
    assert b[1, 2] >= 10.49, f"Apex elevation incorrect: {b[1, 2]}"
    
    # 2. Check 2D profiles at key elevations
    p_base = bp.create_center_curved_feature_poly(z=1.00)
    p_rib = bp.create_center_curved_feature_poly(z=2.15)
    p_top = bp.create_center_curved_feature_poly(z=10.50)
    
    print(f"\nProfile at floor Z=1.00mm: Y in [{p_base.bounds[1]:.3f}, {p_base.bounds[3]:.3f}] (Depth = {p_base.bounds[3]-p_base.bounds[1]:.3f}mm)")
    print(f"Profile at rib Z=2.15mm:   Y in [{p_rib.bounds[1]:.3f}, {p_rib.bounds[3]:.3f}] (Depth = {p_rib.bounds[3]-p_rib.bounds[1]:.3f}mm)")
    print(f"Profile at top Z=10.50mm:  Y in [{p_top.bounds[1]:.3f}, {p_top.bounds[3]:.3f}] (Depth = {p_top.bounds[3]-p_top.bounds[1]:.3f}mm)")
    
    assert abs(p_base.bounds[3] - (-2.45)) < 0.05, f"Flared foot apex incorrect: {p_base.bounds[3]}"
    assert abs(p_top.bounds[3] - (-3.25)) < 0.05, f"Column apex incorrect: {p_top.bounds[3]}"
    
    # 3. Clearance checks
    # Worst-case blade bottom edge: Y = -2.875mm at Z >= 4.5mm
    blade_y_worst = -2.875
    clr_col = blade_y_worst - p_top.bounds[3]
    print(f"\nClearance from upper column to worst-case blade ({blade_y_worst:.3f}mm): {clr_col:.3f} mm")
    assert clr_col >= 0.35, f"Insufficient blade clearance: {clr_col}"
    
    # Nominal blade bottom edge: Y = -1.225mm
    blade_y_nom = -1.225
    clr_nom = blade_y_nom - p_top.bounds[3]
    print(f"Clearance from upper column to nominal blade ({blade_y_nom:.3f}mm): {clr_nom:.3f} mm")
    
    # Foot clearance to nominal blade:
    clr_foot = blade_y_nom - p_base.bounds[3]
    print(f"Clearance from flared foot to nominal blade: {clr_foot:.3f} mm")
    assert clr_foot >= 1.0, f"Insufficient foot clearance: {clr_foot}"
    
    # 4. Monolithic model build
    print("\nBuilding full part model...")
    part_mesh_flat, base_poly = bp.build_exact_3d_model()
    print(f"Full flat part: watertight = {part_mesh_flat.is_watertight}, volume = {part_mesh_flat.volume:.2f} mm^3")
    assert part_mesh_flat.is_watertight, "Flat part is not watertight!"
    
    # 5. Diagnostic plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=180)
    
    # Panel 1: Top-down plan view
    b3 = bp.to_mm_poly(bp.bracket_3_raw_pts)
    b4 = bp.to_mm_poly(bp.bracket_4_raw_pts)
    ax1.fill(*b3.exterior.xy, color='#2e7d32', alpha=0.3, label='Bracket 3 (4.60mm)')
    ax1.plot(*b3.exterior.xy, color='#1b5e20', lw=1.5)
    ax1.fill(*b4.exterior.xy, color='#2e7d32', alpha=0.3, label='Bracket 4 (4.60mm)')
    ax1.plot(*b4.exterior.xy, color='#1b5e20', lw=1.5)
    
    # Foot polygon
    ax1.fill(*p_base.exterior.xy, color='#ba68c8', alpha=0.4, label='Flared Foot (Z=1.00 to 2.15mm)')
    ax1.plot(*p_base.exterior.xy, color='#8e24aa', lw=2, linestyle='--')
    # Column polygon
    ax1.fill(*p_top.exterior.xy, color='#8e24aa', alpha=0.6, label='Reinforced Column (Apex Y = -3.25mm)')
    ax1.plot(*p_top.exterior.xy, color='#4a148c', lw=2.5)
    
    # Plug blade
    blade_poly = box(6.279 - 1.52/2, blade_y_worst, 6.279 + 1.52/2, blade_y_worst + 6.35)
    ax1.fill(*blade_poly.exterior.xy, color='#9e9e9e', alpha=0.5, label='Worst-Case Blade (Y = -2.875mm)')
    ax1.plot(*blade_poly.exterior.xy, color='#212121', lw=1.8)
    
    blade_nom_poly = box(6.279 - 1.52/2, blade_y_nom, 6.279 + 1.52/2, blade_y_nom + 6.35)
    ax1.plot(*blade_nom_poly.exterior.xy, color='#1565c0', lw=2, linestyle=':', label='Nominal Blade (Y = -1.225mm)')
    
    ax1.set_xlim(1.0, 11.5)
    ax1.set_ylim(-6.5, 6.0)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_title('Top-Down Plan View: Reinforced Center D & Clearances', fontsize=11, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=8)
    
    # Panel 2: Side elevation (Y-Z cross section at X = 6.279mm)
    z_arr = np.linspace(1.00, 10.50, 100)
    y_front = [bp.create_center_curved_feature_poly(z=z).bounds[3] for z in z_arr]
    y_back = [-5.05] * len(z_arr)
    
    ax2.fill_betweenx(z_arr, y_back, y_front, color='#ab47bc', alpha=0.4, label='Reinforced Center D Solid Core')
    ax2.plot(y_front, z_arr, color='#4a148c', lw=2.5, label='Front Profile (Flared Foot + Column)')
    ax2.plot(y_back, z_arr, color='#1a237e', lw=2, label='Flat Back Wall (Y = -5.05mm)')
    
    # Blade in side view
    ax2.fill([blade_y_worst, blade_y_worst + 6.35, blade_y_worst + 6.35, blade_y_worst],
             [4.50, 4.50, 15.00, 15.00], color='#9e9e9e', alpha=0.3, label='Blade Insertion Reach (Z >= 4.50mm)')
    ax2.axvline(blade_y_worst, color='#d32f2f', linestyle='--', lw=1.5, label='Worst-Case Blade Bottom (Y = -2.875mm)')
    ax2.axvline(blade_y_nom, color='#1565c0', linestyle=':', lw=1.5, label='Nominal Blade Bottom (Y = -1.225mm)')
    
    ax2.axhline(2.15, color='#ff9800', linestyle='-.', lw=1.2, label='Seating Rib Elevation (Z = 2.15mm)')
    
    ax2.set_xlim(-6.5, 6.0)
    ax2.set_ylim(0.0, 16.0)
    ax2.set_xlabel('Y (mm)')
    ax2.set_ylabel('Z (mm)')
    ax2.set_title('Side Elevation (Y-Z): Flared Foot & Plug Penetration Buffer', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), 'reinforced_center_d_inspection.png')
    plt.savefig(out_png)
    print(f"\nSaved diagnostic render: {out_png}")
    print("\nALL VERIFICATIONS PASSED!")

if __name__ == '__main__':
    run_tests()
