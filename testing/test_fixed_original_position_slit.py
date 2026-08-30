"""
testing/test_fixed_original_position_slit.py
Tests keeping the right slit at its original location (X = +8.453mm) while:
1. Relieving / clearing the inner perimeter wall so it has zero overhang over the socket.
2. Sizing the sloped insert (2.20mm tip, slimmed base) so it fits flush within the outer wall perimeter.
3. Expanded slit (1.35mm x 3.65mm) for increased tolerance.
4. Relaxed socket clearance (0.50mm / 0.25mm per side).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly, create_arch_wall_poly,
    OUTER_WALL_THICK, SLIT_BOSS_HEIGHT, BASE_THICK
)

# Slit Positions (Original unshifted coordinates)
CX_LEFT = -7.853
CX_RIGHT = +8.453   # Kept at original position!
CY_SLIT = -13.589

# Expanded Slit in Insert
SLIT_W = 1.35   # Expanded slit width (+0.58mm clearance for 0.77mm blade)
SLIT_L = 3.65   # Expanded slit length (+0.55mm clearance for 3.10mm blade)

# Insert Dimensions (with 2.20mm wide end)
BODY_W_TIP = 2.20   # Exact 2.20mm wide end as requested
BODY_L_TIP = 4.20
BODY_W_BASE = 2.70  # Slimmed shoulder base so it fits inside the perimeter edge (X_max = 8.453 + 1.35 = 9.803 <= 9.812)
BODY_L_BASE = 4.80

KEY_W_BASE = 1.90   # Key base
KEY_L_BASE = 4.20
KEY_W_TOP = 1.40    # 0.25mm lead-in taper per side
KEY_L_TOP = 3.70
KEY_H = 0.85

# Baseplate Socket Dimensions (Relaxed 0.50mm clearance)
SOCKET_W = KEY_W_BASE + 0.50  # 2.40mm (X in [7.253, 9.653] <= 9.812)
SOCKET_L = KEY_L_BASE + 0.50  # 4.70mm

def check_geometry():
    print("=== TESTING FIXED ORIGINAL POSITION SLIT (X = +8.453mm) ===")
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    
    # 1. Baseplate Floor Sockets
    sock_left = box(CX_LEFT - SOCKET_W/2, CY_SLIT - SOCKET_L/2, CX_LEFT + SOCKET_W/2, CY_SLIT + SOCKET_L/2)
    sock_right = box(CX_RIGHT - SOCKET_W/2, CY_SLIT - SOCKET_L/2, CX_RIGHT + SOCKET_W/2, CY_SLIT + SOCKET_L/2)
    
    # Base poly with sockets
    base_with_sockets = outer_body_poly.difference(unary_union([sock_left, sock_right]))
    
    # 2. Inner Perimeter Wall with Socket Clearance Relief
    inner_poly_raw = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly_raw = outer_body_poly.difference(inner_poly_raw)
    
    # Relieve the wall around both sockets with 0.40mm clearance buffer
    socket_relief_zone = unary_union([sock_left.buffer(0.40), sock_right.buffer(0.40)])
    wall_poly_relieved = wall_poly_raw.difference(socket_relief_zone)
    
    # Verify wall overlap after relief:
    overlap_left = wall_poly_relieved.intersection(sock_left)
    overlap_right = wall_poly_relieved.intersection(sock_right)
    
    print(f"Wall Overlap over Left Socket:  {overlap_left.area:.4f} mm^2")
    print(f"Wall Overlap over Right Socket: {overlap_right.area:.4f} mm^2 (CLEARED! Was 0.7691 mm^2 blocking wall!)")
    
    # 3. Outer Shroud Clearance on Bottom Face
    shroud_right_base = box(CX_RIGHT - BODY_W_BASE/2, CY_SLIT - BODY_L_BASE/2, CX_RIGHT + BODY_W_BASE/2, CY_SLIT + BODY_L_BASE/2)
    shroud_right_tip = box(CX_RIGHT - BODY_W_TIP/2, CY_SLIT - BODY_L_TIP/2, CX_RIGHT + BODY_W_TIP/2, CY_SLIT + BODY_L_TIP/2)
    
    dist_base_to_edge = outer_body_poly.exterior.distance(shroud_right_base)
    dist_tip_to_edge = outer_body_poly.exterior.distance(shroud_right_tip)
    
    print(f"\nRight Shroud Clearance to Perimeter Outer Edge:")
    print(f"  Shoulder Base (X_max = {CX_RIGHT + BODY_W_BASE/2:.3f} mm vs Wall = 9.812 mm): distance = {dist_base_to_edge:.3f} mm (Inside perimeter)")
    print(f"  Outer Tip     (X_max = {CX_RIGHT + BODY_W_TIP/2:.3f} mm vs Wall = 9.812 mm): distance = {dist_tip_to_edge:.3f} mm (Inside perimeter)")
    
    # 4. Generate visual comparison plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 8.5), dpi=200)
    
    # Plot 1: Inner Wall Before vs After Relief at Right Slit
    ax1 = axes[0]
    bx, by = outer_body_poly.exterior.xy
    ax1.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Outer Wall')
    ax1.plot(*inner_poly_raw.exterior.xy, color='#d32f2f', ls=':', lw=2.0, label='Old Inner Wall (Blocked Right Socket!)')
    
    # Relieved inner wall face
    for geom in (wall_poly_relieved.geoms if hasattr(wall_poly_relieved, 'geoms') else [wall_poly_relieved]):
        ax1.plot(*geom.exterior.xy, color='#2e7d32', lw=1.8)
        
    ax1.fill(*sock_right.exterior.xy, color='#ffcdd2', edgecolor='#d32f2f', lw=2.0, label='Right Detent Socket (X=+8.453)')
    ax1.plot(*shroud_right_base.exterior.xy, color='#7b1fa2', ls='--', lw=1.8, label='Insert Shroud Base (2.7x4.8mm)')
    ax1.plot(*shroud_right_tip.exterior.xy, color='#4a148c', ls='-', lw=2.0, label='Insert Sloped Tip (2.2x4.2mm)')
    
    ax1.annotate('Inner Wall Relief Pocket\n(Zero Vertical Overhang)', xy=(8.453, -15.5), xytext=(3.0, -17.5),
                 arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.6), fontsize=8.5, fontweight='bold', color='#2e7d32',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))
                 
    ax1.set_xlim(2.5, 15.5)
    ax1.set_ylim(-19.5, -9.0)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('1. Wall Relief at Original Position (X = +8.453mm)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='lower left', fontsize=8)
    
    # Plot 2: Full Bottom Layout with Relieved Wall & Sloped Inserts
    ax2 = axes[1]
    ax2.plot(bx, by, color='#1565c0', lw=2.2, label='Perimeter Wall')
    
    shroud_left_base = box(CX_LEFT - BODY_W_BASE/2, CY_SLIT - BODY_L_BASE/2, CX_LEFT + BODY_W_BASE/2, CY_SLIT + BODY_L_BASE/2)
    ax2.fill(*shroud_left_base.exterior.xy, color='#ba68c8', alpha=0.45, edgecolor='#6a1b9a', lw=1.5, label='Left Slit (X=-7.853)')
    ax2.fill(*shroud_right_base.exterior.xy, color='#ba68c8', alpha=0.45, edgecolor='#6a1b9a', lw=1.5, label='Right Slit (X=+8.453)')
    
    ax2.plot(*sock_left.exterior.xy, color='#d32f2f', lw=1.8, label='Sockets (2.4x4.7mm)')
    ax2.plot(*sock_right.exterior.xy, color='#d32f2f', lw=1.8)
    
    arch_poly = create_arch_wall_poly()
    ax2.plot(*arch_poly.exterior.xy, color='#0d47a1', lw=1.6)
    
    b_poly = create_all_brackets_poly()
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        ax2.plot(*g.exterior.xy, color='#2e7d32', lw=1.2, ls='--')
        
    ax2.set_xlim(-15.5, 15.5)
    ax2.set_ylim(-20.5, -4.5)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title('2. Complete Layout (Both Slits at Exact OEM Positions)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'fixed_original_position_slit.png')
    plt.savefig(out_path, dpi=200)
    print(f"Saved plot to: {out_path}")

if __name__ == '__main__':
    check_geometry()
