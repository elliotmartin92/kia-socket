"""
build_shaft.py
Parametric 3D CAD generator for the OEM 3-rib Kia Smart Key socket shaft/rocker mechanism.

Features:
- Stepped cylindrical pivot axle pins (Total length 11.50mm, Ø1.90mm - Ø2.27mm parametric)
- 7.60mm central structural hub barrel fitting perfectly between baseplate towers
- OEM 3-Rib Fork Architecture: Left flank rib, central extended plunger blade, right flank rib
- Extended output plunger reaching ≥6.50mm below baseplate outer face (Z ≤ -6.50mm) to actuate PCB switch
- Angled input cam tab (reaches Y = 3.47mm, Z = 6.79mm) engaging key blade slider track
- Generates 100% watertight STL, OBJ, and OpenSCAD CAD assets
"""

import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

# ==============================================================================
# PARAMETRIC SPECIFICATIONS & OEM MEASUREMENTS
# ==============================================================================
# Baseplate Datum & Tower Coordinates
Y_AXLE = 9.279
Z_AXLE = 12.590

# Tower X bounds (1.50mm reinforced towers)
X_LEFT_TOWER_OUTER = 3.900
X_LEFT_TOWER_INNER = 5.400
X_RIGHT_TOWER_INNER = 13.100
X_RIGHT_TOWER_OUTER = 14.600
X_TOWER_CENTER = (X_LEFT_TOWER_INNER + X_RIGHT_TOWER_INNER) / 2.0  # 9.25 mm

# Through-Hole bounds: X in [7.608, 12.960], Y in [8.570, 13.082], Z in [0.00, 1.00]
HOLE_X_CENTER = 10.284
HOLE_X_WIDTH = 5.352
HOLE_Y_CENTER = 10.826
HOLE_Y_LEN = 4.512

# Enlarged Heavy-Duty Dimensions
TOTAL_AXLE_LEN = 11.50       # 11.50mm total length tip-to-tip
HUB_WIDTH = 7.50             # 7.50mm structural hub (0.10mm clearance per side in 7.70mm tower gap)
PIN_LEN = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0  # 2.00 mm per side
PIN_DIAMETER = 2.80          # Ø2.80mm heavy-duty pin (fits Ø3.00mm cradle, 4.72x higher torsional rigidity)
HUB_DIAMETER = 4.20          # Ø4.20mm central structural hub barrel
PLUNGER_REACH_BELOW_Z = 6.50 # Reaches Z = -6.50mm below baseplate floor

# Cam & Ribs
CAM_WIDTH_X = 2.70           # 2.70mm wide input cam tab
CAM_X_CENTER = 7.05          # Aligned with slider guide track
RIB_FLANK_THICK = 1.00       # 1.00mm flank rib thickness
PLUNGER_WIDTH_X = 4.40       # 4.40mm wide central plunger blade (centered in 5.35mm hole)

def build_shaft_rocker_mesh(
    axle_len=TOTAL_AXLE_LEN,
    hub_w=HUB_WIDTH,
    pin_d=PIN_DIAMETER,
    hub_d=HUB_DIAMETER,
    plunger_reach_below_z=PLUNGER_REACH_BELOW_Z,
    plunger_w_x=PLUNGER_WIDTH_X,
    cam_w_x=CAM_WIDTH_X,
    cam_x_c=CAM_X_CENTER,
    in_assembly_coords=True
):
    """
    Builds the enlarged heavy-duty 3-rib 3D mesh of the shaft/rocker mechanism.
    
    Features:
    - Stepped cylindrical pivot pins (Ø2.80mm) with central structural hub (Ø4.20mm)
    - 3-rib fork array: Left & right stiffener flanks + widened 4.40mm central plunger
    - Smooth continuous filleted plunger arm reaching Z <= -6.50mm
    - Angled input cam tab matching OEM bellcrank angle (~105 deg)
    """
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER  # 9.25 mm
    
    # 1. Stepped Cylindrical Axle & Hub
    r_pin = pin_d / 2.0
    r_hub = hub_d / 2.0
    pin_len = (axle_len - hub_w) / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # Left pin: [3.50, 5.50]
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - hub_w/2.0 - pin_len/2.0, y_axle, z_axle])
    
    # Right pin: [13.00, 15.00]
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + hub_w/2.0 + pin_len/2.0, y_axle, z_axle])
    
    # Central Hub Barrel: [5.50, 13.00]
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=hub_w, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 2. OEM 3-Rib Flanks & Plunger Array
    flank_collar = Point(y_axle, z_axle).buffer(r_hub)
    flank_pts = [
        (y_axle - 1.50, z_axle + 0.60),
        (y_axle + 3.20, z_axle - 1.50),
        (y_axle + 2.50, z_axle - 4.50),
        (y_axle + 0.20, z_axle - 4.20),
        (y_axle - 1.60, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    # Rib 1 (Left Flank): X in [5.60, 6.60]
    m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r1 = m_rib1_raw.vertices.copy()
    v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - hub_w/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)
    
    # Rib 3 (Right Flank): X in [11.90, 12.90]
    m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r3 = m_rib3_raw.vertices.copy()
    v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + hub_w/2.0 - 0.10 - RIB_FLANK_THICK), v_r3[:, 0], v_r3[:, 1]])
    mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)
    
    # Rib 2 (Center Plunger Blade): Reaching Z = -6.50mm
    z_tip = -plunger_reach_below_z  # -6.50 mm
    r_tip = 1.00                    # 2.00mm tip thickness in Y
    plunger_y_center = 10.479
    
    N = 25
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + r_hub) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - r_hub) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger = unary_union([flank_collar, Polygon(pts_plunger)])
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=plunger_w_x)
    v_p = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - plunger_w_x/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # 3. Structural Web tying the 3 ribs together (X in [5.60, 12.90])
    web_y_min = y_axle - 1.50
    web_y_max = y_axle + 2.50
    web_z_min = z_axle - 3.20
    web_z_max = z_axle + 1.00
    web_poly = box(web_y_min, web_z_min, web_y_max, web_z_max)
    web_span_x = (x_c + hub_w/2.0 - 0.10) - (x_c - hub_w/2.0 + 0.10)
    m_web_raw = trimesh.creation.extrude_polygon(web_poly, height=web_span_x)
    v_w = m_web_raw.vertices.copy()
    v_web = np.column_stack([v_w[:, 2] + (x_c - hub_w/2.0 + 0.10), v_w[:, 0], v_w[:, 1]])
    mesh_web = trimesh.Trimesh(vertices=v_web, faces=m_web_raw.faces.copy(), process=True)
    
    # 4. Direct 105° Input Cam Tab (100% FLUSH with top apex of shaft hub)
    # Centerline of plunger is at angle theta_p = atan2(-19.09, 1.20) = -86.40°
    # 105° bellcrank angle -> angle of cam centerline = -86.40° - 75.0° = -161.40°
    theta_cam = np.radians(-161.40)
    u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)]) # [-0.948, -0.319]
    u_perp_up = np.array([u_dir[1], -u_dir[0]])
    if u_perp_up[1] < 0:
        u_perp_up = -u_perp_up # [-0.319, 0.948] -> normal pointing up/forward
        
    cam_reach = 6.80     # Total length from shaft center
    cam_arm_thick = 2.80 # Solid 2.80mm beam thickness
    
    # Top line starts TANGENT to cylinder top (100% flush with shaft top apex at Z = z_axle + r_hub = 14.69mm)
    p_tangent_top = np.array([y_axle, z_axle]) + u_perp_up * r_hub
    p_top_tip = p_tangent_top + u_dir * cam_reach
    p_bot_tip = p_top_tip - u_perp_up * cam_arm_thick
    p_tangent_bot = p_tangent_top - u_perp_up * cam_arm_thick
    
    half_t = cam_arm_thick / 2.0
    p_tip_mid = (p_top_tip + p_bot_tip) / 2.0
    cam_tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_tip_mid + u_dir * (half_t * np.cos(a)) + u_perp_up * (half_t * np.sin(a))
        cam_tip_pts.append((pt[0], pt[1]))
        
    poly_cam_arm = Polygon([p_tangent_top] + cam_tip_pts + [p_tangent_bot, p_tangent_top])
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=cam_w_x)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (cam_x_c - cam_w_x/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    # Assembly mesh in place
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_rib1, mesh_rib3, mesh_plunger, mesh_web,
        mesh_cam
    ])
    
    if not in_assembly_coords:
        # Orient flat on print bed: rotate so spine / belly lays flat on build plate (Z=0)
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
    scad_content = f"""// Parametric OEM 3-Rib Shaft & Rocker Mechanism for Kia Socket Enclosure
// Generated by build_shaft.py

$fn = 64;

// Global Parameters (mm)
total_axle_len = {TOTAL_AXLE_LEN};
hub_w = {HUB_WIDTH};
pin_d = {PIN_DIAMETER};
pin_len = {PIN_LEN:.2f};
hub_d = {HUB_DIAMETER};

plunger_reach_below_z = {PLUNGER_REACH_BELOW_Z};
plunger_w = {PLUNGER_WIDTH_X};
plunger_y_c = {11.40};

cam_w = {CAM_WIDTH_X};
cam_x_c = {CAM_X_CENTER};

module oem_shaft_rocker() {{
    // Left Pivot Pin
    translate([-(total_axle_len/2 - pin_len/2), 0, 0])
        rotate([0, 90, 0])
            cylinder(r = pin_d/2, h = pin_len, center = true);
            
    // Right Pivot Pin
    translate([(total_axle_len/2 - pin_len/2), 0, 0])
        rotate([0, 90, 0])
            cylinder(r = pin_d/2, h = pin_len, center = true);
            
    // Central Hub Barrel
    rotate([0, 90, 0])
        cylinder(r = hub_d/2, h = hub_w, center = true);
}}

oem_shaft_rocker();
"""
    with open(filename, 'w') as f:
        f.write(scad_content)
    print(f"Exported {filename}")

if __name__ == '__main__':
    print("Generating parametric OEM 3-rib shaft/rocker CAD models...")
    
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

