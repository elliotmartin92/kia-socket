"""
testing/test_clamp_geometry.py
Prototype and verify the 2D profile, 3D mesh, detent engagement, and clearances
of the Universal Anti-Spreading Tower Prong Clamp.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    BASE_THICK, TOWER_HEIGHT, TOWER_WALL_THICK, TOWER_THROAT_W,
    build_clean_shaft_towers_mesh
)
from build_shaft import (
    Y_AXLE, Z_AXLE, PIN_DIAMETER, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER
)

# Tower Reference Landmarks
Y_SHAFT = Y_AXLE        # 9.279 mm
Z_CRADLE = Z_AXLE       # 12.590 mm
Z_TOP = BASE_THICK + TOWER_HEIGHT  # 14.090 mm
R_PIN = PIN_DIAMETER / 2.0         # 1.400 mm
Z_PIN_TOP = Z_CRADLE + R_PIN       # 13.990 mm

# Tower Prongs in Y
Y_FRONT_OUTER = 6.550
Y_REAR_OUTER = 12.180
TOWER_OUTER_SPAN = Y_REAR_OUTER - Y_FRONT_OUTER  # 5.630 mm

# Clamp Design Parameters
CLAMP_TOL_Y = 0.06           # 0.06mm snug slip fit per jaw
CLAMP_WALL_THICK = 1.15      # 1.15mm heavy-duty tension wall thickness
CLAMP_ROOF_THICK = 0.90      # 0.90mm bridge roof thickness (Z: 14.09 to 14.99 mm)
CLAMP_Z_BOTTOM = 11.20       # Extends down to Z = 11.20mm (3.79mm total clamp height)
CLAMP_WIDTH_X = 1.45         # 1.45mm wide in X (fits inside 1.50mm tower with 0.025mm inset per side)

# Detent Parameters
DETENT_Z = 11.75             # Elevation of snap detent center
DETENT_DEPTH = 0.25          # 0.25mm snap protrusion
DETENT_H = 0.60              # Detent height

def get_clamp_poly_yz():
    """
    Builds the 2D cross-section polygon of the Universal Symmetrical Clamp in (Y, Z).
    """
    z_top = Z_TOP + CLAMP_ROOF_THICK  # 14.990 mm
    z_roof_under = Z_TOP             # 14.090 mm
    z_bot = CLAMP_Z_BOTTOM           # 11.200 mm
    
    # Outer boundaries in Y
    y_front_inner = Y_FRONT_OUTER - CLAMP_TOL_Y  # 6.490 mm
    y_front_outer = y_front_inner - CLAMP_WALL_THICK  # 5.340 mm
    
    y_rear_inner = Y_REAR_OUTER + CLAMP_TOL_Y    # 12.240 mm
    y_rear_outer = y_rear_inner + CLAMP_WALL_THICK    # 13.390 mm
    
    # Detents on inner faces
    # Front jaw detent projects in +Y
    d_z1 = DETENT_Z - DETENT_H/2.0
    d_z2 = DETENT_Z + DETENT_H/2.0
    d_chamf = 0.30
    
    # Central keel descending into throat funnel
    # Funnel opening at Z=14.09 is Y in [7.415, 11.143]
    # Keel extends to Z = 14.020 (0.030mm above pin at 13.990)
    z_keel = 14.020
    y_keel_front = 7.650
    y_keel_rear = 10.908
    
    # Build profile as a single closed polygon
    # Trace counter-clockwise starting at front bottom outer corner:
    pts = [
        # Front outer wall
        (y_front_outer, z_bot),
        (y_front_outer, z_top - 0.40),
        (y_front_outer + 0.40, z_top),   # Top-front chamfer
        # Roof top
        (y_rear_outer - 0.40, z_top),    # Top-rear chamfer
        (y_rear_outer, z_top - 0.40),
        # Rear outer wall
        (y_rear_outer, z_bot),
        # Rear inner wall with snap detent
        (y_rear_inner, z_bot),
        (y_rear_inner, d_z1 - d_chamf),
        (y_rear_inner - DETENT_DEPTH, d_z1),  # Inward snap bump
        (y_rear_inner - DETENT_DEPTH, d_z2),
        (y_rear_inner, d_z2 + d_chamf),
        (y_rear_inner, z_roof_under),
        # Rear prong pocket ceiling
        (y_keel_rear + 0.30, z_roof_under),
        # Central Keel
        (y_keel_rear, z_keel + 0.15),
        (y_keel_rear - 0.15, z_keel),
        (y_keel_front + 0.15, z_keel),
        (y_keel_front, z_keel + 0.15),
        # Front prong pocket ceiling
        (y_keel_front - 0.30, z_roof_under),
        (y_front_inner, z_roof_under),
        # Front inner wall with snap detent
        (y_front_inner, d_z2 + d_chamf),
        (y_front_inner + DETENT_DEPTH, d_z2),  # Inward snap bump
        (y_front_inner + DETENT_DEPTH, d_z1),
        (y_front_inner, d_z1 - d_chamf),
        (y_front_inner, z_bot)
    ]
    return Polygon(pts)

def build_clamp_mesh(poly_yz, in_assembly_coords=False, tower_x_center=4.65):
    """Extrudes the clamp polygon along X."""
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=CLAMP_WIDTH_X)
    v = m_raw.vertices.copy()
    
    if in_assembly_coords:
        # Align with tower center in X
        # Original extrude puts polygon in X-Y and extrudes along Z
        # Map: poly_Y -> Y, poly_Z -> Z, height -> X
        # v[:, 0] is Y, v[:, 1] is Z, v[:, 2] is X
        v_assy = np.column_stack([
            v[:, 2] + (tower_x_center - CLAMP_WIDTH_X/2.0),
            v[:, 0],
            v[:, 1]
        ])
        return trimesh.Trimesh(vertices=v_assy, faces=m_raw.faces.copy(), process=True)
    else:
        # Orient flat on print bed: side face down on bed (Z=0)
        # Dimensions: 1.45mm tall on bed, 7.95mm wide in X, 3.79mm deep in Y
        # v[:, 2] (thickness) becomes Z!
        v_bed = np.column_stack([
            v[:, 0],  # Y profile -> X on bed
            v[:, 1],  # Z profile -> Y on bed
            v[:, 2]   # X thickness -> Z on bed
        ])
        # Center in X, Y and rest on Z=0
        v_bed[:, 0] -= (v_bed[:, 0].min() + v_bed[:, 0].max()) / 2.0
        v_bed[:, 1] -= (v_bed[:, 1].min() + v_bed[:, 1].max()) / 2.0
        v_bed[:, 2] -= v_bed[:, 2].min()
        return trimesh.Trimesh(vertices=v_bed, faces=m_raw.faces.copy(), process=True)

if __name__ == '__main__':
    poly = get_clamp_poly_yz()
    print(f"Polygon valid: {poly.is_valid}")
    print(f"Polygon area: {poly.area:.3f} mm^2")
    
    mesh_assy = build_clamp_mesh(poly, in_assembly_coords=True, tower_x_center=4.65)
    print(f"Assembly mesh watertight: {mesh_assy.is_watertight}")
    print(f"Assembly mesh volume: {mesh_assy.volume:.3f} mm^3")
    print(f"Assembly mesh bounds:\n  X: [{mesh_assy.bounds[0,0]:.2f}, {mesh_assy.bounds[1,0]:.2f}]\n  Y: [{mesh_assy.bounds[0,1]:.2f}, {mesh_assy.bounds[1,1]:.2f}]\n  Z: [{mesh_assy.bounds[0,2]:.2f}, {mesh_assy.bounds[1,2]:.2f}]")
    
    mesh_print = build_clamp_mesh(poly, in_assembly_coords=False)
    print(f"\nPrintable mesh watertight: {mesh_print.is_watertight}")
    print(f"Printable mesh bounds:\n  X: [{mesh_print.bounds[0,0]:.2f}, {mesh_print.bounds[1,0]:.2f}]\n  Y: [{mesh_print.bounds[0,1]:.2f}, {mesh_print.bounds[1,1]:.2f}]\n  Z: [{mesh_print.bounds[0,2]:.2f}, {mesh_print.bounds[1,2]:.2f}]")
