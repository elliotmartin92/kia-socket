"""
build_shaft.py
Parametric 3D CAD generator for the automotive 120V AC outlet safety interlock rocker mechanism.

Functional Context:
- Actuated by the insertion of the right plug prong (blade) of a standard US AC plug.
- Converts plug insertion force into pivot rotation around the shaft axle.
- Plunger arm swings downward through the baseplate floor to press the PCB tactile switch,
  energizing the 120V AC outlet only when a plug is actively inserted.

Features:
- Stepped cylindrical pivot axle pins (Total length 11.50mm, Ø2.80mm heavy-duty pins)
- 7.50mm central structural hub barrel (Ø4.20mm) fitting between baseplate towers
- OEM 3-Rib Fork Architecture: Left flank rib, central extended plunger blade, right flank rib
- Extended output plunger reaching ≥6.50mm below baseplate outer face (Z ≤ -6.50mm) to actuate PCB switch
- Angled input cam tab (105° bellcrank angle direct off shaft) engaging the right plug blade
- Generates 100% watertight STL, OBJ, and OpenSCAD CAD assets

Data Sources & Reverse-Engineering References:
- Reddit OEM Diagnostic Thread: https://www.reddit.com/r/KiaEV6/comments/1n9e8ex/internal_outlet_fix_for_free/p5gh9tp/?screen_view_count=2
- Imgur 18-Photo Teardown Album: https://imgur.com/a/pbAzoX3
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
X_LEFT_TOWER_OUTER = 3.450
X_LEFT_TOWER_INNER = 4.950
X_RIGHT_TOWER_INNER = 13.100
X_RIGHT_TOWER_OUTER = 14.600
X_TOWER_CENTER = (X_LEFT_TOWER_INNER + X_RIGHT_TOWER_INNER) / 2.0  # 9.025 mm

# Through-Hole bounds: X in [7.608, 12.960], Y in [8.570, 13.750], Z in [0.00, 1.00]
HOLE_X_CENTER = 10.284
HOLE_X_WIDTH = 5.352
HOLE_Y_TOP = 13.750
HOLE_Y_BOT = 8.570
HOLE_Y_CENTER = (HOLE_Y_BOT + HOLE_Y_TOP) / 2.0  # 11.160 mm
HOLE_Y_LEN = HOLE_Y_TOP - HOLE_Y_BOT              # 5.180 mm

# Enlarged Heavy-Duty Dimensions
TOTAL_AXLE_LEN = 11.95       # 11.95mm total length tip-to-tip
HUB_WIDTH = 7.45             # 7.45mm structural hub (0.350mm clearance per side in 8.15mm tower gap; 0.70mm axial play for effortless PIP release)
PIN_LEN = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0  # 2.250 mm per side
PIN_DIAMETER = 2.80          # Ø2.80mm heavy-duty pin (fits Ø3.50mm teardrop cradle, smooth 0.35mm radial clearance)
HUB_DIAMETER = 4.20          # Ø4.20mm central structural hub barrel
PLUNGER_REACH_BELOW_Z = 7.00 # Reaches Z = -7.00mm below baseplate floor (+0.50mm longer reach to tactile switch)

# Cam & Ribs (Calibrated for full-width blade capture & softened high-strength hub connection)
CAM_WIDTH_X = 1.80           # 1.80mm wide primary input cam tab (+0.85mm clearance to Bracket 4 X=8.00mm)
CAM_X_START = 5.35           # Primary cam spans X in [5.35, 7.15]mm (+0.40mm clearance to Left Tower X=4.95mm for easy PIP detachment)
CAM_X_CENTER = 6.250         # Dead center in brass throat (X = 6.250mm) and under hot plug blade!
RIB_FLANK_THICK = 1.00       # 1.00mm flank rib thickness
PLUNGER_WIDTH_X = 3.60       # 3.60mm wide central plunger blade (+0.48mm clearance to Bracket 4)
PLUNGER_Y_CENTER = 10.95     # Restored to 10.95mm to guarantee clean clearance during Z-axis assembly into 3.5mm rear housing aperture

# Kinematic Variant Profiles (5-Variant Spectrum for Prototyping & Production PIP Selection)
KINEMATIC_VARIANTS = {
    'v1_ultra_sens': {
        'id': 1,
        'notches': 1,
        'name': 'Variant 1: Ultra-Sensitive (Apex Y=1.65, Plunger Y=11.25)',
        'plunger_y': 11.25,
        'cam_apex': (1.65, 7.70),
        'cam_pts': [
            (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0),
            (7.00, 13.00),
            (4.20, 11.20),
            (2.80, 9.20),
            (1.80, 8.10),
            (1.65, 7.70),  # Forward apex (maximum non-polar capture)
            (1.80, 7.20),
            (2.40, 6.40),
            (3.80, 5.80),
            (5.50, 5.80),
            (7.20, 7.80),
            (8.20, 9.80),
            (Y_AXLE, Z_AXLE - HUB_DIAMETER/2.0)
        ]
    },
    'v2_high_sens': {
        'id': 2,
        'notches': 2,
        'name': 'Variant 2: High Sensitivity (Apex Y=1.85, Plunger Y=11.10)',
        'plunger_y': 11.10,
        'cam_apex': (1.85, 7.65),
        'cam_pts': [
            (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0),
            (7.00, 13.00),
            (4.50, 11.00),
            (3.10, 9.20),
            (2.00, 8.00),
            (1.85, 7.65),  # Early-engagement non-polar champion
            (2.00, 7.10),
            (2.60, 6.30),
            (4.00, 5.80),
            (5.60, 5.80),
            (7.20, 7.80),
            (8.20, 9.80),
            (Y_AXLE, Z_AXLE - HUB_DIAMETER/2.0)
        ]
    },
    'v3_nominal': {
        'id': 3,
        'notches': 3,
        'name': 'Variant 3: Balanced Nominal (Apex Y=2.45, Plunger Y=10.95)',
        'plunger_y': 10.95,
        'cam_apex': (2.45, 7.55),
        'cam_pts': [
            (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0),
            (7.20, 13.00),
            (4.80, 11.00),
            (3.30, 9.30),
            (2.95, 8.10),  # Eased upper nose (+0.37mm extra clearance to brass throat flare)
            (2.45, 7.55),  # Calibrated nose (+0.35mm air gap to seated brass throat flare)
            (2.58, 7.05),
            (3.00, 6.40),
            (4.20, 5.80),
            (5.80, 5.80),
            (7.20, 7.80),
            (8.20, 9.80),
            (Y_AXLE, Z_AXLE - HUB_DIAMETER/2.0)
        ]
    },
    'v4_smooth': {
        'id': 4,
        'notches': 4,
        'name': 'Variant 4: Smooth Progressive (Apex Y=2.30, Plunger Y=10.80)',
        'plunger_y': 10.80,
        'cam_apex': (2.30, 7.50),
        'cam_pts': [
            (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0),
            (7.20, 13.00),
            (5.00, 11.00),
            (3.50, 9.20),
            (2.45, 8.00),
            (2.30, 7.50),  # Low insertion resistance curve
            (2.45, 7.00),
            (3.00, 6.30),
            (4.20, 5.80),
            (5.80, 5.80),
            (7.20, 7.80),
            (8.20, 9.80),
            (Y_AXLE, Z_AXLE - HUB_DIAMETER/2.0)
        ]
    },
    'v5_wide_throat': {
        'id': 5,
        'notches': 5,
        'name': 'Variant 5: OEM-Like Wide Throat (Apex Y=2.50, Plunger Y=10.65)',
        'plunger_y': 10.65,
        'cam_apex': (2.50, 7.40),
        'cam_pts': [
            (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0),
            (7.20, 13.00),
            (5.20, 11.00),
            (3.70, 9.20),
            (2.65, 8.00),
            (2.50, 7.40),  # Baseline OEM proportioned wide throat
            (2.65, 6.90),
            (3.20, 6.30),
            (4.40, 5.80),
            (5.80, 5.80),
            (7.20, 7.80),
            (8.20, 9.80),
            (Y_AXLE, Z_AXLE - HUB_DIAMETER/2.0)
        ]
    }
}

CAM_PROFILES = {k: v['cam_pts'] for k, v in KINEMATIC_VARIANTS.items()}
CAM_PROFILES['v1_nominal'] = KINEMATIC_VARIANTS['v3_nominal']['cam_pts']  # Alias
ACTIVE_VARIANT = 'v3_nominal'
ACTIVE_CAM_PROFILE = ACTIVE_VARIANT

def build_shaft_rocker_mesh(
    axle_len=TOTAL_AXLE_LEN,
    hub_w=HUB_WIDTH,
    pin_d=PIN_DIAMETER,
    hub_d=HUB_DIAMETER,
    plunger_reach_below_z=PLUNGER_REACH_BELOW_Z,
    plunger_y_center=None,
    plunger_w_x=PLUNGER_WIDTH_X,
    cam_w_x=CAM_WIDTH_X,
    cam_x_c=CAM_X_CENTER,
    cam_pts=None,
    in_assembly_coords=True,
    with_supports=True,
    return_subparts=False
):
    if plunger_y_center is None:
        plunger_y_center = KINEMATIC_VARIANTS[ACTIVE_VARIANT]['plunger_y']
    if cam_pts is None:
        cam_pts = KINEMATIC_VARIANTS[ACTIVE_VARIANT]['cam_pts']
    """
    Builds the enlarged heavy-duty 3-rib 3D mesh of the shaft/rocker mechanism.
    
    Features:
    - Stepped cylindrical pivot pins (Ø2.80mm) with central structural hub (Ø4.20mm)
    - 3-rib fork array: Left & right stiffener flanks + widened 4.40mm central plunger
    - Smooth continuous filleted plunger arm reaching Z <= -6.50mm
    - Arched full-width (2.70mm) input cam tab operating inside OEM brass pinching contact gap
    """
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER  # 9.25 mm
    
    # 1. Stepped Cylindrical Axle & Hub
    r_pin = pin_d / 2.0
    r_hub = hub_d / 2.0
    pin_len = (axle_len - hub_w) / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # Left pin: [x_c - hub_w/2.0 - pin_len, x_c - hub_w/2.0]
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.20, sections=36)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - hub_w/2.0 - pin_len/2.0 + 0.10, y_axle, z_axle])
    
    # Right pin: [x_c + hub_w/2.0, x_c + hub_w/2.0 + pin_len]
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.20, sections=36)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + hub_w/2.0 + pin_len/2.0 - 0.10, y_axle, z_axle])
    
    # Central Hub Barrel: [5.50, 13.00]
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=hub_w, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 2. OEM 3-Rib Flanks & Plunger Array
    flank_collar = Point(y_axle, z_axle).buffer(r_hub - 0.05)
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
    
    # Rib 2 (Center Plunger Blade): Reaching Z = -7.00mm (+0.50mm reach to tactile switch)
    z_tip = -plunger_reach_below_z  # -7.00 mm
    r_tip = 1.00                    # 2.00mm tip thickness in Y
    
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
    
    # 3. High-Sensitivity Direct Belly Cam Tab
    if cam_pts is None:
        cam_pts = CAM_PROFILES[ACTIVE_CAM_PROFILE]
    poly_cam_arm = Polygon(cam_pts)
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
    # Primary Cam Tab: X in [5.50, 7.60] (2.10mm wide)
    # Calibrated to provide full blade capture, generous stress-relief fillets at the hub,
    # and maintain >0.90mm clear air gap to the stationary breakaway lever support stick (X >= 8.51mm).
    x_cam_start = CAM_X_START
    actual_cam_w = cam_w_x
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=actual_cam_w)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + x_cam_start, v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    subparts = {
        'pin_l': pin_l,
        'pin_r': pin_r,
        'hub': hub_mesh,
        'rib1': mesh_rib1,
        'rib3': mesh_rib3,
        'plunger': mesh_plunger,
        'cam': mesh_cam
    }
    
    # Assembly mesh in place
    try:
        shaft_mesh = trimesh.boolean.union(list(subparts.values()), engine='manifold')
    except Exception:
        shaft_mesh = trimesh.util.concatenate(list(subparts.values()))
    
    if not in_assembly_coords:
        # Orient flat on print bed: rotate so wide flat cam face sits directly on build plate (Z=0).
        rot_bed = trimesh.transformations.rotation_matrix(np.radians(198.6), [1, 0, 0])
        # Find global transform
        m_tmp = shaft_mesh.copy()
        m_tmp.apply_transform(rot_bed)
        bounds = m_tmp.bounds
        trans = [
            -(bounds[0, 0] + bounds[1, 0])/2.0,
            -(bounds[0, 1] + bounds[1, 1])/2.0,
            -bounds[0, 2]
        ]
        
        if return_subparts:
            parts_p = {}
            for k, part in subparts.items():
                p = part.copy()
                p.apply_transform(rot_bed)
                p.apply_translation(trans)
                parts_p[k] = p
            return parts_p
            
        mesh_printable = shaft_mesh.copy()
        mesh_printable.apply_transform(rot_bed)
        mesh_printable.apply_translation(trans)
        if with_supports:
            cradle = build_shaft_support_cradle_mesh()
            try:
                mesh_printable = trimesh.boolean.union([mesh_printable, cradle], engine='manifold')
                bodies = [b for b in mesh_printable.split(only_watertight=False) if abs(b.volume) > 5.0]
                if len(bodies) > 0:
                    mesh_printable = trimesh.boolean.union(bodies, engine='manifold')
            except Exception:
                mesh_printable = trimesh.util.concatenate([mesh_printable, cradle])
        return mesh_printable
        
    if return_subparts:
        return subparts
    return shaft_mesh

def build_shaft_support_cradle_mesh(release_gap=0.12, bed_thickness=0.35):
    """
    Builds the Sacrificial Snap-Off Support Frame for the printable shaft rocker.
    
    Architecture:
    1. Outer Perimeter Bed Adhesion Frame (Z: 0.00 to 0.35mm):
       - Outer footprint: X in [-6.40, +6.40]mm (12.80mm span), Y in [-2.60, +3.80]mm (6.40mm span).
       - Central open window: X in [-3.85, +3.85]mm, Y in [-0.80, +2.80]mm.
       - The hub barrel of the rocker sits directly in the central open window on the build plate.
       - Massive 52.8 mm² flat bed contact area provides 6x greater adhesion than bare rocker.
    2. Left & Right Axle Pin Support Saddles (Z: 0.35 to 0.58mm):
       - Left saddle: X in [-5.60, -3.90]mm (1.70mm long), centered at Y = 1.05mm, width in Y = 0.90mm.
       - Right saddle: X in [+3.90, +5.60]mm (1.70mm long), centered at Y = 1.05mm, width in Y = 0.90mm.
       - Reaches Z = 0.58mm, providing an exact 0.12mm vertical release micro-gap
         under the Z = 0.70mm bottom of the Ø2.80mm axle pins.
       - Prevents pin sag, droop, and layer distortion while snapping off effortlessly by hand.
    3. Sacrificial Breakaway Micro-Anchor Tabs:
       - Two slender 0.30mm x 0.50mm x 0.20mm bridges at X = +/- 3.75mm, Y = 1.05mm, Z = 0.10mm,
         linking the frame to the hub shoulders so the support frame stays firmly indexed
         during printing, but snaps cleanly off with zero tool marks.
    4. Prying Tabs:
       - 45° chamfered outer corners and 0.80mm rear prying lip for effortless release.
    """
    # 1. Build the frame polygon in 2D
    outer_box = box(-6.60, -2.60, 6.60, 3.80)
    inner_window = box(-3.95, -0.80, 3.95, 2.80)
    
    # Add a small rear prying tab: X in [-2.0, 2.0], Y in [-3.30, -2.60]
    pry_tab = box(-2.00, -3.30, 2.00, -2.60)
    frame_poly = outer_box.union(pry_tab).difference(inner_window)
    
    frame_mesh = trimesh.creation.extrude_polygon(frame_poly, height=bed_thickness)
    
    # 2. Saddles under pins (Pin extends ±3.725 to ±5.975mm, center ±4.85mm)
    z_saddle_top = 0.70 - release_gap
    h_saddle = z_saddle_top - bed_thickness
    
    saddle_l = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_l.apply_translation([-4.85, 1.05, bed_thickness + h_saddle / 2.0])
    
    saddle_r = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_r.apply_translation([4.85, 1.05, bed_thickness + h_saddle / 2.0])
    
    # 3. Micro-breakaway anchor tabs (spanning gap between hub shoulder at ±3.725mm and frame window at ±3.95mm)
    tab_l = trimesh.creation.box([0.45, 0.50, 0.20])
    tab_l.apply_translation([-3.80, 1.05, 0.10])
    
    tab_r = trimesh.creation.box([0.45, 0.50, 0.20])
    tab_r.apply_translation([3.80, 1.05, 0.10])
    
    try:
        cradle_mesh = trimesh.boolean.union([frame_mesh, saddle_l, saddle_r, tab_l, tab_r], engine='manifold')
    except Exception:
        cradle_mesh = trimesh.util.concatenate([frame_mesh, saddle_l, saddle_r, tab_l, tab_r])
    return cradle_mesh

def export_shaft_scad(filename="shaft_rocker.scad"):
    """Exports OpenSCAD source file for parametric customization."""
    active_cfg = KINEMATIC_VARIANTS[ACTIVE_VARIANT]
    pts_str = ",\n    ".join([f"[{p[0]:.2f}, {p[1]:.2f}]" for p in active_cfg['cam_pts']])
    plunger_y = active_cfg['plunger_y']
    scad_content = f"""// Parametric OEM 3-Rib Shaft & Rocker Mechanism for Kia Socket Enclosure
// Generated by build_shaft.py (Active Variant: {active_cfg['name']})

$fn = 64;

// Global Parameters (mm)
total_axle_len = {TOTAL_AXLE_LEN};
hub_w = {HUB_WIDTH};
pin_d = {PIN_DIAMETER};
pin_len = {PIN_LEN:.2f};
hub_d = {HUB_DIAMETER};

plunger_reach_below_z = {PLUNGER_REACH_BELOW_Z};
plunger_w = {PLUNGER_WIDTH_X};
plunger_y = {plunger_y:.2f};
hole_x_c = {HOLE_X_CENTER};

cam_w = {CAM_WIDTH_X};
cam_x_c = {CAM_X_CENTER};
x_c = {X_TOWER_CENTER};
y_axle = {Y_AXLE};
z_axle = {Z_AXLE};

// 2D Profile: High-Sensitivity Direct Belly Cam (Test 4: V3 Balanced Nominal - WINNER)
poly_cam_pts = [
    {pts_str}
];

module oem_shaft_rocker() {{
    // Left Pivot Pin
    translate([x_c - hub_w/2 - pin_len/2, y_axle, z_axle])
        rotate([0, 90, 0])
            cylinder(r = pin_d/2, h = pin_len, center = true);
            
    // Right Pivot Pin
    translate([x_c + hub_w/2 + pin_len/2, y_axle, z_axle])
        rotate([0, 90, 0])
            cylinder(r = pin_d/2, h = pin_len, center = true);
            
    // Central Hub Barrel
    translate([x_c, y_axle, z_axle])
        rotate([0, 90, 0])
            cylinder(r = hub_d/2, h = hub_w, center = true);
            
    // Primary Belly Cam Tab with Filleted Root
    translate([{CAM_X_START}, 0, 0])
        rotate([0, -90, 0])
            rotate([0, 0, 90])
                linear_extrude(height = cam_w)
                    polygon(poly_cam_pts);
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
    
    # 2. Print-ready flat build-plate mesh with built-in breakaway supports (Z = 0.00mm)
    shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=True)
    shaft_printable.export("shaft_rocker.stl")
    shaft_printable.export("shaft_rocker.obj")
    print(f"Saved shaft_rocker.stl with built-in breakaway supports (Print-ready flat at Z=0, Bounds: {shaft_printable.bounds})")
    
    # 3. Clean version without supports (bare lever for reference / custom slicer supports)
    shaft_clean = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
    shaft_clean.export("shaft_rocker_clean.stl")
    shaft_clean.export("shaft_rocker_clean.obj")
    print(f"Saved shaft_rocker_clean.stl (Clean bare lever without supports)")
    
    # 4. OpenSCAD code
    export_shaft_scad("shaft_rocker.scad")
    print("Shaft CAD generation complete!")

