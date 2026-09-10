"""
build_clamp.py
Standalone CAD generator script for the 3D-printable Anti-Spreading Tower Prong Clamps
with Side-Wrapping Snap Retention (Option 2: Zero Pin Friction, 100% Solid Prongs).
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

from build_shaft import Y_AXLE, Z_AXLE, PIN_DIAMETER

# Global Geometric Dimensions
Z_TOP = 14.090               # Tower top elevation
CLAMP_ROOF_THICK = 0.90      # 0.90mm bridge roof thickness (Z: 14.090 to 14.990mm)
CLAMP_Z_BOTTOM = 11.200      # Extends down to Z = 11.20mm (3.79mm total clamp height)
CLAMP_WALL_THICK = 1.15      # 1.15mm heavy-duty tension wall thickness
SIDE_WALL_THICK = 1.00       # 1.00mm robust outer side cheek thickness
ENTRY_CHAMFER = 0.350        # 0.35mm lead-in entry chamfer at bottom of legs

# Central Hold-Down Keel
Z_KEEL = 14.020              # Keel bottom elevation (0.030mm running clearance above pin inside cradle)
Y_KEEL_FRONT = 7.650         # Keel front face (inside funnel gap)
Y_KEEL_REAR = 10.908         # Keel rear face (inside funnel gap)

# Clearance Arch around Pin on Outer Side Wall
PIN_CLEARANCE_RADIUS = 1.70  # Radius = 1.70mm (Pin is R=1.40mm -> >= 0.30mm radial air gap, zero pin friction!)
CLAMP_WIDTH_X = 1.475        # 1.475mm wide U-saddle span across tower

def extrude_xz(poly_xz, height, y_offset=0.0):
    """Extrudes an (X, Z) polygon along Y with correct normal orientation."""
    m_raw = trimesh.creation.extrude_polygon(poly_xz, height=height)
    v = m_raw.vertices.copy()
    v_new = np.column_stack([v[:, 0], v[:, 2] + y_offset, v[:, 1]])
    return trimesh.Trimesh(vertices=v_new, faces=m_raw.faces[:, ::-1].copy(), process=True)

def extrude_yz(poly_yz, height, x_offset=0.0):
    """Extrudes a (Y, Z) polygon along X with correct normal orientation."""
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=height)
    v = m_raw.vertices.copy()
    v_new = np.column_stack([v[:, 2] + x_offset, v[:, 0], v[:, 1]])
    return trimesh.Trimesh(vertices=v_new, faces=m_raw.faces.copy(), process=True)

def unary_union_meshes(meshes):
    """Robust union of multiple touching/overlapping manifold meshes."""
    m_res = meshes[0]
    for m in meshes[1:]:
        m_res = m_res.union(m, engine='manifold')
    return m_res

def get_saddle_polygon_yz():
    """Generates the closed 2D cross-section polygon of the U-saddle in (Y, Z)."""
    z_top = Z_TOP + CLAMP_ROOF_THICK  # 14.990 mm
    z_roof_under = Z_TOP             # 14.090 mm
    z_bot = CLAMP_Z_BOTTOM           # 11.200 mm
    
    y_front_inner_top = 6.550 - 0.040
    y_front_inner_bot = 6.484 - 0.020
    y_rear_inner_top = 12.180 + 0.040
    y_rear_inner_bot = 12.328 + 0.020
    
    y_front_outer_top = y_front_inner_top - CLAMP_WALL_THICK
    y_front_outer_bot = y_front_inner_bot - CLAMP_WALL_THICK
    y_rear_outer_top = y_rear_inner_top + CLAMP_WALL_THICK
    y_rear_outer_bot = y_rear_inner_bot + CLAMP_WALL_THICK
    
    saddle_pts_yz = [
        (y_front_outer_bot, z_bot),
        (y_front_outer_top, z_top - 0.40),
        (y_front_outer_top + 0.40, z_top),
        (y_rear_outer_top - 0.40, z_top),
        (y_rear_outer_top, z_top - 0.40),
        (y_rear_outer_bot, z_bot),
        (y_rear_inner_bot, z_bot),
        (y_rear_inner_top, z_roof_under),
        (Y_KEEL_REAR, z_roof_under),
        (Y_KEEL_REAR, Z_KEEL),
        (Y_KEEL_FRONT, Z_KEEL),
        (Y_KEEL_FRONT, z_roof_under),
        (y_front_inner_top, z_roof_under),
        (y_front_inner_bot, z_bot),
    ]
    return Polygon(saddle_pts_yz)

get_clamp_polygon_yz = get_saddle_polygon_yz

def get_side_wall_polygon_yz():
    """
    Generates the closed 2D profile of the outer side cheek with central pin clearance arch.
    Features:
    - Below Z = 14.09mm, cheek spans Y in [7.10, 11.55mm] to nest with positive clearance
      between the Left Tower's front (Y <= 7.05mm) and rear (Y >= 11.65mm) buttress struts.
    - Above Z = 14.09mm, roof bridge spans full Y in [5.314, 13.498mm], passing +0.39mm clear
      above the apex of the struts (Z_strut = 13.70mm).
    - Clearance arch (R = 1.70mm) maintains >= 0.30mm radial air gap around the pin (zero friction!).
    """
    z_top = Z_TOP + CLAMP_ROOF_THICK
    y_c = Y_AXLE
    z_c = Z_AXLE
    R = PIN_CLEARANCE_RADIUS
    z_bot = 11.75
    
    arch_pts = []
    for p in np.linspace(0, np.pi, 32):
        arch_pts.append((y_c + R * np.cos(p), z_c + R * np.sin(p)))
        
    side_pts_yz = [
        (7.10, z_bot),
        (7.10, 14.09),
        (5.314, 14.09),
        (5.360, 14.59),
        (5.760, 14.99),
        (13.370, 14.99),
        (13.370, 14.59),
        (13.498, 14.09),
        (11.55, 14.09),
        (11.55, z_bot),
        (y_c + R, z_bot),
    ] + arch_pts + [
        (y_c - R, z_bot)
    ]
    return Polygon(side_pts_yz)

def build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False):
    """
    Builds the watertight 3D mesh of the Side-Wrapping Anti-Spreading Tower Prong Clamp.
    Features:
    - Main U-saddle spanning the 1.50mm tower width to prevent prongs from spreading in Y.
    - Outer side wall with central pin clearance arch (>= 0.30mm air gap, zero pin friction!).
    - Robust dual inward snap hooks with 0.65mm undercut depth at Z = 12.40mm for positive locking.
    """
    poly_saddle = get_saddle_polygon_yz()
    poly_side = get_side_wall_polygon_yz()
    
    # Common roof bridging polygon across the gap above Z = 14.09mm
    poly_roof_yz = Polygon([
        (5.314, 14.09), (5.360, 14.59), (5.760, 14.99),
        (13.370, 14.99), (13.370, 14.59), (13.498, 14.09)
    ])
    
    if tower_side == 'left':
        # Saddle spans X in [3.90, 5.375] (1.475mm thick)
        m_saddle = extrude_yz(poly_saddle, height=1.475, x_offset=3.90)
        # Roof bridge over gap X in [3.20, 3.90] (0.70mm thick)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=3.90 - 3.20, x_offset=3.20)
        # Side wall spans X in [2.20, 3.20] (1.00mm thick)
        m_side = extrude_yz(poly_side, height=1.00, x_offset=2.20)
        
        # Robust snap hooks in (X, Z) on inner face of side wall (X in [2.20, 3.85])
        # Hooks under shelf at Z = 12.40mm with 0.65mm engagement
        poly_hook_xz = Polygon([
            (2.20, 11.75),
            (3.85, 12.20),  # 45 deg entry chamfer
            (3.85, 12.40),  # Hook shelf top
            (2.20, 12.40)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side, m_hf, m_hr])
    else:
        # Right clamp: Saddle spans X in [13.125, 14.60] (1.475mm thick)
        m_saddle = extrude_yz(poly_saddle, height=1.475, x_offset=13.125)
        # Roof bridge over gap X in [14.60, 15.30] (0.70mm thick)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=15.30 - 14.60, x_offset=14.60)
        # Side wall spans X in [15.30, 16.30] (1.00mm thick)
        m_side = extrude_yz(poly_side, height=1.00, x_offset=15.30)
        
        poly_hook_xz = Polygon([
            (16.30, 11.75),
            (14.65, 12.20),
            (14.65, 12.40),
            (16.30, 12.40)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side, m_hf, m_hr])
        
    if in_assembly_coords:
        return m_clamp
    else:
        # Pre-orient flat on print bed: top bridge roof down at Z = 0.00mm
        # Zero overhangs, vertical walls, 100% support-free 3D printing
        m_bed = m_clamp.copy()
        # Flip Z upside down: roof at Z = 14.990mm becomes Z = 0.00mm
        v = m_bed.vertices.copy()
        v[:, 2] = (Z_TOP + CLAMP_ROOF_THICK) - v[:, 2]
        # Center X and Y around (0, 0)
        v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2.0
        v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2.0
        # Re-invert face winding to maintain positive volume after reflection
        return trimesh.Trimesh(vertices=v, faces=m_bed.faces[:, ::-1].copy(), process=True)

def build_unified_clamp_mesh(in_assembly_coords=False):
    """
    Builds the 1-Piece Monolithic Bridge Clamp:
    - Left clamp saddle on Left Tower (X in [3.00, 5.375])
    - Right clamp saddle on Right Tower (X in [13.125, 15.50])
    - Rigid Rear Cross-Tie Bar spanning X in [5.375, 13.125] at Y in [12.18, 13.38], Z in [13.70, 14.99]
    Anchors both towers to each other, creating a rigid monolithic gantry frame that physically cannot fall off.
    """
    c_left = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=True)
    c_right = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)
    
    # 2D cross-section of the rear tie bar in (Y, Z)
    tie_pts_yz = [
        (12.18, 13.70),
        (12.18, 14.99),
        (13.38, 14.99),
        (13.38, 13.70)
    ]
    poly_tie_yz = Polygon(tie_pts_yz)
    m_tie = extrude_yz(poly_tie_yz, height=13.125 - 5.375, x_offset=5.375)
    
    unified_clamp = unary_union_meshes([c_left, m_tie, c_right])
    
    if in_assembly_coords:
        return unified_clamp
    else:
        # Pre-orient flat on print bed: top bridge roof down at Z = 0.00mm
        m_bed = unified_clamp.copy()
        v = m_bed.vertices.copy()
        v[:, 2] = (Z_TOP + CLAMP_ROOF_THICK) - v[:, 2]
        v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2.0
        v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2.0
        return trimesh.Trimesh(vertices=v, faces=m_bed.faces[:, ::-1].copy(), process=True)

def build_tower_clamps_pair_mesh(spacing=5.0):
    """
    Creates a pre-arranged pair of separate clamps (1 Left, 1 Right) oriented flat on the
    print bed (Z = 0.00mm) spaced side-by-side for 1-click support-free 3D printing.
    """
    c_left = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False)
    c_right = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=False)
    
    # Arrange along X on print bed
    dx = (c_left.bounds[1, 0] - c_left.bounds[0, 0]) + spacing
    c_left.apply_translation([-dx / 2.0, 0.0, 0.0])
    c_right.apply_translation([dx / 2.0, 0.0, 0.0])
    
    return trimesh.util.concatenate([c_left, c_right])

def export_openscad_clamp(filename='tower_clamp.scad'):
    """Exports parametric OpenSCAD reference model."""
    scad_content = f"""// Kia EV6 Outlet Interlock - Anti-Spreading Tower Prong Clamp (Option 2)
// Generated by build_clamp.py

$fn = 64;

// Global parameters
z_top = {Z_TOP};
roof_thick = {CLAMP_ROOF_THICK};
wall_thick = {CLAMP_WALL_THICK};
side_thick = {SIDE_WALL_THICK};
pin_clearance_r = {PIN_CLEARANCE_RADIUS};
y_axle = {Y_AXLE};
z_axle = {Z_AXLE};

module tower_clamp_left() {{
    // Left Tower Clamp with outer side retention ears and zero pin contact
    difference() {{
        union() {{
            // Main U-saddle
            translate([3.90, 0, 0])
                linear_extrude(height = 1.475)
                    polygon(points = [
                        [5.314, 11.20], [5.360, 14.59], [5.760, 14.99],
                        [13.370, 14.99], [13.370, 14.59], [13.498, 11.20],
                        [12.698, 11.20], [12.348, 11.55], [12.220, 14.09],
                        [11.208, 14.09], [10.908, 14.17], [10.758, 14.02],
                        [7.800, 14.02], [7.650, 14.17], [7.350, 14.09],
                        [6.510, 14.09], [6.464, 11.55], [6.114, 11.20]
                    ]);
            // Outer side wall
            translate([3.00, 0, 0])
                linear_extrude(height = 0.90)
                    difference() {{
                        polygon(points = [
                            [5.314, 12.10], [5.360, 14.59], [5.760, 14.99],
                            [13.370, 14.99], [13.370, 14.59], [13.498, 12.10],
                            [10.75, 12.10], [7.80, 12.10]
                        ]);
                        // Pin clearance arch
                        translate([y_axle, z_axle])
                            circle(r = pin_clearance_r);
                    }}
        }}
    }}
}}

tower_clamp_left();
"""
    with open(filename, 'w') as f:
        f.write(scad_content)
    print(f"Exported OpenSCAD reference: {filename}")

def main():
    print("=" * 80)
    # 1. Unified Monolithic Bridge Clamp (Option 2 - Both Towers Anchoring Each Other)
    bridge_clamp = build_unified_clamp_mesh(in_assembly_coords=False)
    bridge_clamp.export('tower_clamp_bridge.stl')
    bridge_clamp.export('tower_clamp_bridge.obj')
    bridge_clamp.export('tower_clamp.stl')
    bridge_clamp.export('tower_clamp.obj')
    bb = bridge_clamp.bounds
    print(f"Saved tower_clamp_bridge.stl / .obj (Watertight: {bridge_clamp.is_watertight}, Volume: {bridge_clamp.volume:.2f} mm^3)")
    print(f"  Bed Footprint: {bb[1,0]-bb[0,0]:.2f} x {bb[1,1]-bb[0,1]:.2f} mm (Z = {bb[1,2]-bb[0,2]:.2f} mm)")
    
    # 2. Left and Right Individual Clamps
    clamp_l = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False)
    clamp_l.export('tower_clamp_left.stl')
    clamp_l.export('tower_clamp_left.obj')
    print(f"Saved tower_clamp_left.stl / .obj (Watertight: {clamp_l.is_watertight}, Volume: {clamp_l.volume:.2f} mm^3)")
    
    clamp_r = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=False)
    clamp_r.export('tower_clamp_right.stl')
    clamp_r.export('tower_clamp_right.obj')
    print(f"Saved tower_clamp_right.stl / .obj (Watertight: {clamp_r.is_watertight}, Volume: {clamp_r.volume:.2f} mm^3)")
    
    # 3. Paired Build Plate
    pair_mesh = build_tower_clamps_pair_mesh(spacing=4.0)
    pair_mesh.export('tower_clamps_pair.stl')
    b = pair_mesh.bounds
    print(f"Saved tower_clamps_pair.stl (Watertight: {pair_mesh.is_watertight}, Volume: {pair_mesh.volume:.2f} mm^3)")
    print(f"  Bed Footprint: {b[1,0]-b[0,0]:.2f} x {b[1,1]-b[0,1]:.2f} mm (Z = {b[1,2]-b[0,2]:.2f} mm)")
    
    # 4. OpenSCAD reference
    export_openscad_clamp('tower_clamp.scad')
    
    print("=" * 80)
    print("OPTION 2 TOWER CLAMP CAD GENERATION COMPLETE!")
    print("=" * 80)

if __name__ == '__main__':
    main()
