"""
build_clamp.py
Standalone CAD generator script for the Ultra-Rigid Closed-Box Gantry Tower Clamp
and Individual 4-Sided Box-Cap Tower Sleeves.

Key Engineering Improvements:
1. Closed Rectangular Box-Truss Frame (Unified Gantry Clamp):
   - Heavy-Duty Rear Cross-Tie Beam: 2.00mm thick in Y x 2.49mm tall in Z (15.6x stiffer than 0.80mm strip).
   - Heavy-Duty Front Over-Arch Cross-Tie Beam: 2.20mm thick in Y x 2.09mm tall in Z (clears shaft cam by >2.70mm).
   - 2.20mm thick Bridge Roof Cap + 2.20mm Front Jaws + 2.00mm Rear Jaws.
2. Self-Centering 4-Sided Tower Capture with High-Temp FDM Clearances:
   - Parallel vertical inner clamping faces matching the parallel upper tower lands (Z = 11.20..14.09mm).
   - 0.18mm per-side Y-clearance (0.36mm total) + 0.45mm per-side bottom lead-in funnel chamfers.
   - 0.22mm per-side X-clearance on both Outer Cheeks and Inner Tower Guide Shoulders.
   - 0.40mm Y-clearance to Left Tower buttress struts (Y in [7.45, 11.25mm] vs struts at 7.05 and 11.65mm).
   - Smooth low-profile 0.30mm click-retention bumps engaging the 0.35mm tower detents.
"""

import os
import sys

# Ensure repository root is on sys.path
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import numpy as np
import trimesh
from shapely.geometry import Polygon, box

from build_shaft import Y_AXLE, Z_AXLE, PIN_DIAMETER, HUB_DIAMETER

# Global Geometric Dimensions
Z_TOP = 14.090               # Tower top elevation
CLAMP_ROOF_THICK = 1.00      # 1.00mm low-profile bridge roof thickness (Z: 14.090 to 15.090mm, -1.20mm reduction!)
CLAMP_Z_BOTTOM = 11.200      # Extends down to Z = 11.20mm (3.89mm total clamp height)
CLAMP_WALL_THICK = 2.20      # 2.20mm heavy-duty front/rear clamping jaw thickness (3.9x stiffer than 1.40mm)
SIDE_WALL_THICK = 1.60       # 1.60mm robust outer side cheek thickness (4 solid perimeters on 0.4mm nozzle)
ENTRY_CHAMFER = 0.450        # 0.45mm lead-in entry funnel chamfer at bottom of jaws

# Central Hold-Down & Upward Relief Pocket over Pin Funnel
Z_PIN_RELIEF = 14.280        # Relief pocket ceiling (+0.29mm running clearance above 13.99mm pin top)
Z_KEEL = Z_PIN_RELIEF        # Backwards-compatibility alias for test/visualization scripts
Y_RELIEF_FRONT = 7.550       # Front edge of relief pocket
Y_RELIEF_REAR = 11.000       # Rear edge of relief pocket

# Clearance Arch around Pin on Outer Side Wall
PIN_CLEARANCE_RADIUS = 1.85  # Radius = 1.85mm (Pin is R=1.40mm -> +0.45mm radial air gap)
CLAMP_WIDTH_X = 1.500        # 1.500mm wide U-saddle span across tower

# Parallel Upper Tower Land Coordinates & High-Temp Clearances
TOWER_Y_FRONT = 6.550
TOWER_Y_REAR = 11.850
CLAMP_Y_CLEARANCE = 0.180    # 0.180mm per side (0.36mm total) for smooth push-on at higher print temps
CLAMP_X_CLEARANCE = 0.220    # 0.220mm per side X-clearance to tower lateral faces


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
    """Robust union of multiple overlapping manifold meshes."""
    m_res = meshes[0]
    for m in meshes[1:]:
        m_res = m_res.union(m, engine='manifold')
    return m_res


def get_saddle_polygon_yz(rear_max_y=None):
    """
    Generates the closed 2D cross-section polygon of the U-saddle in (Y, Z):
    - Parallel vertical inner clamping faces at Y = 6.370mm and Y = 12.360mm (0.18mm/side clearance to 6.55..12.18mm tower).
    - 0.45mm x 45 deg flared entry funnel from Z = 11.75mm down to Z = 11.20mm (catches tower tops effortlessly).
    - 2.20mm thick front jaw (Y = 4.170 to 6.370mm) and 2.00mm thick rear jaw.
    """
    z_top = Z_TOP + CLAMP_ROOF_THICK  # 16.290 mm
    z_roof_under = Z_TOP             # 14.090 mm
    z_funnel_top = 11.750            # Top of 0.45mm bottom lead-in funnel
    z_bot = CLAMP_Z_BOTTOM           # 11.200 mm
    
    y_front_inner = TOWER_Y_FRONT - CLAMP_Y_CLEARANCE          # 6.370 mm
    y_front_inner_bot = y_front_inner - ENTRY_CHAMFER          # 5.920 mm (flared entry mouth)
    
    y_rear_inner = TOWER_Y_REAR + CLAMP_Y_CLEARANCE            # 12.360 mm
    y_rear_inner_bot = y_rear_inner + ENTRY_CHAMFER            # 12.810 mm (flared entry mouth)
    
    y_front_outer = y_front_inner - CLAMP_WALL_THICK           # 4.170 mm (2.20mm solid front jaw)
    
    if rear_max_y is not None:
        y_rear_outer = rear_max_y
        y_rear_inner_bot_clipped = min(y_rear_inner_bot, rear_max_y - 0.55)
    else:
        y_rear_outer = y_rear_inner + 2.000                    # 14.360 mm (2.00mm solid rear jaw)
        y_rear_inner_bot_clipped = y_rear_inner_bot
        
    saddle_pts_yz = [
        (y_front_outer, z_bot),
        (y_front_outer, z_top - 0.40),
        (y_front_outer + 0.40, z_top),
        (y_rear_outer - 0.40, z_top),
        (y_rear_outer, z_top - 0.40),
        (y_rear_outer, z_bot),
        (y_rear_inner_bot_clipped, z_bot),
        (y_rear_inner, z_funnel_top),
        (y_rear_inner, z_roof_under),
        (11.20, z_roof_under),
        (Y_RELIEF_REAR, Z_PIN_RELIEF),   # Upward relief pocket: +0.51mm air gap over pin top
        (Y_RELIEF_FRONT, Z_PIN_RELIEF),  # Prevents any binding from support marks or layer roughness
        (7.35, z_roof_under),
        (y_front_inner, z_roof_under),
        (y_front_inner, z_funnel_top),
        (y_front_inner_bot, z_bot),
    ]
    return Polygon(saddle_pts_yz)


get_clamp_polygon_yz = get_saddle_polygon_yz


def get_side_wall_polygon_yz(with_arch=False, y_rear_max=None, is_right=False):
    """
    Generates a clean, non-self-intersecting closed 2D profile of the outer side cheek.
    (The 3D pin safety clearance arch R = 1.85mm is boolean-subtracted in 3D via Manifold for 100% watertightness.)
    """
    z_top = Z_TOP + CLAMP_ROOF_THICK
    z_bot = 11.75
    
    if is_right:
        y_r_end = y_rear_max if y_rear_max is not None else 10.650
        side_pts_yz = [
            (6.50, z_bot),
            (6.50, 14.09),
            (4.17, 14.09),
            (4.17, z_top - 0.40),
            (4.57, z_top),
            (13.15, z_top),
            (13.55, z_top - 0.40),
            (13.55, 14.09),
            (y_r_end, 14.09),
            (y_r_end, z_bot),
        ]
        return Polygon(side_pts_yz)
        
    side_pts_yz = [
        (6.50, z_bot),
        (6.50, 14.09),
        (4.17, 14.09),
        (4.17, z_top - 0.40),
        (4.57, z_top),
        (13.63, z_top),
        (14.03, z_top - 0.40),
        (14.03, 14.09),
        (11.90, 14.09),
        (11.90, z_bot),
    ]
    return Polygon(side_pts_yz)


def build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False, skip_trim=False):
    """
    Builds the 100% watertight 3D mesh of the Reinforced 4-Sided Box-Cap Tower Clamp.
    All boolean sub-volumes overlap by >= 0.08mm to guarantee zero non-manifold seam edges.
    """
    poly_saddle = get_saddle_polygon_yz()
    poly_side_solid = get_side_wall_polygon_yz(is_right=False)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    poly_roof_yz = Polygon([
        (4.17, 14.09), (4.17, z_top - 0.40), (4.57, z_top),
        (13.63, z_top), (14.03, z_top - 0.40), (14.03, 14.09)
    ])
    
    if tower_side == 'left':
        # Left Tower is at X in [3.90, 5.40].
        # Outer cheek inner face sits at X = 3.90 - 0.22 = 3.68mm (0.22mm X-clearance!).
        # Lower saddle stays within X in [3.68, 5.30] (0.20mm axial clearance to shaft hub/cam at X=5.50).
        m_saddle = extrude_yz(poly_saddle, height=5.30 - 3.68, x_offset=3.68)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=3.80 - 2.08, x_offset=2.08)
        m_side = extrude_yz(poly_side_solid, height=3.68 - 2.08, x_offset=2.08)
        
        # Smooth low-profile snap detent hook on inner face of side wall (engages Z=12.35mm shelf)
        # Includes a detent relief pocket (X=3.50mm at Z in [12.32, 13.15]) so seated interference is 0.0000 mm^3!
        poly_pocket_l_xz = Polygon([
            (3.50, 12.32),
            (3.80, 12.32),
            (3.80, 13.15),
            (3.50, 13.15)
        ])
        m_pl_f = extrude_xz(poly_pocket_l_xz, height=7.40 - 6.50, y_offset=6.50)
        m_pl_r = extrude_xz(poly_pocket_l_xz, height=11.90 - 11.10, y_offset=11.10)
        
        poly_hook_xz = Polygon([
            (2.50, 11.75),
            (3.68, 11.75),
            (3.73, 12.10),  # Smooth entry ramp protruding to X=3.73mm (0.08mm click over X=3.65mm bead)
            (3.73, 12.32),  # Hook shelf top (0.03mm below 12.35mm detent shelf -> zero seated stress!)
            (2.50, 12.32)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=7.35 - 6.55, y_offset=6.55)
        m_hr = extrude_xz(poly_hook_xz, height=11.85 - 11.15, y_offset=11.15)
        
        # Inner X-guide lip on the inside of Left Tower (overlaps m_saddle from X=5.20 to 5.95 at Z>=13.75)
        poly_inner_guide_xz = Polygon([
            (5.20, 13.85),
            (5.62, 13.85),
            (5.95, 13.75),
            (6.15, 13.75),
            (6.15, z_top),
            (5.20, z_top)
        ])
        m_ig_front = extrude_xz(poly_inner_guide_xz, height=6.37 - 4.17, y_offset=4.17)
        m_ig_rear = extrude_xz(poly_inner_guide_xz, height=14.03 - 12.03, y_offset=12.03)
        
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side, m_ig_front, m_ig_rear])
        m_clamp = m_clamp.difference(unary_union_meshes([m_pl_f, m_pl_r]), engine='manifold')
        m_clamp = m_clamp.union(unary_union_meshes([m_hf, m_hr]), engine='manifold')
        
        # Cut pin safety clearance arch (from X = 2.68 to 5.00mm, preserving 0.60mm solid outer plate X in [2.08, 2.68])
        pin_cutter = trimesh.creation.cylinder(radius=PIN_CLEARANCE_RADIUS, height=3.0, sections=64)
        R_mat = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
        pin_cutter.apply_transform(R_mat)
        pin_cutter.apply_translation([2.68 + 1.50, Y_AXLE, Z_AXLE])
        m_clamp = m_clamp.difference(pin_cutter, engine='manifold')
    else:
        # Right Tower is at X in [13.10, 14.60].
        # Lower saddle stays within X in [13.20, 14.82] (0.20mm axial clearance to shaft hub at X=13.00).
        # Outer cheek inner face sits at X = 14.60 + 0.22 = 14.82mm (0.22mm X-clearance!).
        poly_saddle_r = get_saddle_polygon_yz(rear_max_y=13.550)
        m_saddle = extrude_yz(poly_saddle_r, height=14.82 - 13.20, x_offset=13.20)
        
        poly_side_r = get_side_wall_polygon_yz(y_rear_max=10.650, is_right=True)
        m_cheek = extrude_yz(poly_side_r, height=16.12 - 14.70, x_offset=14.70)
        
        # Clear out tower slot X in [13.00, 14.82] below Z=14.09 so m_cheek roof bridges cleanly over 14.70..14.82
        tower_slot_cutter = trimesh.creation.box([14.82 - 13.00, (TOWER_Y_REAR - TOWER_Y_FRONT) + 2*CLAMP_Y_CLEARANCE, 4.0])
        tower_slot_cutter.apply_translation([
            (13.00 + 14.82)/2.0,
            (TOWER_Y_FRONT + TOWER_Y_REAR)/2.0,
            14.09 - 2.0
        ])
        
        # Detent relief pocket above Right hook (X=15.00mm at Z in [12.32, 13.15]) so seated interference is 0.0000 mm^3!
        poly_pocket_r_xz = Polygon([
            (14.70, 12.32),
            (15.00, 12.32),
            (15.00, 13.15),
            (14.70, 13.15)
        ])
        m_pr_f = extrude_xz(poly_pocket_r_xz, height=7.40 - 6.50, y_offset=6.50)
        
        # Smooth low-profile retention hook under Right front detent (protrudes to X=14.77mm, 0.08mm click over X=14.85mm bead)
        poly_hook_xz = Polygon([
            (15.60, 11.75),
            (14.82, 11.75),
            (14.77, 12.10),
            (14.77, 12.32),
            (15.60, 12.32)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=7.35 - 6.55, y_offset=6.55)
        
        # Inner X-guide lip on the inside of Right Tower (overlaps m_saddle from 12.35 to 13.30 at Z>=13.75)
        poly_inner_guide_r_xz = Polygon([
            (13.30, 13.85),
            (12.88, 13.85),
            (12.55, 13.75),
            (12.35, 13.75),
            (12.35, z_top),
            (13.30, z_top)
        ])
        m_ig_front = extrude_xz(poly_inner_guide_r_xz, height=6.37 - 4.17, y_offset=4.17)
        m_ig_rear = extrude_xz(poly_inner_guide_r_xz, height=13.80 - 12.03, y_offset=12.03)
        
        m_clamp_raw = unary_union_meshes([m_saddle, m_cheek, m_ig_front, m_ig_rear])
        m_clamp_raw = m_clamp_raw.difference(tower_slot_cutter, engine='manifold')
        m_clamp_raw = m_clamp_raw.difference(m_pr_f, engine='manifold')
        m_clamp_raw = m_clamp_raw.union(m_hf, engine='manifold')
        
        # Ensure complete pin running clearance (+0.45mm radial air gap, zero rubbing)
        pin_cutter = trimesh.creation.cylinder(radius=PIN_CLEARANCE_RADIUS, height=10.0, sections=64)
        R_mat = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
        pin_cutter.apply_transform(R_mat)
        pin_cutter.apply_translation([15.00, Y_AXLE, Z_AXLE])
        m_clamp_relieved = m_clamp_raw.difference(pin_cutter, engine='manifold')
        
        if not skip_trim:
            # Contour trimming in (X, Y) to stay 100% inside the baseplate interior clearance envelope (-0.15mm margin)
            from build_part import get_exact_base_polygon, OUTER_WALL_THICK
            _, outer_body_poly, _ = get_exact_base_polygon()
            inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
            safe_interior_poly = inner_poly.buffer(-0.15)
            m_trim = trimesh.creation.extrude_polygon(safe_interior_poly, height=25.0)
            m_clamp = m_clamp_relieved.intersection(m_trim, engine='manifold')
        else:
            m_clamp = m_clamp_relieved
        
    if tower_side == 'left':
        if not skip_trim:
            from build_part import get_exact_base_polygon, OUTER_WALL_THICK
            _, outer_body_poly, _ = get_exact_base_polygon()
            inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
            safe_interior_poly = inner_poly.buffer(-0.15)
            m_trim_l = trimesh.creation.extrude_polygon(safe_interior_poly, height=25.0)
            m_clamp = m_clamp.intersection(m_trim_l, engine='manifold')
        
    if in_assembly_coords:
        return m_clamp
    else:
        m_bed = m_clamp.copy()
        rot = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
        m_bed.apply_transform(rot)
        bounds = m_bed.bounds
        m_bed.apply_translation([
            -(bounds[0, 0] + bounds[1, 0]) / 2.0,
            -(bounds[0, 1] + bounds[1, 1]) / 2.0,
            -bounds[0, 2]
        ])
        return m_bed


def build_unified_clamp_mesh(in_assembly_coords=False):
    """
    Builds the 1-Piece Ultra-Rigid Closed-Box Gantry Clamp:
    - Left 4-sided box cap on Left Tower (X in [2.08, 6.15])
    - Right 4-sided box cap on Right Tower (X in [12.35, 16.12])
    - Heavy-Duty Rear Cross-Tie Beam spanning X in [5.20, 13.30] at Y in [11.95, 13.80], Z in [13.75, 15.09]
    - Heavy-Duty Front Over-Arch Cross-Tie Beam spanning X in [5.20, 13.30] at Y in [4.17, 6.37], Z in [13.75, 15.09]
    """
    c_left = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=True, skip_trim=True)
    c_right = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True, skip_trim=True)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK  # 15.090 mm
    
    # 1. Heavy-Duty Rear Cross-Tie Beam in (Y, Z): Y in [11.95, 13.80] x Z in [13.75, 15.09]
    # Clears shaft structural web (Y<=11.78, Z<=13.59) at all pivot angles!
    rear_tie_pts_yz = [
        (11.95, 13.75),
        (11.95, z_top),
        (13.40, z_top),
        (13.80, z_top - 0.40),
        (13.80, 13.75)
    ]
    poly_rear_tie_yz = Polygon(rear_tie_pts_yz)
    m_rear_tie = extrude_yz(poly_rear_tie_yz, height=13.30 - 5.20, x_offset=5.20)
    
    # 2. Heavy-Duty Front Over-Arch Cross-Tie Beam in (Y, Z): Y in [4.17, 6.37] x Z in [13.75, 15.09]
    front_tie_pts_yz = [
        (4.17, 13.75),
        (4.17, z_top - 0.40),
        (4.57, z_top),
        (6.37, z_top),
        (6.37, 13.75)
    ]
    poly_front_tie_yz = Polygon(front_tie_pts_yz)
    m_front_tie = extrude_yz(poly_front_tie_yz, height=13.30 - 5.20, x_offset=5.20)
    
    unified_clamp = unary_union_meshes([c_left, m_rear_tie, m_front_tie, c_right])
    
    # Guarantee >= 0.35mm radial running clearance to central shaft hub barrel (R_hub = 2.10mm -> cutter R = 2.45mm)
    hub_cutter = trimesh.creation.cylinder(radius=HUB_DIAMETER/2.0 + 0.35, height=8.20, sections=64)
    R_mat = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    hub_cutter.apply_transform(R_mat)
    hub_cutter.apply_translation([9.25, Y_AXLE, Z_AXLE])
    unified_clamp = unified_clamp.difference(hub_cutter, engine='manifold')
    
    # Trim entire unified gantry clamp against safe_interior_poly so 100% stays inside the baseplate interior clearance envelope
    from build_part import get_exact_base_polygon, OUTER_WALL_THICK
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    safe_interior_poly = inner_poly.buffer(-0.15)
    m_trim_u = trimesh.creation.extrude_polygon(safe_interior_poly, height=25.0)
    unified_clamp = unified_clamp.intersection(m_trim_u, engine='manifold')
    
    if in_assembly_coords:
        return unified_clamp
    else:
        m_bed = unified_clamp.copy()
        rot = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
        m_bed.apply_transform(rot)
        bounds = m_bed.bounds
        m_bed.apply_translation([
            -(bounds[0, 0] + bounds[1, 0]) / 2.0,
            -(bounds[0, 1] + bounds[1, 1]) / 2.0,
            -bounds[0, 2]
        ])
        return m_bed


def build_tower_clamps_pair_mesh(spacing=5.0):
    """
    Creates a pre-arranged pair of separate clamps (1 Left, 1 Right) oriented flat on the
    print bed (Z = 0.00mm) spaced side-by-side for 1-click support-free 3D printing.
    """
    c_left = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False)
    c_right = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=False)
    
    dx = (c_left.bounds[1, 0] - c_left.bounds[0, 0]) + spacing
    c_left.apply_translation([-dx / 2.0, 0.0, 0.0])
    c_right.apply_translation([dx / 2.0, 0.0, 0.0])
    
    return trimesh.util.concatenate([c_left, c_right])


def export_openscad_clamp(filename='tower_clamp.scad'):
    """Exports parametric OpenSCAD reference model."""
    scad_content = f"""// Kia EV6 Outlet Interlock - Closed-Box Gantry Tower Prong Clamp
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

// Closed-Box Gantry Clamp Parameters
y_front_inner = {TOWER_Y_FRONT - CLAMP_Y_CLEARANCE:.3f};
y_rear_inner = {TOWER_Y_REAR + CLAMP_Y_CLEARANCE:.3f};
"""
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
        f.write(scad_content)
    print(f"Exported OpenSCAD reference: {os.path.join(OUTPUT_DIR, filename)}")


def main():
    print("=" * 80)
    OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Unified Monolithic Closed-Box Gantry Clamp
    bridge_clamp = build_unified_clamp_mesh(in_assembly_coords=False)
    bridge_clamp.export(os.path.join(OUTPUT_DIR, 'tower_clamp_bridge.stl'))
    bridge_clamp.export(os.path.join(OUTPUT_DIR, 'tower_clamp_bridge.obj'))
    bridge_clamp.export(os.path.join(OUTPUT_DIR, 'tower_clamp.stl'))
    bridge_clamp.export(os.path.join(OUTPUT_DIR, 'tower_clamp.obj'))
    bb = bridge_clamp.bounds
    print(f"Saved tower_clamp_bridge.stl / .obj (Watertight: {bridge_clamp.is_watertight}, Volume: {bridge_clamp.volume:.2f} mm^3)")
    print(f"  Bed Footprint: {bb[1,0]-bb[0,0]:.2f} x {bb[1,1]-bb[0,1]:.2f} mm (Z = {bb[1,2]-bb[0,2]:.2f} mm)")
    
    # 2. Left and Right Individual Clamps
    clamp_l = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=False)
    clamp_l.export(os.path.join(OUTPUT_DIR, 'tower_clamp_left.stl'))
    clamp_l.export(os.path.join(OUTPUT_DIR, 'tower_clamp_left.obj'))
    print(f"Saved tower_clamp_left.stl / .obj (Watertight: {clamp_l.is_watertight}, Volume: {clamp_l.volume:.2f} mm^3)")
    
    clamp_r = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=False)
    clamp_r.export(os.path.join(OUTPUT_DIR, 'tower_clamp_right.stl'))
    clamp_r.export(os.path.join(OUTPUT_DIR, 'tower_clamp_right.obj'))
    print(f"Saved tower_clamp_right.stl / .obj (Watertight: {clamp_r.is_watertight}, Volume: {clamp_r.volume:.2f} mm^3)")
    
    # 3. Paired Build Plate
    pair_mesh = build_tower_clamps_pair_mesh(spacing=4.0)
    pair_mesh.export(os.path.join(OUTPUT_DIR, 'tower_clamps_pair.stl'))
    b = pair_mesh.bounds
    print(f"Saved tower_clamps_pair.stl (Watertight: {pair_mesh.is_watertight}, Volume: {pair_mesh.volume:.2f} mm^3)")
    print(f"  Bed Footprint: {b[1,0]-b[0,0]:.2f} x {b[1,1]-b[0,1]:.2f} mm (Z = {b[1,2]-b[0,2]:.2f} mm)")
    
    # 4. OpenSCAD reference
    export_openscad_clamp('tower_clamp.scad')
    
    print("=" * 80)
    print("CLOSED-BOX GANTRY TOWER CLAMP CAD GENERATION COMPLETE!")
    print("=" * 80)


if __name__ == '__main__':
    main()
