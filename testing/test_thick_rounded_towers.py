"""
testing/test_thick_rounded_towers.py
Prototype and verification for thicker, rounded top tower enclosure:
1. Replaces flat top with a smooth rounded arch profile over the axle.
2. Increases top wall thickness over the teardrop bore to >= 1.20mm solid plastic.
3. Blends smoothly with front vertical land and rear cross-tie bridge.
4. Validates clearances to shaft rocker, hub barrel, and kinematic rotation.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
import matplotlib.pyplot as plt

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, HUB_DIAMETER,
    build_shaft_rocker_mesh
)
from build_part import (
    BASE_THICK, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

def create_rounded_tower_poly(
    r_bore=1.65,
    arch_rx=2.85, # Radius in Y
    arch_rz=3.00, # Radius in Z (Apex at Z = 12.59 + 3.00 = 15.59mm)
    y_min_base=6.250,
    y_max_base=12.850,
    z_base=1.000,
    z_land_bot=11.200
):
    y_shaft = Y_AXLE      # 9.279 mm
    z_shaft = Z_AXLE      # 12.590 mm
    
    # 1. Rounded Exterior Arch over the Axle
    # Tangent points: front wall at Y = y_shaft - arch_rx (approx 6.43mm)
    # rear wall at Y = y_shaft + arch_rx (approx 12.13mm)
    # Arch from theta = 0 (rear) to theta = pi (front)
    theta_arch = np.linspace(0, np.pi, 48)
    arch_pts = [(y_shaft + arch_rx * np.cos(t), z_shaft + arch_rz * np.sin(t)) for t in theta_arch]
    # arch_pts[0] is rear tangent: (y_shaft + arch_rx, z_shaft)
    # arch_pts[-1] is front tangent: (y_shaft - arch_rx, z_shaft)
    
    y_rear_tangent = y_shaft + arch_rx
    y_front_tangent = y_shaft - arch_rx
    
    exterior_pts = [
        (y_min_base, z_base),
        (y_max_base, z_base),
        (y_rear_tangent, z_land_bot),
        (y_rear_tangent, z_shaft),
    ] + arch_pts + [
        (y_front_tangent, z_shaft),
        (y_front_tangent, z_land_bot),
    ]
    
    # 2. Teardrop Bore Profile (with 45° peaked apex pointing in machine vertical direction)
    phi_up = 3 * np.pi / 4.0 # 135 degrees
    phi_arc = np.linspace(phi_up + np.pi/4, phi_up + 7*np.pi/4, 48)
    arc_pts = [(y_shaft + r_bore * np.cos(p), z_shaft + r_bore * np.sin(p)) for p in phi_arc]
    peak_pt = (y_shaft + r_bore * np.sqrt(2.0) * np.cos(phi_up),
               z_shaft + r_bore * np.sqrt(2.0) * np.sin(phi_up))
    bore_pts = arc_pts + [peak_pt]
    
    poly_yz = Polygon(exterior_pts, [bore_pts])
    return poly_yz, arch_pts, bore_pts

def build_thick_rounded_towers_mesh():
    poly_yz, _, _ = create_rounded_tower_poly()
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=TOWER_WALL_THICK)
    verts = m_raw.vertices.copy()
    
    verts_left = np.column_stack([verts[:, 2] + 3.900, verts[:, 0], verts[:, 1]])
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    if mesh_left.volume < 0:
        mesh_left.faces = np.fliplr(mesh_left.faces)
        
    verts_right = np.column_stack([verts[:, 2] + 13.100, verts[:, 0], verts[:, 1]])
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    if mesh_right.volume < 0:
        mesh_right.faces = np.fliplr(mesh_right.faces)
        
    # Rear Monolithic Cross-Tie Bridge
    # Spans X in [5.40, 13.10] (width 7.70mm)
    # Y in [11.60, 12.85] (thickness 1.25mm)
    # Z in [12.60, 15.00] (height 2.40mm - thicker and taller to match rounded crown!)
    bridge_box = trimesh.creation.box([TOWER_INTERNAL_GAP, 1.25, 2.40])
    bridge_box.apply_translation([
        (5.40 + 13.10) / 2.0,       # X center = 9.25 mm
        (11.60 + 12.85) / 2.0,      # Y center = 12.225 mm
        (12.60 + 15.00) / 2.0       # Z center = 13.80 mm
    ])
    
    return trimesh.util.concatenate([mesh_left, mesh_right, bridge_box])

def main():
    print("Testing Thicker Rounded Tower Enclosure...")
    poly_yz, arch_pts, bore_pts = create_rounded_tower_poly()
    print(f"Polygon is valid: {poly_yz.is_valid}, Area: {poly_yz.area:.2f} mm2")
    
    # Calculate minimum top roof thickness
    y_shaft, z_shaft = Y_AXLE, Z_AXLE
    top_apex_z = z_shaft + 3.00 # 15.59 mm
    bore_top_z = z_shaft + 1.65 # 14.24 mm
    min_thickness = top_apex_z - bore_top_z
    print(f"Top crown apex: Z = {top_apex_z:.2f} mm")
    print(f"Bore peak:      Z = {bore_top_z:.2f} mm")
    print(f"Roof thickness at apex: {min_thickness:.2f} mm (Thick solid plastic!)")
    
    towers = build_thick_rounded_towers_mesh()
    print(f"Towers mesh volume: {towers.volume:.2f} mm3, Watertight: {towers.is_watertight}")
    print(f"Towers bounds Z: [{towers.bounds[0, 2]:.2f}, {towers.bounds[1, 2]:.2f}] mm")
    
    # Check clearance to shaft
    shaft = build_shaft_rocker_mesh(hub_w=7.20, in_assembly_coords=True, with_supports=False)
    from scipy.spatial import cKDTree
    tree = cKDTree(towers.vertices)
    dists, _ = tree.query(shaft.vertices)
    print(f"Min clearance to shaft: {np.min(dists):.3f} mm")
    
    # Kinematic rotation check
    pivot_pt = np.array([0, Y_AXLE, Z_AXLE])
    for angle_deg in [0.0, 4.0, 8.0, 10.3, 12.0]:
        rad = np.radians(angle_deg)
        T1 = trimesh.transformations.translation_matrix(-pivot_pt)
        R_x = trimesh.transformations.rotation_matrix(rad, [1, 0, 0])
        T2 = trimesh.transformations.translation_matrix(pivot_pt)
        M_rot = T2 @ R_x @ T1
        shaft_rot = shaft.copy().apply_transform(M_rot)
        d_rot, _ = tree.query(shaft_rot.vertices)
        print(f"  Theta = {angle_deg:4.1f}° -> Min clearance: {np.min(d_rot):.3f} mm")
        assert np.min(d_rot) >= 0.22, "Clearance too small!"
        
    # Plot side cross-section
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150, facecolor='#1e272e')
    ax.set_facecolor('#0f1419')
    ax.set_title("Thicker Rounded Tower Enclosure Profile (Y-Z)", color='white', weight='bold')
    
    x_ext, y_ext = poly_yz.exterior.xy
    ax.plot(x_ext, y_ext, color='#3498db', linewidth=2.5, label='Thick Rounded Tower Profile')
    ax.fill(x_ext, y_ext, color='#3498db', alpha=0.3)
    
    for interior in poly_yz.interiors:
        xi, yi = interior.xy
        ax.plot(xi, yi, color='#e74c3c', linewidth=2, label='Teardrop Bore (Ø3.30mm)')
        ax.fill(xi, yi, color='#0f1419')
        
    # Draw Axle Pin
    pin_circle = Point(Y_AXLE, Z_AXLE).buffer(PIN_DIAMETER / 2.0)
    xp, yp = pin_circle.exterior.xy
    ax.plot(xp, yp, color='#f1c40f', linewidth=2, label=f'Axle Pin (Ø{PIN_DIAMETER:.2f}mm)')
    ax.fill(xp, yp, color='#f1c40f', alpha=0.5)
    
    ax.plot([Y_AXLE], [Z_AXLE], 'w+', markersize=12, label='Axle Center (Y=9.28, Z=12.59)')
    
    # Annotate roof thickness
    ax.annotate(f'Thick Solid Roof: {min_thickness:.2f}mm',
                xy=(Y_AXLE, top_apex_z), xytext=(Y_AXLE - 2.5, top_apex_z + 0.8),
                arrowprops=dict(arrowstyle='->', color='#2ecc71', lw=2),
                color='#2ecc71', fontweight='bold', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.3', fc='#1e272e', ec='#2ecc71', lw=1.5))
    
    ax.set_xlabel("Y (mm)", color='white')
    ax.set_ylabel("Z (mm)", color='white')
    ax.tick_params(colors='white')
    ax.grid(True, color='#2c3e50', alpha=0.5)
    ax.set_aspect('equal')
    ax.legend(loc='lower left')
    
    out_png = os.path.join(os.path.dirname(__file__), 'thick_rounded_tower_profile.png')
    plt.tight_layout()
    plt.savefig(out_png)
    print(f"Saved profile visualization to: {out_png}")
    print("SUCCESS: Thicker rounded tower profile verified cleanly!")

if __name__ == '__main__':
    main()
