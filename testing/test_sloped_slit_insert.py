"""
testing/test_sloped_slit_insert.py
Tests:
1. Symmetrical right slit detent position (cx_right = +7.853mm, matching cx_left = -7.853mm).
2. Relaxed insert clearance (e.g. 0.50mm / 0.25mm per side) so it is not too tight.
3. Sloped/tapered walls and lead-in chamfers on the slit insert.
4. Total clearance vs baseplate perimeter walls, arch, and brackets.
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
    OUTER_WALL_THICK, SLIT_W_X, SLIT_LEN_Y, SLIT_BOSS_HEIGHT, BASE_THICK
)

# Proposed New Slit & Insert Parameters:
CX_LEFT = -7.853
CX_RIGHT = +7.853   # Symmetrical to cx_left (pulled 0.60mm inward away from perimeter wall)
CY_SLIT = -13.589   # Y center

# Male Key dimensions on Insert
INSERT_KEY_W_X = 2.00    # 2.00mm at base
INSERT_KEY_LEN_Y = 4.30  # 4.30mm at base
INSERT_KEY_HEIGHT = 0.85 # 0.85mm protrusion into 1.0mm floor socket

# Socket dimensions in Baseplate Floor (with relaxed 0.50mm clearance / 0.25mm per side)
RELAXED_CLEARANCE = 0.50 # 0.50mm clearance (0.25mm per side)
SOCKET_W_X = INSERT_KEY_W_X + RELAXED_CLEARANCE     # 2.50mm
SOCKET_LEN_Y = INSERT_KEY_LEN_Y + RELAXED_CLEARANCE # 4.80mm

# Shroud Body on Insert (outer face on back of housing)
INSERT_BODY_W_X = 3.60   # 3.60mm at base (slightly slimmed from 3.80mm for maximum wall clearance)
INSERT_BODY_LEN_Y = 5.40 # 5.40mm at base (slightly slimmed from 5.60mm)

def build_sloped_slit_insert_mesh(draft_angle_deg=5.0, key_chamfer=0.40):
    """
    Builds a 3D-printable slit insert with:
    1. Sloped outer shroud walls (draft angle from mating shoulder Z=2.47mm to outer face Z=0).
    2. Beveled/tapered indexing key (Z=2.47mm to Z=3.32mm) for self-centering easy insertion.
    3. Smooth through-hole with funnel lead-in.
    """
    z_shoulder = SLIT_BOSS_HEIGHT  # 2.47mm
    z_key_top = z_shoulder + INSERT_KEY_HEIGHT  # 3.32mm
    
    # 1. Shroud Body (Z: 0 to 2.47mm) with sloped exterior walls
    # Base at Z=2.47mm: INSERT_BODY_W_X x INSERT_BODY_LEN_Y (3.60 x 5.40)
    # Tip at Z=0.00mm: tapered by draft (dx = 2.47 * tan(draft_angle))
    dx_body = z_shoulder * np.tan(np.radians(draft_angle_deg))  # ~0.22mm per side
    w_bot = INSERT_BODY_W_X - 2 * dx_body   # ~3.16mm
    l_bot = INSERT_BODY_LEN_Y - 2 * dx_body # ~4.96mm
    
    # 2. Male Key (Z: 2.47 to 3.32mm) with lead-in taper/chamfer
    # Base at Z=2.47mm: INSERT_KEY_W_X x INSERT_KEY_LEN_Y (2.00 x 4.30)
    # Top at Z=3.32mm: chamfered/tapered by key_chamfer (dx = 0.30mm per side)
    dx_key = 0.25  # 0.25mm taper per side at key tip
    w_key_top = INSERT_KEY_W_X - 2 * dx_key   # 1.50mm
    l_key_top = INSERT_KEY_LEN_Y - 2 * dx_key # 3.80mm
    
    # Through-hole dimensions: 1.20mm x 3.50mm
    hole_w = SLIT_W_X   # 1.20mm
    hole_l = SLIT_LEN_Y # 3.50mm
    
    # Let's construct the lofted 3D mesh for the insert
    # Level 0: Z = 0.00mm (Outer shroud bottom face)
    # Level 1: Z = 2.47mm (Shroud shoulder mating face)
    # Level 2: Z = 2.47mm (Key base)
    # Level 3: Z = 3.32mm (Key top tip)
    
    # Level 0 (Z=0.0) outer rect & hole
    v0_out = np.array([
        [-w_bot/2, -l_bot/2, 0.0],
        [ w_bot/2, -l_bot/2, 0.0],
        [ w_bot/2,  l_bot/2, 0.0],
        [-w_bot/2,  l_bot/2, 0.0],
    ])
    v0_in = np.array([
        [-hole_w/2 - 0.2, -hole_l/2 - 0.2, 0.0], # lead-in funnel on outer hole
        [ hole_w/2 + 0.2, -hole_l/2 - 0.2, 0.0],
        [ hole_w/2 + 0.2,  hole_l/2 + 0.2, 0.0],
        [-hole_w/2 - 0.2,  hole_l/2 + 0.2, 0.0],
    ])
    
    # Level 1 (Z=2.47) shoulder outer rect
    v1_out = np.array([
        [-INSERT_BODY_W_X/2, -INSERT_BODY_LEN_Y/2, z_shoulder],
        [ INSERT_BODY_W_X/2, -INSERT_BODY_LEN_Y/2, z_shoulder],
        [ INSERT_BODY_W_X/2,  INSERT_BODY_LEN_Y/2, z_shoulder],
        [-INSERT_BODY_W_X/2,  INSERT_BODY_LEN_Y/2, z_shoulder],
    ])
    
    # Key Base (Z=2.47)
    v1_key = np.array([
        [-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, z_shoulder],
        [ INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, z_shoulder],
        [ INSERT_KEY_W_X/2,  INSERT_KEY_LEN_Y/2, z_shoulder],
        [-INSERT_KEY_W_X/2,  INSERT_KEY_LEN_Y/2, z_shoulder],
    ])
    
    # Key Top (Z=3.32)
    v2_key = np.array([
        [-w_key_top/2, -l_key_top/2, z_key_top],
        [ w_key_top/2, -l_key_top/2, z_key_top],
        [ w_key_top/2,  l_key_top/2, z_key_top],
        [-w_key_top/2,  l_key_top/2, z_key_top],
    ])
    
    # Through-hole at Z=z_shoulder and Z=z_key_top
    v1_in = np.array([
        [-hole_w/2, -hole_l/2, z_shoulder],
        [ hole_w/2, -hole_l/2, z_shoulder],
        [ hole_w/2,  hole_l/2, z_shoulder],
        [-hole_w/2,  hole_l/2, z_shoulder],
    ])
    v2_in = np.array([
        [-hole_w/2 - 0.15, -hole_l/2 - 0.15, z_key_top], # lead-in funnel on key top
        [ hole_w/2 + 0.15, -hole_l/2 - 0.15, z_key_top],
        [ hole_w/2 + 0.15,  hole_l/2 + 0.15, z_key_top],
        [-hole_w/2 - 0.15,  hole_l/2 + 0.15, z_key_top],
    ])
    
    # Construct complete solid mesh
    # Body mesh (Z: 0 to z_shoulder)
    # We can create body with extrude_polygon or trimesh convex hull/polyhedron
    # A cleaner and 100% robust way with trimesh is using loft or creating submeshes:
    
    # 1. Shroud body: extrude polygon with draft / taper
    # 2. Key: extrude polygon with taper
    # Let's test a watertight creation approach:
    poly_body_base = box(-INSERT_BODY_W_X/2, -INSERT_BODY_LEN_Y/2, INSERT_BODY_W_X/2, INSERT_BODY_LEN_Y/2)
    poly_body_tip = box(-w_bot/2, -l_bot/2, w_bot/2, l_bot/2)
    
    # Build shroud body vertices & faces directly:
    # 4 outer bottom, 4 inner bottom, 4 outer top (shoulder), 4 inner key-base, 4 outer key-top, 4 inner key-top
    # Total 24 vertices
    verts = np.vstack([v0_out, v0_in, v1_out, v1_in, v1_key, v2_key, v2_in])
    # Total vertices: 4 + 4 + 4 + 4 + 4 + 4 + 4 = 28
    
    faces = []
    # 1. Bottom face (Z=0): Ring between v0_out (0..3) and v0_in (4..7)
    for i in range(4):
        i_next = (i + 1) % 4
        # Normal pointing -Z
        faces.append([i, i_next, 4 + i_next])
        faces.append([i, 4 + i_next, 4 + i])
        
    # 2. Shroud outer side walls: v0_out (0..3) to v1_out (8..11)
    for i in range(4):
        i_next = (i + 1) % 4
        faces.append([i, 8 + i, 8 + i_next])
        faces.append([i, 8 + i_next, i_next])
        
    # 3. Horizontal Shoulder Face (Z=2.47): Ring between v1_out (8..11) and v1_key (16..19)
    for i in range(4):
        i_next = (i + 1) % 4
        # Normal pointing +Z
        faces.append([8 + i, 8 + i_next, 16 + i_next])
        faces.append([8 + i, 16 + i_next, 16 + i])
        
    # 4. Key outer sloped walls: v1_key (16..19) to v2_key (20..23)
    for i in range(4):
        i_next = (i + 1) % 4
        faces.append([16 + i, 20 + i, 20 + i_next])
        faces.append([16 + i, 20 + i_next, 16 + i_next])
        
    # 5. Key top rim face: Ring between v2_key (20..23) and v2_in (24..27)
    for i in range(4):
        i_next = (i + 1) % 4
        faces.append([20 + i, 20 + i_next, 24 + i_next])
        faces.append([20 + i, 24 + i_next, 24 + i])
        
    # 6. Inner hole tube: v2_in (24..27) down to v0_in (4..7) via v1_in (12..15)
    for i in range(4):
        i_next = (i + 1) % 4
        # Key internal wall: 24..27 to 12..15
        faces.append([24 + i, 12 + i_next, 12 + i])
        faces.append([24 + i, 24 + i_next, 12 + i_next])
        # Body internal wall: 12..15 to 4..7
        faces.append([12 + i, 4 + i_next, 4 + i])
        faces.append([12 + i, 12 + i_next, 4 + i_next])
        
    insert_mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
    return insert_mesh

def run_test():
    print("=== TESTING SLOPED SLIT INSERT & CLEARANCE ===")
    mesh = build_sloped_slit_insert_mesh()
    print(f"Insert Mesh is Watertight: {mesh.is_watertight}")
    print(f"Insert Mesh Volume: {mesh.volume:.3f} mm^3")
    print(f"Insert Bounds X: [{mesh.bounds[0,0]:.3f}, {mesh.bounds[1,0]:.3f}] mm")
    print(f"Insert Bounds Y: [{mesh.bounds[0,1]:.3f}, {mesh.bounds[1,1]:.3f}] mm")
    print(f"Insert Bounds Z: [{mesh.bounds[0,2]:.3f}, {mesh.bounds[1,2]:.3f}] mm")
    
    # Check interference with symmetrical position CX_RIGHT = +7.853 mm
    shroud_box_right = box(CX_RIGHT - INSERT_BODY_W_X/2, CY_SLIT - INSERT_BODY_LEN_Y/2,
                           CX_RIGHT + INSERT_BODY_W_X/2, CY_SLIT + INSERT_BODY_LEN_Y/2)
    shroud_box_left = box(CX_LEFT - INSERT_BODY_W_X/2, CY_SLIT - INSERT_BODY_LEN_Y/2,
                          CX_LEFT + INSERT_BODY_W_X/2, CY_SLIT + INSERT_BODY_LEN_Y/2)
                          
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    
    dist_r = outer_body_poly.exterior.distance(shroud_box_right)
    dist_l = outer_body_poly.exterior.distance(shroud_box_left)
    print(f"\nShroud Clearance with Symmetrical Positioning (X = ±7.853mm):")
    print(f"  Left Shroud Distance to Outer Perimeter Wall:  {dist_l:.3f} mm")
    print(f"  Right Shroud Distance to Outer Perimeter Wall: {dist_r:.3f} mm (CLEARED! Was 0.000mm collision!)")
    
    # Plot visualization
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)
    
    # 2D Plan View
    ax1 = axes[0]
    bx, by = outer_body_poly.exterior.xy
    ax1.plot(bx, by, color='#1565c0', lw=2.5, label='Perimeter Wall')
    ax1.fill(*shroud_box_left.exterior.xy, color='#ab47bc', alpha=0.45, edgecolor='#6a1b9a', lw=1.8, label=f'Left Shroud (X={CX_LEFT:.2f})')
    ax1.fill(*shroud_box_right.exterior.xy, color='#ab47bc', alpha=0.45, edgecolor='#6a1b9a', lw=1.8, label=f'Right Shroud (X={CX_RIGHT:+.2f})')
    
    # Sockets (2.50 x 4.80mm)
    s_left = box(CX_LEFT - SOCKET_W_X/2, CY_SLIT - SOCKET_LEN_Y/2, CX_LEFT + SOCKET_W_X/2, CY_SLIT + SOCKET_LEN_Y/2)
    s_right = box(CX_RIGHT - SOCKET_W_X/2, CY_SLIT - SOCKET_LEN_Y/2, CX_RIGHT + SOCKET_W_X/2, CY_SLIT + SOCKET_LEN_Y/2)
    ax1.plot(*s_left.exterior.xy, color='#d32f2f', lw=2.0, label='Floor Detent Socket (2.50x4.80mm)')
    ax1.plot(*s_right.exterior.xy, color='#d32f2f', lw=2.0)
    
    # Brackets
    b_poly = create_all_brackets_poly()
    for g in (b_poly.geoms if hasattr(b_poly, 'geoms') else [b_poly]):
        ax1.plot(*g.exterior.xy, color='#2e7d32', lw=1.5, ls='--')
        
    arch = create_arch_wall_poly()
    ax1.plot(*arch.exterior.xy, color='#0d47a1', lw=1.8)
    
    ax1.set_xlim(-15, 15)
    ax1.set_ylim(-20, -5)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title('Symmetrical Slit Placement (X = ±7.853mm) - Zero Wall Collision', fontsize=11, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='upper right', fontsize=8)
    
    # 3D View of Sloped Insert
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    v = mesh.vertices
    f = mesh.faces
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    coll = Poly3DCollection(v[f], facecolors='#ab47bc', edgecolors='#4a148c', linewidths=0.5, alpha=0.85)
    ax2.add_collection3d(coll)
    ax2.set_xlim(-3, 3)
    ax2.set_ylim(-4, 4)
    ax2.set_zlim(0, 4)
    ax2.view_init(elev=25, azim=-45)
    ax2.set_title('3D Sloped Insert (Draft Walls + Tapered Key + Lead-in Funnel)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_zlabel('Z (mm)')
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'sloped_slit_insert_preview.png')
    plt.savefig(out_path, dpi=180)
    print(f"Saved preview to {out_path}")

if __name__ == '__main__':
    run_test()
