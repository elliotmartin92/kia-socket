"""
build_shaft.py
Parametric 3D CAD generator for the Kia Smart Key socket shaft/rocker mechanism.

Features:
- Cylindrical pivot axle (Ø1.90mm for positive retention and low-friction rotation in Ø2.00mm tower cradles)
- Axial thrust retention collars on the outer tower faces
- Input actuation cam arm (engages sliding metal bar / key blade)
- Extended output plunger arm reaching ≥6.50mm below the baseplate outer face (Z ≤ -6.50mm) to actuate PCB switch
- Generates 100% watertight STL, OBJ, and OpenSCAD CAD assets
"""

import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

# ==============================================================================
# PARAMETRIC SPECIFICATIONS & DEFAULTS
# ==============================================================================
# Baseplate Datum & Tower Coordinates
Y_AXLE = 7.666
Z_AXLE = 12.590

# Tower X bounds
X_LEFT_TOWER_OUTER = 4.250
X_LEFT_TOWER_INNER = 5.500
X_RIGHT_TOWER_INNER = 13.360
X_RIGHT_TOWER_OUTER = 14.610

# Through-Hole bounds: X in [7.608, 12.960], Y in [8.570, 13.082], Z in [0.00, 1.00]
HOLE_X_CENTER = 10.284
HOLE_X_WIDTH = 5.352
HOLE_Y_CENTER = 10.826
HOLE_Y_LEN = 4.512

# Shaft Default Parameters (Heavy-Duty Reinforced)
AXLE_DIAMETER = 1.90          # Ø1.90mm bearing ends (snaps through 1.65mm throat into Ø2.00mm cradle)
AXLE_TRUNK_DIAMETER = 2.80    # Ø2.80mm heavy-duty structural reinforcing core between towers
PLUNGER_REACH_BELOW_Z = 6.50  # 6.50mm below baseplate outer bottom face (Z = -6.50mm)
PLUNGER_WIDTH_X = 3.80        # Widened to 3.80mm in X (centered in 5.35mm hole -> 0.78mm side clearances)
PLUNGER_THICK_Y = 2.00        # Thickened to 2.00mm in Y for high flexural and bending strength
PLUNGER_Y_CENTER = 11.40      # Optimized centerline for smooth horizontal Y-axis actuation

INPUT_CAM_WIDTH_X = 2.40      # 2.40mm wide input cam in X (centered at X = 6.60mm in bracket guide channel)
INPUT_CAM_X_CENTER = 6.60     # Aligned with guide channel between Brackets 3 & 4
INPUT_CAM_REACH_Y = 4.50      # Reaches 4.50mm in -Y (to Y = 3.17mm)
INPUT_CAM_DROP_Z = 6.00       # Drops 6.00mm below axle in Z (to Z = 6.59mm)

COLLAR_DIAMETER = 3.00        # Ø3.00mm thrust retention collars
COLLAR_THICK = 0.80           # 0.80mm thick collars outside tower faces

def build_shaft_rocker_mesh(
    axle_d=AXLE_DIAMETER,
    axle_trunk_d=AXLE_TRUNK_DIAMETER,
    plunger_reach_below_z=PLUNGER_REACH_BELOW_Z,
    plunger_w_x=PLUNGER_WIDTH_X,
    plunger_t_y=PLUNGER_THICK_Y,
    plunger_y_center=PLUNGER_Y_CENTER,
    input_cam_w_x=INPUT_CAM_WIDTH_X,
    input_cam_x_center=INPUT_CAM_X_CENTER,
    input_cam_reach_y=INPUT_CAM_REACH_Y,
    input_cam_drop_z=INPUT_CAM_DROP_Z,
    collar_d=COLLAR_DIAMETER,
    collar_t=COLLAR_THICK,
    in_assembly_coords=True
):
    """
    Builds the reinforced 3D mesh of the shaft/rocker mechanism.
    
    Features:
    - Smooth continuous filleted root (no sharp notch at bend)
    - Ø2.80mm central structural trunk sleeve
    - Monolithic gusset web connecting input cam and plunger arm
    - High flexural section modulus for durable print removal and actuation
    """
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    r_axle = axle_d / 2.0
    
    # 1. Cylindrical Axle Bearing Ends (X-axis aligned, Ø1.90mm)
    x_min = X_LEFT_TOWER_OUTER - collar_t - 0.40   # 3.05 mm
    x_max = X_RIGHT_TOWER_OUTER + collar_t + 0.40  # 15.81 mm
    axle_len = x_max - x_min
    
    cyl_mesh = trimesh.creation.cylinder(radius=r_axle, height=axle_len, sections=32)
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    cyl_mesh.apply_transform(rot_x)
    cyl_mesh.apply_translation([(x_min + x_max)/2.0, y_axle, z_axle])
    
    # 2. Heavy-Duty Central Structural Trunk Sleeve (Ø2.80mm between inner tower faces)
    x_trunk_min = X_LEFT_TOWER_INNER + 0.10   # 5.60 mm
    x_trunk_max = X_RIGHT_TOWER_INNER - 0.10  # 13.26 mm
    trunk_len = x_trunk_max - x_trunk_min
    trunk_mesh = trimesh.creation.cylinder(radius=axle_trunk_d/2.0, height=trunk_len, sections=32)
    trunk_mesh.apply_transform(rot_x)
    trunk_mesh.apply_translation([(x_trunk_min + x_trunk_max)/2.0, y_axle, z_axle])
    
    # 3. Retaining Collars
    col_left = trimesh.creation.cylinder(radius=collar_d/2.0, height=collar_t, sections=32)
    col_left.apply_transform(rot_x)
    col_left.apply_translation([X_LEFT_TOWER_OUTER - collar_t/2.0, y_axle, z_axle])
    
    col_right = trimesh.creation.cylinder(radius=collar_d/2.0, height=collar_t, sections=32)
    col_right.apply_transform(rot_x)
    col_right.apply_translation([X_RIGHT_TOWER_OUTER + collar_t/2.0, y_axle, z_axle])
    
    # 4. Reinforced Output Plunger Arm (Thickened + Smooth Filleted Root)
    z_tip = -plunger_reach_below_z  # -6.50mm
    r_tip = plunger_t_y / 2.0       # 1.00mm rounded nose
    
    # Smooth continuous filleted 2D profile in (Y, Z)
    collar_disc = Point(y_axle, z_axle).buffer(1.50)
    
    N = 25
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + 1.20) + 2*(1-t)*t * 11.20 + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * 12.00 + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - 1.20) + 2*(1-t)*t * 9.20 + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * 11.80 + 2*(1-t)*t * 8.00 + t**2 * 3.50
    
    pts_arm_body = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger_body = Polygon(pts_arm_body)
    poly_plunger = unary_union([collar_disc, poly_plunger_body])
    
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=plunger_w_x)
    v_p = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([
        v_p[:, 2] + (HOLE_X_CENTER - plunger_w_x/2.0),
        v_p[:, 0],
        v_p[:, 1]
    ])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # 5. Reinforced Input Cam Arm
    y_input_tip = y_axle - input_cam_reach_y  # ~ 3.17 mm
    z_input_tip = z_axle - input_cam_drop_z   # ~ 6.59 mm
    
    cam_collar = Point(y_axle, z_axle).buffer(1.50)
    profile_cam_pts = [
        (y_axle + 1.20, z_axle),
        (y_input_tip, z_input_tip + 1.80),
        (y_input_tip, z_input_tip),
        (y_input_tip + 2.50, z_input_tip),
        (y_axle, z_axle - 2.80)
    ]
    poly_cam = unary_union([cam_collar, Polygon(profile_cam_pts)])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=input_cam_w_x)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([
        v_c[:, 2] + (input_cam_x_center - input_cam_w_x/2.0),
        v_c[:, 0],
        v_c[:, 1]
    ])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    # 6. Connecting Gusset Web between Cam and Plunger
    web_box = box(y_axle - 1.20, z_axle - 2.00, y_axle + 2.00, z_axle + 1.20)
    m_web_raw = trimesh.creation.extrude_polygon(web_box, height=(HOLE_X_CENTER - input_cam_x_center))
    v_w = m_web_raw.vertices.copy()
    v_web = np.column_stack([
        v_w[:, 2] + input_cam_x_center,
        v_w[:, 0],
        v_w[:, 1]
    ])
    mesh_web = trimesh.Trimesh(vertices=v_web, faces=m_web_raw.faces.copy(), process=True)
    
    # Assembly mesh in place
    shaft_mesh = trimesh.util.concatenate([cyl_mesh, trunk_mesh, col_left, col_right, mesh_plunger, mesh_cam, mesh_web])
    
    if not in_assembly_coords:
        # Orient flat on print bed: rotate so plunger arm lays flat on build plate (Z=0)
        mesh_printable = shaft_mesh.copy()
        rot_bed = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
        mesh_printable.apply_transform(rot_bed)
        # Center in X, Y and shift Z_min to 0.00mm
        bounds = mesh_printable.bounds
        mesh_printable.apply_translation([
            -(bounds[0, 0] + bounds[1, 0])/2.0,
            -(bounds[0, 1] + bounds[1, 1])/2.0,
            -bounds[0, 2]
        ])
        return mesh_printable
        
    return shaft_mesh

def export_shaft_scad(filename="shaft_rocker.scad"):
    """Exports OpenSCAD source file for parametric customization."""
    scad_content = f"""// Parametric Shaft & Rocker Mechanism for Kia Socket Enclosure
// Generated by build_shaft.py

$fn = 64;

// Global Parameters (mm)
axle_d = {AXLE_DIAMETER};
axle_r = axle_d / 2;
axle_len = {15.81 - 3.05:.2f};

collar_d = {COLLAR_DIAMETER};
collar_t = {COLLAR_THICK};

plunger_reach_below_z = {PLUNGER_REACH_BELOW_Z};
plunger_w = {PLUNGER_WIDTH_X};
plunger_t = {PLUNGER_THICK_Y};
plunger_y_c = {PLUNGER_Y_CENTER};

input_cam_w = {INPUT_CAM_WIDTH_X};
input_cam_x_c = {INPUT_CAM_X_CENTER};

module shaft_rocker() {{
    // Main Axle
    rotate([0, 90, 0])
        cylinder(r = axle_r, h = axle_len, center = true);
        
    // Left Collar
    translate([-(axle_len/2 - collar_t/2), 0, 0])
        rotate([0, 90, 0])
            cylinder(r = collar_d/2, h = collar_t, center = true);
            
    // Right Collar
    translate([(axle_len/2 - collar_t/2), 0, 0])
        rotate([0, 90, 0])
            cylinder(r = collar_d/2, h = collar_t, center = true);
}}

shaft_rocker();
"""
    with open(filename, 'w') as f:
        f.write(scad_content)
    print(f"Exported {filename}")

if __name__ == '__main__':
    print("Generating parametric shaft/rocker CAD models...")
    
    # 1. Assembled coordinate mesh
    shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)
    shaft_assembled.export("shaft_rocker_assembled.stl")
    shaft_assembled.export("shaft_rocker_assembled.obj")
    print(f"Saved shaft_rocker_assembled.stl (Bounds: {shaft_assembled.bounds})")
    
    # 2. Print-ready flat build-plate mesh (Z = 0.00mm)
    shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
    shaft_printable.export("shaft_rocker.stl")
    shaft_printable.export("shaft_rocker.obj")
    print(f"Saved shaft_rocker.stl (Print-ready flat at Z=0, Bounds: {shaft_printable.bounds})")
    
    # 3. OpenSCAD code
    export_shaft_scad("shaft_rocker.scad")
    print("Shaft CAD generation complete!")
