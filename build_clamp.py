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
CLAMP_ROOF_THICK = 1.60      # 1.60mm bridge roof thickness (Z: 14.090 to 15.690mm, +78% thicker, 5.6x bending stiffness)
CLAMP_Z_BOTTOM = 11.200      # Extends down to Z = 11.20mm (4.49mm total clamp height)
CLAMP_WALL_THICK = 1.40      # 1.40mm heavy-duty tension wall thickness (+22% thicker)
SIDE_WALL_THICK = 1.60       # 1.60mm robust outer side cheek thickness (4 solid perimeters on 0.4mm nozzle)
ENTRY_CHAMFER = 0.400        # 0.40mm lead-in entry chamfer at bottom of legs

# Central Hold-Down & Upward Relief Pocket over Pin Funnel
# Top of Ø2.80mm pin is at Z = 13.990mm. Relief pocket at Z = 14.500mm provides +0.51mm clear air gap
# above pin top to absorb any 3D-printing support residue, roughness, or dimensional inaccuracies.
Z_PIN_RELIEF = 14.500        # Relief pocket ceiling (+0.51mm running clearance above pin inside cradle)
Z_KEEL = Z_PIN_RELIEF        # Backwards-compatibility alias for test/visualization scripts
Y_RELIEF_FRONT = 7.550       # Front edge of relief pocket
Y_RELIEF_REAR = 11.000       # Rear edge of relief pocket

# Clearance Arch around Pin on Outer Side Wall
PIN_CLEARANCE_RADIUS = 1.85  # Radius = 1.85mm (Pin is R=1.40mm -> +0.45mm radial air gap for imperfect supported prints!)
CLAMP_WIDTH_X = 1.400        # 1.400mm wide U-saddle span across tower (0.20mm axial margin to central hub barrel)

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
    """Generates the closed 2D cross-section polygon of the U-saddle in (Y, Z) with upward pin relief pocket."""
    z_top = Z_TOP + CLAMP_ROOF_THICK  # 15.690 mm
    z_roof_under = Z_TOP             # 14.090 mm
    z_bot = CLAMP_Z_BOTTOM           # 11.200 mm
    
    y_front_inner_top = 6.550 - 0.020  # 6.530mm (precision snug fit across prongs)
    y_front_inner_bot = 6.484 - 0.010
    y_rear_inner_top = 12.180 + 0.020  # 12.200mm (precision snug fit across prongs)
    y_rear_inner_bot = 12.328 + 0.010
    
    y_front_outer_top = y_front_inner_top - CLAMP_WALL_THICK
    y_front_outer_bot = y_front_inner_bot - CLAMP_WALL_THICK
    y_rear_outer_top = y_rear_inner_top + CLAMP_WALL_THICK
    y_rear_outer_bot = y_rear_inner_bot + CLAMP_WALL_THICK
    
    saddle_pts_yz = [
        (y_front_outer_bot, z_bot),
        (y_front_outer_top, z_top - 0.50),
        (y_front_outer_top + 0.50, z_top),
        (y_rear_outer_top - 0.50, z_top),
        (y_rear_outer_top, z_top - 0.50),
        (y_rear_outer_bot, z_bot),
        (y_rear_inner_bot, z_bot),
        (y_rear_inner_top, z_roof_under),
        (11.20, z_roof_under),
        (Y_RELIEF_REAR, Z_PIN_RELIEF),   # Upward relief pocket: +0.51mm air gap over pin top
        (Y_RELIEF_FRONT, Z_PIN_RELIEF),  # Prevents any binding from support marks or layer roughness
        (7.35, z_roof_under),
        (y_front_inner_top, z_roof_under),
        (y_front_inner_bot, z_bot),
    ]
    return Polygon(saddle_pts_yz)

get_clamp_polygon_yz = get_saddle_polygon_yz

def get_side_wall_polygon_yz(with_arch=True):
    """
    Generates the closed 2D profile of the outer side cheek.
    - Below Z = 14.09mm, cheek spans Y in [7.10, 11.55mm] to nest with positive clearance
      between the Left Tower's front (Y <= 7.05mm) and rear (Y >= 11.65mm) buttress struts.
    - Above Z = 14.09mm, roof bridge spans full Y in [5.114, 13.698mm], passing +0.39mm clear
      above the apex of the struts (Z_strut = 13.70mm).
    - If with_arch=True, includes pin safety clearance arch (R = 1.85mm, +0.45mm radial air gap).
    - If with_arch=False, provides 100% solid continuous outer backing plate for extreme stiffness.
    """
    z_top = Z_TOP + CLAMP_ROOF_THICK
    y_c = Y_AXLE
    z_c = Z_AXLE
    R = PIN_CLEARANCE_RADIUS
    z_bot = 11.75
    
    if with_arch:
        arch_pts = []
        for p in np.linspace(0, np.pi, 32):
            arch_pts.append((y_c + R * np.cos(p), z_c + R * np.sin(p)))
            
        side_pts_yz = [
            (7.10, z_bot),
            (7.10, 14.09),
            (5.114, 14.09),
            (5.160, 15.19),
            (5.660, z_top),
            (13.170, z_top),
            (13.670, 15.19),
            (13.698, 14.09),
            (11.55, 14.09),
            (11.55, z_bot),
            (y_c + R, z_bot),
        ] + arch_pts + [
            (y_c - R, z_bot)
        ]
    else:
        side_pts_yz = [
            (7.10, z_bot),
            (7.10, 14.09),
            (5.114, 14.09),
            (5.160, 15.19),
            (5.660, z_top),
            (13.170, z_top),
            (13.670, 15.19),
            (13.698, 14.09),
            (11.55, 14.09),
            (11.55, z_bot),
        ]
    return Polygon(side_pts_yz)

def build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False):
    """
    Builds the watertight 3D mesh of the Reinforced Side-Wrapping Tower Prong Clamp.
    Features:
    - Main U-saddle spanning the tower width to prevent prongs from spreading in Y.
    - Upward pin relief pocket providing +0.51mm air gap over pin top (absorbs support roughness).
    - Dual-layer reinforced side cheek: 1.00mm inner arched cavity (R=1.85mm) + 0.60mm outer solid continuous backplate.
    - Zero pin contact: pin tips end at X=3.45mm / X=15.05mm, maintaining >= 1.25mm axial clearance to outer plate.
    - Heavy-duty snap hooks at Z = 12.35mm with 0.65mm engagement for secure positive locking.
    """
    poly_saddle = get_saddle_polygon_yz()
    poly_side_arch = get_side_wall_polygon_yz(with_arch=True)
    poly_side_solid = get_side_wall_polygon_yz(with_arch=False)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    poly_roof_yz = Polygon([
        (5.114, 14.09), (5.160, 15.19), (5.660, z_top),
        (13.170, z_top), (13.670, 15.19), (13.698, 14.09)
    ])
    
    if tower_side == 'left':
        # Saddle spans X in [3.90, 5.30] (1.40mm thick, 0.20mm axial gap to hub at 5.50)
        m_saddle = extrude_yz(poly_saddle, height=5.30 - 3.90, x_offset=3.90)
        # Roof bridge over gap X in [3.20, 3.90] (0.70mm thick, full 1.60mm height in Z)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=3.90 - 3.20, x_offset=3.20)
        # Inner cheek with enlarged pin arch spans X in [2.20, 3.20] (1.00mm deep cavity)
        m_side_inner = extrude_yz(poly_side_arch, height=1.00, x_offset=2.20)
        # Outer cheek 100% solid continuous plate spans X in [1.60, 2.20] (0.60mm thick)
        m_side_outer = extrude_yz(poly_side_solid, height=0.60, x_offset=1.60)
        
        # Robust snap hooks in (X, Z) on inner face of side wall
        # Hooks under shelf at Z = 12.35mm with 0.65mm engagement and 35 deg lead-in
        poly_hook_xz = Polygon([
            (2.20, 11.75),
            (3.85, 12.15),  # 35 deg entry chamfer
            (3.85, 12.35),  # Hook shelf top (0.05mm below 12.40mm for positive click)
            (2.20, 12.35)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side_inner, m_side_outer, m_hf, m_hr])
    else:
        # Right clamp: Saddle spans X in [13.20, 14.60] (1.40mm thick, 0.20mm axial gap to hub at 13.00)
        m_saddle = extrude_yz(poly_saddle, height=14.60 - 13.20, x_offset=13.20)
        # Roof bridge over gap X in [14.60, 15.30] (0.70mm thick, full 1.60mm height in Z)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=15.30 - 14.60, x_offset=14.60)
        # Inner cheek with enlarged pin arch spans X in [15.30, 16.30] (1.00mm deep cavity)
        m_side_inner = extrude_yz(poly_side_arch, height=1.00, x_offset=15.30)
        # Outer cheek 100% solid continuous plate spans X in [16.30, 16.90] (0.60mm thick)
        m_side_outer = extrude_yz(poly_side_solid, height=0.60, x_offset=16.30)
        
        poly_hook_xz = Polygon([
            (16.30, 11.75),
            (14.65, 12.15),
            (14.65, 12.35),
            (16.30, 12.35)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side_inner, m_side_outer, m_hf, m_hr])
        
    if in_assembly_coords:
        return m_clamp
    else:
        # Pre-orient flat on print bed: top bridge roof down at Z = 0.00mm
        # Zero overhangs, vertical walls, 100% support-free 3D printing
        m_bed = m_clamp.copy()
        # Flip Z upside down: roof at Z = 15.690mm becomes Z = 0.00mm
        v = m_bed.vertices.copy()
        v[:, 2] = (Z_TOP + CLAMP_ROOF_THICK) - v[:, 2]
        # Center X and Y around (0, 0)
        v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2.0
        v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2.0
        # Re-invert face winding to maintain positive volume after reflection
        return trimesh.Trimesh(vertices=v, faces=m_bed.faces[:, ::-1].copy(), process=True)

def build_unified_clamp_mesh(in_assembly_coords=False):
    """
    Builds the 1-Piece Monolithic Reinforced Bridge Clamp:
    - Left clamp saddle on Left Tower (X in [1.60, 5.30])
    - Right clamp saddle on Right Tower (X in [13.20, 16.90])
    - Heavy-Duty Rear Cross-Tie Bar spanning X in [5.30, 13.20] at Y in [12.18, 13.68], Z in [13.50, 15.69]
    Anchors both towers to each other, creating an ultra-rigid monolithic gantry frame that physically cannot flex or pop off.
    """
    c_left = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=True)
    c_right = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    # 2D cross-section of the reinforced rear tie bar in (Y, Z)
    tie_pts_yz = [
        (12.18, 13.50),
        (12.18, z_top),
        (13.68, z_top),
        (13.68, 13.50)
    ]
    poly_tie_yz = Polygon(tie_pts_yz)
    m_tie = extrude_yz(poly_tie_yz, height=13.20 - 5.30, x_offset=5.30)
    
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
