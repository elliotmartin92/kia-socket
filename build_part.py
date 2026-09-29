"""
build_part.py
Parametric 3D CAD generator for the automotive 120V AC outlet sub-housing baseplate.

Dual Functional Roles:
1) Current-Carrying Busbar & Terminal Retention: Retains conductive metal pieces inside
   guide brackets (Brackets 1-4) and backside slit channels to route 120V AC power from the
   rear electronics board to the front outlet receptacle.
2) Safety Interlock & Rocker Cradle Support: Mounts the pivot shaft rocker mechanism.
   When the right plug prong is inserted, the rocker actuates a PCB momentary switch,
   ensuring the outlet is energized only when a plug is engaged.

Data Sources & Reverse-Engineering References:
- Reddit OEM Diagnostic Thread: https://www.reddit.com/r/KiaEV6/comments/1n9e8ex/internal_outlet_fix_for_free/p5gh9tp/?screen_view_count=2
- Imgur 18-Photo Teardown Album: https://imgur.com/a/pbAzoX3
"""

import os
import re
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==============================================================================
# DIMENSIONS & SCALING
# ==============================================================================
# Top tab measured width = 8.22 mm. In SVG, top tab width = 23.5 units.
SCALE = 8.22 / 23.5  # ~0.349787234 mm / unit
X0 = 128.65
Y0 = 124.20

BASE_THICK = 1.00
OUTER_WALL_HEIGHT = 6.77
OUTER_WALL_THICK = 1.20

RIB_HEIGHT = 0.50
RIB_THICK = 0.60
RIB_GRID_X = 5.20
RIB_GRID_Y = 3.20

BRACKET_HEIGHT = 4.60
BRACKET_SEATING_RIB_HEIGHT = 1.15   # 1.15mm protrusion above baseplate floor (Z in [1.00, 2.15]mm)
BRACKET_SEATING_RIB_EXT = 1.80      # 1.80mm extension into channel from interior spine walls
BRACKET_SEATING_RIB_THICK = 0.60    # 0.60mm thickness in Y (matching floor ribs)
BRACKET_SEATING_RIB_Y = [5.25, 1.95, -1.35, -4.65]  # 4 Y-stations (Rib 1 bottom corner meets hook corner at Y=4.95mm)

# Clips (Mating with 5.00mm female holes) - Sturdy Proven Architecture
CLIP_HEIGHT = 6.77        # Flush with outer wall
CLIP_GAP_DEPTH = 3.70     # Proven 3.70mm slot depth (ends at Z=3.07mm, leaving 2.07mm solid hoop ring above floor)
CLIP_ARM_THICK = 1.20     # Uniform 1.20mm wall beam thickness (matching outer wall)
CLIP_ARM_WIDTH = 4.20     # 4.20mm wide snap beam (leaves 0.80mm total margin / 0.40mm per side for 5.0mm mating holes)
CLIP_SLOT_CLEARANCE = 0.60 # 0.60mm wide flex slot (eliminates nozzle bridging, ensures clean separate perimeters)
CLIP_HOOK_DEPTH = 1.85    # 1.85mm radial overhang (calibrated 0.25mm less prominent for lower insertion pressure & smooth retention)
CLIP_HOOK_DEPTH_BY_ANGLE = {
    45.0: 1.85,
    135.0: 1.85,
    211.3: 1.85,
    327.5: 1.85,
}
CLIP_STEM_OUTER_RECESS_BY_ANGLE = {
    45.0: 0.00,
    135.0: 0.00,
    211.3: 0.00,
    327.5: 0.00,
}
CLIP_HOOK_HEIGHT = 1.80
CLIP_BLUNT_HEIGHT = 0.53  # 0.53mm prominent vertical squared-off face at outer apex (+51% increase, eliminates knife-edge fragility)
CLIP_CROWN_EASE = 0.20    # 0.20mm top-down continuous crown arc ease (1.85mm at center -> 1.65mm at lateral corners)
CLIP_ROOT_RADIUS = 0.40   # 0.40mm radius (Ø0.80mm) circular stress-relief root at bottom of flex slots
# 4 Clip positions: Top clips (45°, 135°) halfway to top tab; Bottom clips (211.3°, 327.5°) 4.42mm from ears, 8.47mm from bottom tabs
CLIP_ANGLES = [45.0, 135.0, 211.3, 327.5]

# Bottom Slits / Holes (Clearance fit for 0.77mm x 3.10mm mating part)
SLIT_W_X = 1.20         # 1.20mm wide in X (+0.43mm clearance for 0.77mm brass blade)
SLIT_LEN_Y = 3.40       # 3.40mm long in Y (+0.30mm clearance for 3.10mm brass blade)
SLIT_BOSS_HEIGHT = 2.47 # 2.47mm protrusion on back side (-Z)
SLIT_BOSS_WALL = 0.80   # 0.8mm thick wall around slits
# Slit Y positioning: Option 1 (+1.00mm shift in +Y, 2.00mm offset from inner bottom wall, was 1.00mm)
SLIT_OFFSET_FROM_WALL = 2.00

# Slit Insert Detent Socket (High-temp compensated press-fit registration in main baseplate floor)
INSERT_KEY_W_X = 2.44     # Male key base width in X (leaves solid 0.62mm wall around 1.20mm slit)
INSERT_KEY_LEN_Y = 4.64   # Male key base length in Y (leaves solid 0.62mm wall around 3.40mm slit)
INSERT_KEY_TAPER = 0.20   # 0.20mm per side (0.40mm total) self-centering lead-in taper at top of key (2.04x4.24mm tip)
INSERT_KEY_HEIGHT = 0.95  # Male key height in Z on separate insert (nearly flush with 1.00mm floor)
INSERT_CLEARANCE = 0.56   # 0.56mm total clearance (0.28mm per side at base, 0.48mm per side at tip) for high-temp print fit
SOCKET_W_X = INSERT_KEY_W_X + INSERT_CLEARANCE     # 3.00mm female detent socket width in X
SOCKET_LEN_Y = INSERT_KEY_LEN_Y + INSERT_CLEARANCE # 5.20mm female detent socket length in Y
SOCKET_BOT_CHAMFER = 0.35 # 0.35mm x 45 deg bottom elephant's-foot relief countersink on baseplate floor sockets

INSERT_BODY_W_X = 3.30    # 3.30mm outer shroud body width in X at base shoulder (creates horizontal seating shelf)
INSERT_BODY_LEN_Y = 5.50  # 5.50mm outer shroud body length in Y at base shoulder
INSERT_BODY_W_TIP = 2.40  # 2.40mm outer end width in X at Z=0
INSERT_BODY_LEN_TIP = 4.40 # 4.40mm outer end length in Y at Z=0

# Shaft Support Towers (Top-Right Above Hole) - Heavy-Duty Reinforced Enclosed PIP
TOWER_ARCH_RY = 2.85         # 2.85mm arch radius in Y
TOWER_ARCH_RZ = 3.00         # 3.00mm arch radius in Z (Apex at Z = 12.59 + 3.00 = 15.59mm, solid 1.35mm roof over bore)
TOWER_HEIGHT = 14.59         # 14.59mm protrusion above face (Total Z_apex = 15.59mm, cradle center Z = 12.59mm)
TOWER_Y_BASE_LEN = 6.60      # 6.60mm flared base in Y (Y in [6.250, 12.850]mm, exactly aligned with Bracket 3 top inner wall)
TOWER_INTERNAL_GAP = 7.70    # 7.70mm internal gap between reinforced tower inner faces (X: 5.40 to 13.10mm)
TOWER_WALL_THICK = 1.50      # 1.50mm heavy-duty wall thickness in X (+50% column strength)
TOWER_BORE_RADIUS = 1.65     # Ø3.30mm teardrop bore for Ø2.80mm shaft pin (0.25mm radial clearance for smooth PIP)
TOWER_BRIDGE_THICK_Y = 1.25  # 1.25mm thick monolithic rear cross-tie bridge (Y in [11.60, 12.85]mm)
TOWER_BRIDGE_HEIGHT_Z = 2.40 # 2.40mm tall monolithic rear cross-tie bridge (Z in [12.60, 15.00]mm)

# Side Ears (Mating with 8.30mm enclosure guide slot/gap)
EAR_GAP = 8.30             # 8.30mm enclosure guide slot/gap
EAR_CLEARANCE = 0.60       # 0.60mm total clearance (0.30mm per side) for smooth sliding fit without binding
EAR_WIDTH_Y = EAR_GAP - EAR_CLEARANCE  # 7.70mm outer width in Y (Y in [-3.85, +3.85]mm)

# Top Tab (Mating with 8.33mm enclosure guide slot/gap)
TOP_TAB_GAP = 8.33         # 8.33mm enclosure guide slot/gap
TOP_TAB_CLEARANCE = 0.13   # 0.13mm total clearance (0.065mm per side) for smooth sliding fit
TOP_TAB_WIDTH_X = TOP_TAB_GAP - TOP_TAB_CLEARANCE  # 8.20mm outer width in X (X in [-4.10, +4.10]mm)

# ==============================================================================
# EXACT SVG PATH PARSER
# ==============================================================================
def parse_svg_d(d_str):
    """Parse SVG path string into high-resolution (X, Y) points in mm."""
    tokens = re.findall(r'([A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)', d_str)
    points = []
    curr_x, curr_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    
    i = 0
    cmd = None
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
        
        if cmd == 'M':
            curr_x = float(tokens[i])
            curr_y = float(tokens[i+1])
            start_x, start_y = curr_x, curr_y
            points.append((curr_x, curr_y))
            i += 2
            cmd = 'L'
        elif cmd == 'm':
            curr_x += float(tokens[i])
            curr_y += float(tokens[i+1])
            start_x, start_y = curr_x, curr_y
            points.append((curr_x, curr_y))
            i += 2
            cmd = 'l'
        elif cmd == 'L':
            curr_x = float(tokens[i])
            curr_y = float(tokens[i+1])
            points.append((curr_x, curr_y))
            i += 2
        elif cmd == 'l':
            curr_x += float(tokens[i])
            curr_y += float(tokens[i+1])
            points.append((curr_x, curr_y))
            i += 2
        elif cmd == 'H':
            curr_x = float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'h':
            curr_x += float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'V':
            curr_y = float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'v':
            curr_y += float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'C':
            x1, y1 = float(tokens[i]), float(tokens[i+1])
            x2, y2 = float(tokens[i+2]), float(tokens[i+3])
            x3, y3 = float(tokens[i+4]), float(tokens[i+5])
            for t_step in np.linspace(0.04, 1.0, 25):
                bx = (1-t_step)**3 * curr_x + 3*(1-t_step)**2 * t_step * x1 + 3*(1-t_step)*t_step**2 * x2 + t_step**3 * x3
                by = (1-t_step)**3 * curr_y + 3*(1-t_step)**2 * t_step * y1 + 3*(1-t_step)*t_step**2 * y2 + t_step**3 * y3
                points.append((bx, by))
            curr_x, curr_y = x3, y3
            i += 6
        elif cmd == 'c':
            x1, y1 = curr_x + float(tokens[i]), curr_y + float(tokens[i+1])
            x2, y2 = curr_x + float(tokens[i+2]), curr_y + float(tokens[i+3])
            x3, y3 = curr_x + float(tokens[i+4]), curr_y + float(tokens[i+5])
            for t_step in np.linspace(0.04, 1.0, 25):
                bx = (1-t_step)**3 * curr_x + 3*(1-t_step)**2 * t_step * x1 + 3*(1-t_step)*t_step**2 * x2 + t_step**3 * x3
                by = (1-t_step)**3 * curr_y + 3*(1-t_step)**2 * t_step * y1 + 3*(1-t_step)*t_step**2 * y2 + t_step**3 * y3
                points.append((bx, by))
            curr_x, curr_y = x3, y3
            i += 6
        elif cmd in ('Z', 'z'):
            points.append((start_x, start_y))
            cmd = None
        else:
            i += 1
            
    pts_arr = np.array(points)
    # Transform to centered MM coordinates
    pts_mm = np.zeros_like(pts_arr)
    pts_mm[:, 0] = (pts_arr[:, 0] - X0) * SCALE
    pts_mm[:, 1] = -(pts_arr[:, 1] - Y0) * SCALE
    return pts_mm

# Load SVG and extract outer path and features
SVG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'part.svg')
with open(SVG_PATH, 'r') as f:
    svg_text = f.read()

outer_match = re.search(r'<path class="st2" d="([^"]+)"', svg_text)
outer_pts = parse_svg_d(outer_match.group(1))

# Also extract bottom arch path
arch_match = re.search(r'<path class="st3" d="(M132\.6[^"]+)"', svg_text)
if arch_match:
    arch_pts = parse_svg_d(arch_match.group(1))
else:
    arch_pts = None

# ==============================================================================
# GEOMETRY GENERATION (Shapely)
# ==============================================================================
# 1. Exact Bracket Polygons (Looser Interior Clearances & Zero Tower Interference)
# - Spine channel gap widened from 6.856mm to 7.156mm (+0.42mm sliding clearance for 6.74mm brass contact)
# - Top lead-in throat gap widened to 3.500mm (+0.32mm to +0.35mm lead-in opening)
# - Bottom step gap widened to 3.800mm (+0.34mm clearance for S-curved terminal leg)
# - Vertical interior span extended to 12.600mm (Y in [-6.200, +6.400]mm)
# - Top hook face raised to Y=4.950mm, pocket ceiling raised to Y=6.400mm (1.45mm capture depth)
bracket_4_raw_pts = [
    (10.791,  7.171), (8.000,  7.171), (8.000,  4.950), (8.900,  4.950),
    (8.900,  6.400), (9.857,  6.400), (9.857, -6.200), (8.150, -6.200),
    (8.150, -7.136), (10.791, -7.136), (10.791,  7.171)
]
bracket_3_raw_pts = [
    (1.766,  7.171), (4.500,  7.171), (4.500,  4.950), (3.650,  4.950),
    (3.650,  6.400), (2.701,  6.400), (2.701, -6.200), (4.350, -6.200),
    (4.350, -7.171), (1.766, -7.171), (1.766,  7.171)
]
bracket_2_raw_pts = [
    (-1.766,  7.171), (-4.500,  7.171), (-4.500,  4.950), (-3.650,  4.950),
    (-3.650,  6.400), (-2.701,  6.400), (-2.701, -6.200), (-4.350, -6.200),
    (-4.350, -7.136), (-1.766, -7.136), (-1.766,  7.171)
]
bracket_1_raw_pts = [
    (-10.791,  7.136), (-8.000,  7.136), (-8.000,  4.950), (-8.900,  4.950),
    (-8.900,  6.400), (-9.857,  6.400), (-9.857, -6.200), (-8.150, -6.200),
    (-8.150, -7.171), (-10.791, -7.171), (-10.791,  7.136)
]

def to_mm_poly(raw_pts):
    # Points already in exact mm coordinates
    return Polygon(raw_pts)

def create_all_brackets_poly():
    b1 = to_mm_poly(bracket_1_raw_pts)
    b2 = to_mm_poly(bracket_2_raw_pts)
    b3 = to_mm_poly(bracket_3_raw_pts)
    b4 = to_mm_poly(bracket_4_raw_pts)
    return unary_union([b1, b2, b3, b4])

def create_bracket_seating_ribs_poly(ext=BRACKET_SEATING_RIB_EXT, thick=BRACKET_SEATING_RIB_THICK, y_stations=BRACKET_SEATING_RIB_Y):
    """Creates 2D polygons for the seating ribs in both bracket pairs.
    - Left Pair (B1 & B2): all 4 stations extend 1.80mm into channel from spine walls.
    - Right Pair (B3 & B4):
      * Top 3 stations (5.25, 1.95, -1.35mm) extend 1.80mm into channel.
      * Station 4 (-4.65mm, below half moon) extends all the way across from B3 to B4 spine to become one.
    """
    boxes = []
    b1_spine = -9.857
    b2_spine = -2.701
    b3_spine = 2.701
    b4_spine = 9.857
    
    # Left Pair (all 4 stations)
    for y_c in y_stations:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        boxes.append(box(b1_spine, y_min, b1_spine + ext, y_max))
        boxes.append(box(b2_spine - ext, y_min, b2_spine, y_max))
        
    # Right Pair (top 3 stations separate, station 4 extends all the way across)
    for y_c in y_stations[:3]:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
        boxes.append(box(b4_spine - ext, y_min, b4_spine, y_max))
        
    if len(y_stations) >= 4:
        y_c4 = y_stations[3]
        boxes.append(box(b3_spine, y_c4 - thick / 2.0, b4_spine, -4.30))
        
    return unary_union(boxes)

def build_chamfered_seating_ribs_mesh():
    """Builds the 3D mesh of the seating ribs:
    - Standard Unchamfered Ribs (1.15mm tall, Z in [1.00, 2.15]mm, 0.60mm thick in Y, extending 1.80mm into channel):
      * All 4 pairs on Left Brackets (B1 & B2): Y = 5.25, 1.95, -1.35, -4.65 mm.
      * Top 3 pairs on Right Brackets (B3 & B4): Y = 5.25, 1.95, -1.35 mm.
    - One Pair Below Half Moon (Right Brackets B3 & B4 at Y = -4.65 mm):
      * Extended all the way across from B3 spine (X = 2.701 mm) to B4 spine (X = 9.857 mm) to become ONE continuous rib.
      * Chamfered on -Y flank (ramping smoothly over 0.80mm from Z = 1.00mm to 2.15mm) to eliminate stress concentration.
      * Flat seating land at Z = 2.15mm extends to Y = -4.30mm, 100% flush and fused into the half-moon base across Z in [1.00, 2.15]mm.
    """
    z_floor = BASE_THICK  # 1.00 mm
    z_rib = z_floor + BRACKET_SEATING_RIB_HEIGHT  # 2.15 mm
    h_rib = BRACKET_SEATING_RIB_HEIGHT  # 1.15 mm
    
    b1_spine = -9.857
    b2_spine = -2.701
    b3_spine = 2.701
    b4_spine = 9.857
    ext = BRACKET_SEATING_RIB_EXT
    thick = BRACKET_SEATING_RIB_THICK
    
    # 1. Standard unchamfered rectangular ribs
    std_boxes = []
    # Left pair (B1 & B2) - all 4 stations
    for y_c in BRACKET_SEATING_RIB_Y:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        std_boxes.append(box(b1_spine, y_min, b1_spine + ext, y_max))
        std_boxes.append(box(b2_spine - ext, y_min, b2_spine, y_max))
        
    # Right pair (B3 & B4) - only top 3 stations
    for y_c in BRACKET_SEATING_RIB_Y[:3]:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        std_boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
        boxes_b4 = box(b4_spine - ext, y_min, b4_spine, y_max)
        std_boxes.append(boxes_b4)
        
    poly_std = unary_union(std_boxes)
    m_std = extrude_shapely_geom(poly_std, height=h_rib)
    m_std.apply_translation([0, 0, z_floor])
    
    # 2. The ONE pair below the half moon (Right pair, y_c = -4.65)
    # Extends all the way across from b3_spine (2.701) to b4_spine (9.857) to become one
    # Chamfered on -Y flank, fully fused with half moon base at Y = -4.30mm across Z in [1.00, 2.15]mm
    chamf_dy = 0.80  # 0.80mm ramp
    y_c4 = -4.65
    pts_yz = [
        (y_c4 - thick/2.0 - chamf_dy, z_floor), # -5.75, 1.00
        (y_c4 - thick/2.0, z_rib),              # -4.95, 2.15
        (-4.30, z_rib),                         # -4.30, 2.15 (100% flush & fused with half moon base)
        (-4.30, z_floor)                        # -4.30, 1.00 (100% flush & fused with half moon base)
    ]
    poly_yz = Polygon(pts_yz)
    span_r4 = b4_spine - b3_spine
    m_r4_poly = trimesh.creation.extrude_polygon(poly_yz, height=span_r4)
    v4 = m_r4_poly.vertices.copy()
    v_r4 = np.column_stack([v4[:, 2] + b3_spine, v4[:, 0], v4[:, 1]])
    m_r4 = trimesh.Trimesh(vertices=v_r4, faces=m_r4_poly.faces.copy(), process=True)
    
    return trimesh.util.concatenate([m_std, m_r4])

def create_arch_wall_poly():
    """Creates a clean geometric U-arch wall (1.20mm thick) with 5.00mm interior width at base.
    - Interior Width: 5.00mm (inner radius R_inner = 2.50mm), centered on X = 0.
    - Wall thickness: 1.20mm (outer radius R_outer = 3.70mm).
    - Total Outer Height: 7.95mm from inset bottom wall (Y = -16.65mm to outer apex Y = -8.70mm).
    - Arc center at Y = -12.40mm (Inner Apex Y = -9.90mm).
    - Sides: Vertical straight tangent legs from Y = -12.40mm down to inset wall (Y = -16.65mm)."""
    w_inner = 5.00
    r_inner = w_inner / 2.0         # 2.50mm
    wall_thick = OUTER_WALL_THICK  # 1.20mm
    r_outer = r_inner + wall_thick # 3.70mm
    
    y_bot = -16.650
    total_outer_height = 7.950
    y_apex_outer = y_bot + total_outer_height  # -8.700mm
    y_apex_inner = y_apex_outer - wall_thick   # -9.900mm
    y_arc_center = y_apex_inner - r_inner      # -12.400mm
    
    angles = np.linspace(np.pi, 0, 32)
    arc_inner_pts = [(r_inner * np.cos(a), y_arc_center + r_inner * np.sin(a)) for a in angles]
    inner_pts = [(-r_inner, y_bot), (-r_inner, y_arc_center)] + arc_inner_pts + [(r_inner, y_arc_center), (r_inner, y_bot)]
    
    arc_outer_pts = [(r_outer * np.cos(a), y_arc_center + r_outer * np.sin(a)) for a in angles]
    outer_pts_list = [(r_outer, y_bot), (r_outer, y_arc_center)] + list(reversed(arc_outer_pts)) + [(-r_outer, y_arc_center), (-r_outer, y_bot)]
    
    wall_polygon_pts = outer_pts_list + inner_pts
    return Polygon(wall_polygon_pts)

def get_exact_base_polygon():
    pts = outer_pts.copy()
    
    # 1. Adjust Left and Right Side Ears to fit into 8.30mm enclosure gap (EAR_WIDTH_Y = 8.20mm, Y in [-4.10, +4.10]mm)
    half_ear_w = EAR_WIDTH_Y / 2.0
    
    # Right Ear (indices 0..4, 242..243)
    pts[0] = [18.206, half_ear_w]
    pts[1] = [20.200, half_ear_w]
    pts[2] = [20.200, 0.0]
    pts[3] = [20.200, -half_ear_w]
    pts[4] = [18.206, -half_ear_w]
    if len(pts) > 242:
        pts[242] = [18.206, half_ear_w]
        pts[243] = [18.206, half_ear_w]
        
    # Left Ear (indices 111..139)
    pts[111] = [-19.081, -half_ear_w]
    for k in range(112, 136):
        pts[k] = [-21.075, -half_ear_w]
    pts[136] = [-21.075, -half_ear_w]
    pts[137] = [-21.075, 0.0]
    pts[138] = [-21.075, half_ear_w]
    pts[139] = [-19.081, half_ear_w]
    
    # 2. Adjust Top Tab to fit into 8.33mm enclosure gap (TOP_TAB_WIDTH_X = 8.20mm, X in [-4.10, +4.10]mm)
    half_tab_w = TOP_TAB_WIDTH_X / 2.0
    pts[189] = [-half_tab_w, 18.504]
    pts[190] = [-half_tab_w, 20.008]
    pts[191] = [half_tab_w, 20.008]
    pts[192] = [half_tab_w, 18.504]
    
    # 3. Config 1: Align bottom exterior wall notch outer walls with Arch INNER walls (X = ±2.50mm)
    for idx, (x, y) in enumerate(pts):
        if abs(y - (-18.539)) < 0.05:
            if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
                pts[idx] = [2.50, -18.539]
            elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
                pts[idx] = [-2.50, -18.539]
        elif abs(y - (-16.650)) < 0.05:
            if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
                pts[idx] = [2.50, -16.650]
            elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
                pts[idx] = [-2.50, -16.650]
                
    raw_poly = Polygon(pts)
    if not raw_poly.is_valid:
        raw_poly = raw_poly.buffer(0)
    
    # 1. Top-Right rectangular through-hole (extended rearward to Y = 13.75mm for free plunger swing)
    hole_w = (165.7 - 150.4) * SCALE  # 5.352 mm
    hole_x = ((150.4 + 165.7)/2.0 - X0) * SCALE  # 10.284 mm
    hole_y_bot = -((86.8 + 99.7)/2.0 - Y0) * SCALE - ((99.7 - 86.8) * SCALE)/2.0  # 8.570 mm
    hole_y_top = 13.750  # Extended rear wall from 13.082mm to 13.750mm (+0.67mm plunger clearance)
    hole_h = hole_y_top - hole_y_bot  # 5.180 mm
    hole_y = (hole_y_bot + hole_y_top) / 2.0  # 11.160 mm
    hole_box = box(hole_x - hole_w/2, hole_y_bot, hole_x + hole_w/2, hole_y_top)
    
    # 2. Outer Solid Body: complete perimeter including 1.88mm inset bottom wall aligned to arch
    outer_body_poly = raw_poly
    
    # 3. Two Bottom Slit Through-Holes for Direct In-Place Printed Slits (1.20mm x 3.40mm)
    # Left slit: Centered on Bracket 1 datum line (X = -7.853mm, Y = -13.589mm)
    # Right slit: Centered on OEM datum line (X = +8.453mm, Y = -13.589mm)
    cx_left = -7.853
    cx_right = 8.453
    cy = -13.589
    w_slit, len_slit = SLIT_W_X, SLIT_LEN_Y
    
    slit_hole_l = box(cx_left - w_slit/2, cy - len_slit/2, cx_left + w_slit/2, cy + len_slit/2)
    slit_hole_r = box(cx_right - w_slit/2, cy - len_slit/2, cx_right + w_slit/2, cy + len_slit/2)
    
    # Base plate floor (with through-hole and blade slits cut through 1mm floor)
    base_poly = outer_body_poly.difference(unary_union([hole_box, slit_hole_l, slit_hole_r]))
    return base_poly, outer_body_poly, (hole_x, hole_y, hole_w, hole_h)

def create_grid_ribs_poly(base_poly, outer_body_poly=None):
    """Grid ribbing (0.60mm thick lines on a 5.2mm x 3.2mm pitch).
    - Extends all the way to merge and connect directly with the outer perimeter walls.
    - Excludes the bounding envelopes of the brackets.
    - Excludes the bottom section (Y < -7.17mm) where there is zero floor ribbing.
    - Excludes the top-right through hole.
    - Excludes a 3.00mm inward radial flex-relief pocket behind all 4 snap clips (eliminates rib fulcrum pinch)."""
    if outer_body_poly is None:
        outer_body_poly = base_poly
    b1_pts = bracket_1_raw_pts
    b2_pts = bracket_2_raw_pts
    b3_pts = bracket_3_raw_pts
    b4_pts = bracket_4_raw_pts
    
    # 1. Left Bracket Pair Entire Bounding Envelope
    left_pair_bbox = box(
        min(p[0] for p in b1_pts) - 0.1,
        min(p[1] for p in b1_pts) - 0.1,
        max(p[0] for p in b2_pts) + 0.1,
        max(p[1] for p in b2_pts) + 0.1
    )
    
    # 2. Right Bracket Pair Entire Bounding Envelope
    right_pair_bbox = box(
        min(p[0] for p in b3_pts) - 0.1,
        min(p[1] for p in b3_pts) - 0.1,
        max(p[0] for p in b4_pts) + 0.1,
        max(p[1] for p in b4_pts) + 0.1
    )
    
    bracket_exclusions = unary_union([left_pair_bbox, right_pair_bbox])
    below_brackets_box = box(-30.0, -30.0, 30.0, -7.17)
    
    # Top-right through hole exclusion (extended to Y = 13.75mm)
    hole_x, hole_y, hole_w, hole_h = 10.284, 11.160, 5.352, 5.180
    hole_box = box(hole_x - hole_w/2 - 0.1, hole_y - hole_h/2 - 0.1,
                   hole_x + hole_w/2 + 0.1, hole_y + hole_h/2 + 0.1)
                   
    # 3.00mm inward radial flex-relief pocket behind all 4 snap clips so no floor rib acts as a fulcrum
    clip_relief_polys = []
    for angle_deg in CLIP_ANGLES:
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        half_w = (CLIP_ARM_WIDTH + 1.20) / 2.0
        c1 = p + tang * half_w + norm * 0.50
        c2 = p - tang * half_w + norm * 0.50
        c3 = p - tang * half_w - norm * (OUTER_WALL_THICK + 3.00)
        c4 = p + tang * half_w - norm * (OUTER_WALL_THICK + 3.00)
        clip_relief_polys.append(Polygon([c1, c2, c3, c4]))
    clip_relief_union = unary_union(clip_relief_polys)
    
    bounds = outer_body_poly.bounds
    rib_boxes = []
    
    # Vertical ribs (pitch RIB_GRID_X = 5.20mm)
    x_steps = np.concatenate([
        np.arange(0, bounds[2] + 5, RIB_GRID_X),
        np.arange(-RIB_GRID_X, bounds[0] - 5, -RIB_GRID_X)
    ])
    for x in x_steps:
        rib_boxes.append(box(x - RIB_THICK/2, bounds[1] - 5, x + RIB_THICK/2, bounds[3] + 5))
        
    # Horizontal ribs (pitch RIB_GRID_Y = 3.20mm)
    y_steps = np.concatenate([
        np.arange(0, bounds[3] + 5, RIB_GRID_Y),
        np.arange(-RIB_GRID_Y, bounds[1] - 5, -RIB_GRID_Y)
    ])
    for y in y_steps:
        rib_boxes.append(box(bounds[0] - 5, y - RIB_THICK/2, bounds[2] + 5, y + RIB_THICK/2))
        
    raw_grid = unary_union(rib_boxes)
    
    # Intersect with outer_body_poly so all ribs extend directly into the outer walls
    connected_ribs = raw_grid.intersection(outer_body_poly).difference(bracket_exclusions).difference(below_brackets_box).difference(hole_box).difference(clip_relief_union)
    return connected_ribs

# ==============================================================================
# 3D MESH GENERATION (Trimesh)
# ==============================================================================
def extrude_shapely_geom(geom, height):
    polys = geom.geoms if hasattr(geom, 'geoms') else [geom]
    sub_meshes = []
    for poly in polys:
        if not poly.is_empty and poly.area > 1e-4:
            m = trimesh.creation.extrude_polygon(poly, height=height)
            sub_meshes.append(m)
    if len(sub_meshes) == 1:
        return sub_meshes[0]
    elif len(sub_meshes) > 1:
        return trimesh.util.concatenate(sub_meshes)
    return trimesh.Trimesh()

def find_boundary_point_and_normal(base_poly, angle_deg):
    """Find the exact intersection point and outward normal on the non-circular perimeter."""
    rad = math.radians(angle_deg)
    ray_dir = np.array([math.cos(rad), math.sin(rad)])
    ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
    
    exterior = base_poly.exterior
    inter = exterior.intersection(ray)
    if inter.geom_type == 'Point':
        p = np.array([inter.x, inter.y])
    elif hasattr(inter, 'geoms') and len(inter.geoms) > 0:
        p = np.array([inter.geoms[-1].x, inter.geoms[-1].y])
    else:
        p = ray_dir * 19.25
        
    # Compute tangent by projecting adjacent points on perimeter
    dist = exterior.project(Point(p))
    p_prev = np.array(exterior.interpolate(max(0, dist - 0.5)).coords[0])
    p_next = np.array(exterior.interpolate(min(exterior.length, dist + 0.5)).coords[0])
    tangent = p_next - p_prev
    tangent = tangent / np.linalg.norm(tangent)
    normal = np.array([tangent[1], -tangent[0]])
    if np.dot(normal, ray_dir) < 0:
        normal = -normal
    return p, normal, tangent

def create_backside_slit_bosses_poly():
    """Returns the 2D polygon of the protruding shroud walls around the bottom slits on the back side.
    Wall thickness is 0.8mm around the 1.1mm x 3.0mm slit holes."""
    b1_pts = bracket_1_raw_pts
    b4_pts = bracket_4_raw_pts
    b1_rightmost_x = max(p[0] for p in b1_pts)  # -7.853mm
    b4_leftmost_x = min(p[0] for p in b4_pts)   # +7.853mm
    
    slit_y_bot = -18.539 + OUTER_WALL_THICK + SLIT_OFFSET_FROM_WALL  # -15.339mm
    slit_y_top = slit_y_bot + SLIT_LEN_Y                             # -11.989mm
    
    # Left slit outer box and hole
    slit_left_hole = box(b1_rightmost_x - SLIT_W_X, slit_y_bot, b1_rightmost_x, slit_y_top)
    slit_left_outer = box(b1_rightmost_x - SLIT_W_X - SLIT_BOSS_WALL, slit_y_bot - SLIT_BOSS_WALL,
                          b1_rightmost_x + SLIT_BOSS_WALL, slit_y_top + SLIT_BOSS_WALL)
    boss_left = slit_left_outer.difference(slit_left_hole)
    
    # Right slit outer box and hole
    slit_right_hole = box(b4_leftmost_x, slit_y_bot, b4_leftmost_x + SLIT_W_X, slit_y_top)
    slit_right_outer = box(b4_leftmost_x - SLIT_BOSS_WALL, slit_y_bot - SLIT_BOSS_WALL,
                           b4_leftmost_x + SLIT_W_X + SLIT_BOSS_WALL, slit_y_top + SLIT_BOSS_WALL)
    boss_right = slit_right_outer.difference(slit_right_hole)
    return unary_union([boss_left, boss_right])

def create_center_curved_feature_poly():
    """Returns the 2D polygon of the calibrated reinforced curved feature between Brackets 3 & 4.
    - Solid D-shape cross-section: 100% solid core.
    - Width: 4.20mm (centered at X = 6.279mm -> X in [4.179, 8.379]mm).
    - Depth in Y: 1.45mm (Base extended 0.75mm in -Y to Y = -5.05mm, Apex receded in -Y to Y = -3.60mm).
    - Bottom base: Flat solid wall at Y = -5.05mm (extended 0.75mm to backstop flush against brass insert).
    - Front apex: Calibrated to Y = -3.60mm (+0.725mm clearance to nominal 6.35mm plug blade bottom at Y = -2.875mm).
      Eliminates blade collision on insertion while acting as a reliable deflection backstop.
    """
    cx = 6.279
    w_x = 4.20
    base_y = -4.30
    apex_y = -3.60
    extension_y = 0.75  # 0.75mm extension in -Y direction to backstop against brass insert
    
    rx = w_x / 2.0
    ry = apex_y - base_y  # 0.70 mm
    
    angles = np.linspace(np.pi, 0, 33)
    out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
    
    pts = out_arc + [
        (cx + rx, base_y - extension_y),
        (cx - rx, base_y - extension_y)
    ]
    return Polygon(pts)

def build_center_curved_feature_mesh():
    """Builds the 100% watertight 3D mesh of the calibrated half moon with 25% height reduction
    (height = 7.125mm above floor -> Z = 1.00 to 8.125mm) and a smooth 15° lead-in entry chamfer on top.
    """
    poly = create_center_curved_feature_poly()
    h_moon = (10.50 - BASE_THICK) * 0.75  # 7.125mm (25% height drop from 9.50mm)
    z_top = BASE_THICK + h_moon            # 8.125mm
    mesh = extrude_shapely_geom(poly, height=h_moon)
    mesh.apply_translation([0, 0, BASE_THICK])
    
    # Smooth 15° lead-in funnel bevel on the top front face (Z = 6.50 to 8.125mm)
    cx = 6.279
    w_x = 4.20
    apex_y = -3.60
    chamfer_cutter = trimesh.creation.box([w_x + 2.0, 1.0, 2.5])
    rot_chamfer = trimesh.transformations.rotation_matrix(np.radians(-15.0), [1, 0, 0])
    chamfer_cutter.apply_transform(rot_chamfer)
    chamfer_cutter.apply_translation([cx, apex_y + 0.40, z_top - 0.50])
    
    try:
        mesh_chamfered = mesh.difference(chamfer_cutter, engine='manifold')
        if mesh_chamfered.is_watertight and mesh_chamfered.volume > 0:
            return mesh_chamfered
    except Exception:
        pass
        
    return mesh

def create_shaft_support_towers_poly():
    """Returns 2D bounding boxes for the two reinforced shaft support towers and left tower buttress struts."""
    y_min = 6.250
    y_max = 12.850
    
    x_left_outer = 3.900
    x_left_inner = 5.400
    
    x_right_inner = 13.100
    x_right_outer = 14.600
    
    left_box = box(x_left_outer, y_min, x_left_inner, y_max)
    right_box = box(x_right_inner, y_min, x_right_outer, y_max)
    
    # Front strut (starts at top inner wall of Bracket 3 at Y = 6.250mm, X: 1.90 to 3.90mm)
    strut_front = box(1.90, 6.250, x_left_outer, 7.050)
    # Rear strut (full height, X: 1.90 to 3.90mm, Y: 11.650 to 12.850mm)
    strut_rear = box(1.90, 11.650, x_left_outer, 12.850)
    
    return unary_union([left_box, right_box, strut_front, strut_rear])

def build_clean_shaft_towers_mesh():
    """Builds the heavy-duty shaft support towers and rear cross-tie bridge for Print-in-Place (PIP):
    - Left Tower: X in [3.90, 5.40] (1.50mm thick).
    - Right Tower: X in [13.10, 14.60] (1.50mm thick).
    - Fully enclosed 360° journal sockets with a smooth rounded arch crown (Apex Z = 15.59mm, R_z = 3.00mm)
      providing a thick 1.35mm solid roof over the bearing bore.
    - Bore: Ø3.30mm (1.65mm radius) teardrop profile with 45° apex in machine build direction for smooth PIP pivot.
    - Rear Monolithic Cross-Tie Bridge: Spans X in [5.40, 13.10] at Y in [11.60, 12.85], Z in [12.60, 15.00],
      rigidly boxing Left and Right towers together so they CANNOT spread under plug insertion force.
    """
    y_shaft = 9.279
    z_shaft = 12.590
    z_base = BASE_THICK  # 1.0mm
    z_land_bot = 11.200
    r_bore = TOWER_BORE_RADIUS  # 1.65mm (Ø3.30mm bore for Ø2.80mm pin -> 0.25mm radial clearance)
    arch_rx = TOWER_ARCH_RY     # 2.85mm in Y
    arch_rz = TOWER_ARCH_RZ     # 3.00mm in Z (Apex Z = 15.59mm)
    
    y_min_base = 6.250
    y_max_base = 12.850
    y_rear_tangent = y_shaft + arch_rx
    y_front_tangent = y_shaft - arch_rx
    
    # 1. Exterior boundary of the tower in (Y, Z) with smooth rounded arch over axle
    theta_arch = np.linspace(0, np.pi, 48)
    arch_pts = [(y_shaft + arch_rx * np.cos(t), z_shaft + arch_rz * np.sin(t)) for t in theta_arch]
    
    exterior_pts = [
        (y_min_base, z_base),
        (y_max_base, z_base),
        (y_rear_tangent, z_land_bot),
    ] + arch_pts + [
        (y_front_tangent, z_land_bot),
    ]
    
    # 2. Teardrop bore profile in (Y, Z)
    # Direction of machine vertical in unrotated Y-Z plane when tilted 45° around X:
    phi_up = 3 * np.pi / 4.0  # 135 degrees (dY = -1/sqrt(2), dZ = +1/sqrt(2))
    
    # Circular arc for the bottom and sides (270 degrees)
    phi_arc = np.linspace(phi_up + np.pi/4, phi_up + 7*np.pi/4, 48)
    arc_pts = [(y_shaft + r_bore * np.cos(p), z_shaft + r_bore * np.sin(p)) for p in phi_arc]
    
    # Teardrop peak extending upward along phi_up:
    peak_pt = (y_shaft + r_bore * np.sqrt(2.0) * np.cos(phi_up),
               z_shaft + r_bore * np.sqrt(2.0) * np.sin(phi_up))
    
    bore_pts = arc_pts + [peak_pt]
    poly_yz = Polygon(exterior_pts, [bore_pts])
    
    # Extrude along X (thickness = 1.50mm)
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=TOWER_WALL_THICK)
    verts = m_raw.vertices.copy()
    
    # Left tower mesh: X in [3.90, 5.40]
    verts_left = np.column_stack([verts[:, 2] + 3.900, verts[:, 0], verts[:, 1]])
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    if mesh_left.volume < 0:
        mesh_left.faces = np.fliplr(mesh_left.faces)
        
    # Right tower mesh: X in [13.10, 14.60]
    verts_right = np.column_stack([verts[:, 2] + 13.100, verts[:, 0], verts[:, 1]])
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    if mesh_right.volume < 0:
        mesh_right.faces = np.fliplr(mesh_right.faces)
        
    # 3. Rear Monolithic Cross-Tie Bridge
    # Spans X in [5.40, 13.10] (width 7.70mm)
    # Y in [11.60, 12.85] (thickness 1.25mm, leaves >0.22mm air gap behind hub)
    # Z in [12.60, 15.00] (height 2.40mm, solidly bracing both towers)
    bridge_box = trimesh.creation.box([TOWER_INTERNAL_GAP, TOWER_BRIDGE_THICK_Y, TOWER_BRIDGE_HEIGHT_Z])
    bridge_box.apply_translation([
        (5.40 + 13.10) / 2.0,       # X center = 9.25 mm
        (11.60 + 12.85) / 2.0,      # Y center = 12.225 mm
        (12.60 + 15.00) / 2.0       # Z center = 13.80 mm
    ])
    
    try:
        combined = trimesh.boolean.union([mesh_left, mesh_right, bridge_box], engine='manifold')
        if combined.is_watertight:
            return combined
    except Exception:
        pass
        
    return trimesh.util.concatenate([mesh_left, mesh_right, bridge_box])

def build_left_tower_struts_mesh():
    """Builds the dual triangular buttress struts on the left side of the left tower.
    - Front Strut: Starts at Y = 6.250mm (top inner wall of Bracket 3) extending to Y = 7.050mm (X: 1.90 to 3.90mm, Z: 1.00 to 10.90mm).
    - Rear Strut: Triangle at Y: 11.650 to 12.850mm (X: 1.90 to 3.90mm, Z: 1.00 to 10.90mm).
    - Top at Z = 10.90mm leaves +0.30mm vertical clearance below the tower clamp bottom (Z = 11.20mm).
    """
    x_left_outer = 3.900
    z_base = BASE_THICK  # 1.0mm
    z_strut_top = 10.90  # 10.90mm (+0.30mm clear below Z=11.20mm clamp bottom so clamp never hits struts!)
    
    # Triangular strut in (X, Z)
    strut_pts_xz = [
        (1.90, z_base),
        (x_left_outer, z_base),
        (x_left_outer, z_strut_top)
    ]
    poly_xz = Polygon(strut_pts_xz)
    
    # 1. Front Strut at Y in [6.250, 7.050] (0.80mm thick, aligns with top inner wall of Bracket 3!)
    m_front_raw = trimesh.creation.extrude_polygon(poly_xz, height=0.80)
    v_front = m_front_raw.vertices.copy()
    v_front = np.column_stack([v_front[:, 0], v_front[:, 2] + 6.250, v_front[:, 1]])
    mesh_front = trimesh.Trimesh(vertices=v_front, faces=m_front_raw.faces.copy(), process=True)
    if mesh_front.volume < 0:
        mesh_front.faces = np.fliplr(mesh_front.faces)
    
    # 2. Rear Strut at Y in [11.650, 12.850] (1.20mm thick)
    m_rear_raw = trimesh.creation.extrude_polygon(poly_xz, height=1.20)
    v_rear = m_rear_raw.vertices.copy()
    v_rear = np.column_stack([v_rear[:, 0], v_rear[:, 2] + 11.650, v_rear[:, 1]])
    mesh_rear = trimesh.Trimesh(vertices=v_rear, faces=m_rear_raw.faces.copy(), process=True)
    if mesh_rear.volume < 0:
        mesh_rear.faces = np.fliplr(mesh_rear.faces)
    
    return trimesh.util.concatenate([mesh_front, mesh_rear])

def build_exact_3d_model():
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    
    # 1. Extrude Base Plate (Z: 0 to BASE_THICK = 1.0mm) with floor through-holes
    mesh_base = extrude_shapely_geom(base_poly, height=BASE_THICK)
    
    # 1b. In-Place Backside Slit Shrouds (Z: -SLIT_BOSS_HEIGHT = -2.47mm to 0.00mm)
    cx_left, cx_right, cy_sock = -7.853, 8.453, -13.589
    shroud_l = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, -SLIT_BOSS_HEIGHT, 0.0)
    shroud_l.apply_translation([cx_left, cy_sock, 0.0])
    shroud_r = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, -SLIT_BOSS_HEIGHT, 0.0)
    shroud_r.apply_translation([cx_right, cy_sock, 0.0])
    
    slit_cutter_l = extrude_shapely_geom(box(cx_left - SLIT_W_X/2, cy_sock - SLIT_LEN_Y/2, cx_left + SLIT_W_X/2, cy_sock + SLIT_LEN_Y/2), height=SLIT_BOSS_HEIGHT + 2.0)
    slit_cutter_l.apply_translation([0, 0, -SLIT_BOSS_HEIGHT - 1.0])
    shroud_l_hollow = shroud_l.difference(slit_cutter_l, engine='manifold')
    
    slit_cutter_r = extrude_shapely_geom(box(cx_right - SLIT_W_X/2, cy_sock - SLIT_LEN_Y/2, cx_right + SLIT_W_X/2, cy_sock + SLIT_LEN_Y/2), height=SLIT_BOSS_HEIGHT + 2.0)
    slit_cutter_r.apply_translation([0, 0, -SLIT_BOSS_HEIGHT - 1.0])
    shroud_r_hollow = shroud_r.difference(slit_cutter_r, engine='manifold')
    
    mesh_shrouds = trimesh.util.concatenate([shroud_l_hollow, shroud_r_hollow])
    
    # 2. Outer Rim Wall + Arch Wall (Z: BASE_THICK to OUTER_WALL_HEIGHT = 6.77mm)
    # 100% UNTOUCHED, continuous, solid 1.20mm wall across the entire perimeter!
    inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_poly)
    arch_wall_poly = create_arch_wall_poly()
    all_walls_poly = unary_union([wall_poly, arch_wall_poly])
    mesh_wall = extrude_shapely_geom(all_walls_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
    mesh_wall.apply_translation([0, 0, BASE_THICK])
    
    # 3. Floor Grid Ribbing (Z: BASE_THICK to BASE_THICK + RIB_HEIGHT)
    # Plus bridge ribs to the right of the right tower extruded to OUTER_WALL_HEIGHT (6.77mm)
    all_ribs_poly = create_grid_ribs_poly(base_poly, outer_body_poly)
    # Bridge ribbing bounded between through-hole and top outer wall
    bridge_box = box(13.10, 8.5, 25.0, 14.0)
    bridge_ribs_poly = all_ribs_poly.intersection(bridge_box)
    normal_ribs_poly = all_ribs_poly.difference(bridge_box)
    
    mesh_normal_ribs = extrude_shapely_geom(normal_ribs_poly, height=RIB_HEIGHT)
    mesh_normal_ribs.apply_translation([0, 0, BASE_THICK])
    
    mesh_bridge_ribs = extrude_shapely_geom(bridge_ribs_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
    mesh_bridge_ribs.apply_translation([0, 0, BASE_THICK])
    
    mesh_ribs = trimesh.util.concatenate([mesh_normal_ribs, mesh_bridge_ribs])
    
    # 4. Guide Brackets (Z: BASE_THICK to BASE_THICK + BRACKET_HEIGHT)
    brackets_poly = create_all_brackets_poly()
    mesh_brackets = extrude_shapely_geom(brackets_poly, height=BRACKET_HEIGHT)
    mesh_brackets.apply_translation([0, 0, BASE_THICK])
    
    # 4b. Bracket Seating Ribs (Z: BASE_THICK to BASE_THICK + BRACKET_SEATING_RIB_HEIGHT = 1.00 to 2.15mm)
    # Chamfered 45° stress-relief ramps from one rib to the next and Rib 4 bridge fusing with half moon
    mesh_seating_ribs = build_chamfered_seating_ribs_mesh()
    
    # 6. Shaft Support Towers & Triangular Struts (Z: 1.0 to 13.59mm)
    mesh_towers = build_clean_shaft_towers_mesh()
    mesh_struts = build_left_tower_struts_mesh()
    mesh_towers_assembly = trimesh.util.concatenate([mesh_towers, mesh_struts])
    
    # Inward flex clearance relief on Right Tower behind 45° snap clip
    p45, norm45, _ = find_boundary_point_and_normal(base_poly, 45.0)
    center_rad_45 = math.radians(45.0)
    tower_clearance_box = trimesh.creation.box([CLIP_ARM_WIDTH + 1.0, 3.0, 7.0])
    rot_45 = trimesh.transformations.rotation_matrix(center_rad_45, [0, 0, 1])
    tower_clearance_box.apply_transform(rot_45)
    p_cut_45 = p45 - norm45 * (OUTER_WALL_THICK + 1.0)
    tower_clearance_box.apply_translation([p_cut_45[0], p_cut_45[1], 3.5 + BASE_THICK])
    try:
        mesh_towers_assembly = mesh_towers_assembly.difference(tower_clearance_box, engine='manifold')
    except Exception:
        pass
    
    # 7. Snap Clips: Sturdy Architecture with Solid Hoop Base (4 clips: 45°, 135°, 211.3°, 327.5°)
    slot_cuts = []
    hook_meshes = []
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT         # 4.97 mm
    slot_z_bot = OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH # 3.07 mm (leaves 2.07mm solid hoop ring above floor)
    z_root_center = slot_z_bot + CLIP_ROOT_RADIUS   # 3.47 mm (center of radiused root)
    slot_t = CLIP_SLOT_CLEARANCE                    # 0.60mm wide flex slot for clean printing
    
    for angle_deg in CLIP_ANGLES:
        center_rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = CLIP_ARM_WIDTH / r_est
        slot_d_theta = slot_t / r_est
        hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        
        # 1. Two vertical flex slots with stress-relief circular roots at slot bottom
        for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
            slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
            rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
            
            # Vertical slot box from root center up to top of wall (+1.0mm)
            box_h = (OUTER_WALL_HEIGHT + 1.0) - z_root_center
            s_box = trimesh.creation.box([OUTER_WALL_THICK * 4.0, slot_t, box_h])
            s_box.apply_transform(rot_mat)
            s_box.apply_translation([slot_p[0], slot_p[1], z_root_center + box_h / 2.0])
            
            # Smooth circular stress-relief root cylinder at slot bottom
            cyl = trimesh.creation.cylinder(radius=CLIP_ROOT_RADIUS, height=OUTER_WALL_THICK * 4.0, sections=16)
            rot_to_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
            cyl.apply_transform(rot_to_x)
            cyl.apply_transform(rot_mat)
            cyl.apply_translation([slot_p[0], slot_p[1], z_root_center])
            
            s_cutter = trimesh.util.concatenate([s_box, cyl])
            slot_cuts.append(s_cutter)
            
        # 2. Solid Faced-Off Crowned Hook Wedge on outer face of flexible wall beam (Z: 4.97 to 6.77mm)
        N = 32
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        half_w = CLIP_ARM_WIDTH / 2.0
        
        outer_coords = []
        shelf_coords = []
        inner_overlap_coords = []
        
        for th in theta_vals:
            ray_dir = np.array([np.cos(th), np.sin(th)])
            ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
            inter_out = outer_body_poly.exterior.intersection(ray)
            if inter_out.geom_type == 'Point':
                po = np.array([inter_out.x, inter_out.y])
            elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
                po = np.array([inter_out.x, inter_out.y]) if hasattr(inter_out, 'x') else np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
            else:
                po = ray_dir * r_est
                
            n_dir = po / np.linalg.norm(po)
            t = (th - center_rad) * r_est
            frac = abs(t / half_w)
            eff_depth = hook_depth - CLIP_CROWN_EASE * (frac ** 2.0)
            
            ps = po + n_dir * eff_depth
            # Penetrate 0.25mm inward into the wall stem so the boolean union completely dissolves the interface
            p_in = po - n_dir * 0.25
            
            outer_coords.append(po)
            shelf_coords.append(ps)
            inner_overlap_coords.append(p_in)
            
        inner_overlap_coords = np.array(inner_overlap_coords)
        shelf_coords = np.array(shelf_coords)
        
        # Faced-off Hook Wedge on outer face of flexible wall beam (Z: 4.97 to 6.77mm)
        v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
        v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
        v_face = np.column_stack([shelf_coords, np.full(N, stem_h + CLIP_BLUNT_HEIGHT)])
        v2 = np.column_stack([inner_overlap_coords, np.full(N, CLIP_HEIGHT)])
        hook_verts = np.vstack([v0, v1, v_face, v2])
        
        hook_faces = []
        for i in range(N - 1):
            # Retention shelf (at stem_h, pointing -Z): V0 -> V1
            hook_faces.append([i, N + i + 1, N + i])
            hook_faces.append([i, i + 1, N + i + 1])
            
            # Faced-off vertical blunt tip: V1 -> V_face
            hook_faces.append([N + i, 2*N + i + 1, 2*N + i])
            hook_faces.append([N + i, N + i + 1, 2*N + i + 1])
            
            # Slanted lead-in ramp: V_face -> V2
            hook_faces.append([2*N + i, 3*N + i + 1, 3*N + i])
            hook_faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
            
            # Inner mating face (inside outer wall stem): V2 -> V0
            hook_faces.append([3*N + i, i + 1, i])
            hook_faces.append([3*N + i, 3*N + i + 1, i + 1])
            
        # Side endcaps
        hook_faces.append([0, 2*N, 3*N])
        hook_faces.append([0, N, 2*N])
        hook_faces.append([N - 1, 3*N - 1, 2*N - 1])
        hook_faces.append([N - 1, 4*N - 1, 3*N - 1])
        
        hook_mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
        if hook_mesh.volume < 0:
            hook_mesh.faces = np.fliplr(hook_mesh.faces)
        hook_meshes.append(hook_mesh)
        
    # 1. Monolithically fuse hook wedges into outer wall
    unmerged_hooks = []
    for hm in hook_meshes:
        try:
            mesh_wall = mesh_wall.union(hm, engine='manifold')
        except Exception:
            unmerged_hooks.append(hm)
            
    # 2. Cut vertical flex slots through the monolithic wall + hook assembly
    try:
        all_slot_cuts = trimesh.util.concatenate(slot_cuts)
        mesh_wall = mesh_wall.difference(all_slot_cuts, engine='manifold')
        mesh_towers_assembly = mesh_towers_assembly.difference(all_slot_cuts, engine='manifold')
    except Exception:
        pass
        
    # 8. Center Curved Feature: Blade-Calibrated & Flared-Base Reinforced (Z: 1.0 to 8.125mm)
    mesh_curved_feat = build_center_curved_feature_mesh()
    
    # 8b. Thin Removable 45° Breakaway Supports for Bottom Clips (211.3° and 327.5°)
    mesh_clip_supports = build_bottom_clip_45deg_supports_mesh(base_poly)
    
    # Main part with in-place printed slit shrouds and clip supports
    full_part = trimesh.util.concatenate([mesh_base, mesh_shrouds, mesh_wall, mesh_ribs, mesh_brackets, mesh_seating_ribs, mesh_towers_assembly, mesh_curved_feat, mesh_clip_supports] + unmerged_hooks)
    
    # Filter and monolithically fuse into a single solid watertight body
    try:
        bodies = full_part.split(only_watertight=False)
        valid_bodies = []
        for b in bodies:
            if abs(b.volume) > 0.001:
                if b.volume < 0:
                    b.faces = np.fliplr(b.faces)
                valid_bodies.append(b)
        if len(valid_bodies) > 0:
            try:
                full_part = trimesh.boolean.union(valid_bodies, engine='manifold')
            except Exception:
                full_part = trimesh.util.concatenate(valid_bodies)
    except Exception:
        pass
        
    return full_part, base_poly

def build_clip_supports_mesh(base_poly):
    """Builds twin-prong sacrificial breakaway support towers directly under the 4 snap clip hook overhangs.
    - Base sits flat on the print bed at Z = 0.00mm with foot (1.20mm radial x 3.20mm tangential) for bed adhesion.
    - Solid lower trunk (0.65mm radial x 2.80mm tangential) from Z = 0.35mm to Z = 3.20mm prevents wobble.
    - Central prying arch window allows effortless tool leverage.
    - Slender twin vertical prongs at lateral edges (Y = +/- 1.30mm, 0.55mm radial x 0.65mm tangential) rise to Z = 4.61mm.
    - Micro-chisel contact tips (0.25mm radial x 0.55mm tangential x 0.10mm tall, -57% contact area) reach Z = 4.71mm,
      leaving an expanded 0.26mm Z-gap below the 4.97mm shelf to eliminate thermal fusion at high print temperatures.
    """
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
    tip_h = 0.10
    z_gap = 0.26                             # 0.26mm vertical release gap (prevents thermal welding at high print temps)
    support_top_z = stem_h - z_gap - tip_h   # 4.61mm (tips reach 4.71mm)
    
    y_prongs = [-1.30, 1.30]
    prong_w_tang = 0.65                      # Slimmed from 0.85mm
    prong_t_rad = 0.55                       # Slimmed from 0.75mm (increases wall air gap to >= 0.35mm)
    tip_w_tang = 0.55                        # Micro-chisel width (was 0.85mm)
    tip_t_rad = 0.25                         # Micro-chisel depth (was 0.38mm)
    
    support_meshes = []
    for angle_deg in CLIP_ANGLES:
        rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        r_supp_radial = max(0.62, hook_depth * 0.58)
        
        pos_center = n_dir * (r_wall + r_supp_radial)
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
        
        # 1. Compact bed adhesion foot (Z in [0, 0.35]mm, 1.20mm radial x 3.20mm tangential)
        foot = trimesh.creation.box([1.20, 3.20, 0.35])
        foot.apply_transform(rot)
        foot.apply_translation([pos_center[0], pos_center[1], 0.175])
        
        # 2. Lower solid shared trunk (Z in [0.35, 3.20]mm -> height 2.85mm, 0.65mm radial x 2.80mm tangential)
        z_trunk_h = 2.85
        trunk = trimesh.creation.box([0.65, 2.80, z_trunk_h])
        trunk.apply_transform(rot)
        trunk.apply_translation([pos_center[0], pos_center[1], 0.35 + z_trunk_h / 2.0])
        
        # 3. Slender twin vertical prongs (Z in [3.20, 4.61]mm -> height 1.41mm, at Y = +/- 1.30mm)
        z_prong_h = support_top_z - 3.20
        prong_parts = []
        for yp in y_prongs:
            prong = trimesh.creation.box([prong_t_rad, prong_w_tang, z_prong_h])
            prong.apply_translation([0, yp, 0])
            prong.apply_transform(rot)
            prong.apply_translation([pos_center[0], pos_center[1], 3.20 + z_prong_h / 2.0])
            prong_parts.append(prong)
            
        # 4. Micro-chisel breakaway contact tips (Z in [4.61, 4.71]mm -> height 0.10mm, 0.26mm clear gap to 4.97mm shelf)
        tip_parts = []
        for yp in y_prongs:
            tip = trimesh.creation.box([tip_t_rad, tip_w_tang, tip_h])
            tip.apply_translation([0, yp, 0])
            tip.apply_transform(rot)
            tip.apply_translation([pos_center[0], pos_center[1], support_top_z + tip_h / 2.0])
            tip_parts.append(tip)
            
        supp_combined = trimesh.util.concatenate([foot, trunk] + prong_parts + tip_parts)
        support_meshes.append(supp_combined)
        
    return trimesh.util.concatenate(support_meshes)

def build_bottom_clip_45deg_supports_mesh(base_poly):
    """Builds thin, easily removable 45° breakaway support struts under the bottom clips (211.3° and 327.5°):
    - Sprouts directly from the solid clip stem at a 45° angle to support the hook shelf and eliminate sagging.
    - Twin slender struts (0.80mm wide x 0.55mm beam thickness) leaving a wide 1.60mm open center space.
    - Root penetrates 0.25mm into the stem wall with a neck notch (0.40mm tall in Z at the stem surface)
      ensuring rock-solid print adhesion and a clean, flush snap-off when twisted with needle-nose pliers.
    - Top chisel tip (0.35mm radial contact) catches the underside of the shelf perimeter right at Z = 4.97mm.
    - Preserves 100% of the flat horizontal retention shelf once snapped off.
    """
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97 mm
    hook_depth = CLIP_HOOK_DEPTH            # 1.85 mm
    half_w = CLIP_ARM_WIDTH / 2.0           # 2.10 mm
    z_stem = stem_h - hook_depth            # 3.12 mm
    
    prong_w = 0.80
    prong_offsets = [-1.20, 1.20]
    bottom_clip_angles = [211.3, 327.5]
    
    support_meshes = []
    
    for angle_deg in bottom_clip_angles:
        rad = math.radians(angle_deg)
        u_r = np.array([math.cos(rad), math.sin(rad)])
        u_t = np.array([-math.sin(rad), math.cos(rad)])
        p, _, _ = find_boundary_point_and_normal(base_poly, angle_deg)
        
        prongs = []
        for yo in prong_offsets:
            eff_depth = hook_depth - CLIP_CROWN_EASE * ((abs(yo) / half_w) ** 2.0)
            pts_rz = [
                (-0.25, z_stem - 0.25),       # root inside stem wall
                (-0.25, z_stem + 0.15),       # root inside stem wall
                (0.00,  z_stem + 0.15),       # stem outer face (top of neck)
                (eff_depth - 0.35, stem_h),   # shelf contact start
                (eff_depth, stem_h),          # shelf contact end (outer perimeter edge)
                (eff_depth, stem_h - 0.20),   # outer chamfer
                (0.00,  z_stem - 0.25),       # stem outer face (bottom of neck)
            ]
            poly_rz = Polygon(pts_rz)
            m2d = trimesh.creation.extrude_polygon(poly_rz, height=prong_w)
            v = m2d.vertices.copy()
            v_local = np.column_stack([v[:, 0], v[:, 2] - prong_w/2.0 + yo, v[:, 1]])
            m_p = trimesh.Trimesh(vertices=v_local, faces=m2d.faces.copy(), process=True)
            if m_p.volume < 0:
                m_p.faces = np.fliplr(m_p.faces)
            prongs.append(m_p)
            
        m_pair = trimesh.util.concatenate(prongs)
        M = np.eye(4)
        M[:3, 0] = [u_r[0], u_r[1], 0]
        M[:3, 1] = [u_t[0], u_t[1], 0]
        M[:3, 2] = [0, 0, 1]
        M[:3, 3] = [p[0], p[1], 0]
        m_pair.apply_transform(M)
        support_meshes.append(m_pair)
        
    return trimesh.util.concatenate(support_meshes)

def create_frustum_mesh(w_bot, l_bot, w_top, l_top, z_bot, z_top):
    """Creates a solid watertight 6-faced rectangular frustum."""
    v_bot = np.array([
        [-w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2,  l_bot/2, z_bot],
        [-w_bot/2,  l_bot/2, z_bot],
    ])
    v_top = np.array([
        [-w_top/2, -l_top/2, z_top],
        [ w_top/2, -l_top/2, z_top],
        [ w_top/2,  l_top/2, z_top],
        [-w_top/2,  l_top/2, z_top],
    ])
    verts = np.vstack([v_bot, v_top])
    faces = [
        [0, 3, 2], [0, 2, 1],       # Bottom face (normal -Z)
        [4, 5, 6], [4, 6, 7],       # Top face (normal +Z)
        [0, 1, 5], [0, 5, 4],       # Front face (-Y)
        [1, 2, 6], [1, 6, 5],       # Right face (+X)
        [2, 3, 7], [2, 7, 6],       # Back face (+Y)
        [3, 0, 4], [3, 4, 7],       # Left face (-X)
    ]
    return trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)

def build_slit_insert_mesh(is_hollow=True, inner_hole_w=SLIT_W_X, inner_hole_l=SLIT_LEN_Y, is_right=True):
    """Builds a single 100% monolithic, watertight 3D-printable slit insert part with polarized self-centering tapered key.
    - Flat print bed face at Z = 0 (2.40mm wide x 4.40mm long outer end tip).
    - Sloped wall body expanding to 3.30x5.50mm at shoulder Z=2.47mm.
    - Continuous solid horizontal shoulder at Z = 2.47mm (flush mating face against baseplate floor).
    - Raised self-centering tapered indexing registration key: 2.44x4.64mm at shoulder tapering to 2.04x4.24mm at top tip (Z=3.42mm)
      with 45° polarized corner chamfer (provides 0.28mm/side base clearance and 0.48mm/side lead-in entry clearance at higher print temps).
    - Continuous inner through-hole: 1.20mm x 3.40mm from Z = 0 to 3.42mm (generous clearance for 0.77x3.10mm brass blade).
    """
    z0 = 0.00
    z1 = SLIT_BOSS_HEIGHT  # 2.47mm
    z2 = z1 + INSERT_KEY_HEIGHT  # 3.42mm
    
    # 1. Shroud body: Frustum from Z=0 to Z=2.47mm (100% monolithic, untouched 4-sided frustum)
    m_body = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, z0, z1)
    
    # 2. Polarized Self-Centering Tapered Key / Lip on Top (Z: 2.47 to 3.42mm):
    # Tapers inward by INSERT_KEY_TAPER (0.20mm per side) toward Z=3.42mm so the tip drops freely into high-temp printed sockets
    m_key_frustum = create_frustum_mesh(
        INSERT_KEY_W_X, INSERT_KEY_LEN_Y,
        INSERT_KEY_W_X - 2.0 * INSERT_KEY_TAPER, INSERT_KEY_LEN_Y - 2.0 * INSERT_KEY_TAPER,
        z1 - 0.05, z2
    )
    
    key_poly_raw = box(-INSERT_KEY_W_X/2 - 0.1, -INSERT_KEY_LEN_Y/2 - 0.1, INSERT_KEY_W_X/2 + 0.1, INSERT_KEY_LEN_Y/2 + 0.1)
    d_chamfer = 0.75  # 0.75mm x 45 deg chamfer matching socket polarizing chamfer
    if is_right:
        # Chamfer bottom-right corner of the lip (also tapered inward by 0.15mm toward top)
        p1 = [INSERT_KEY_W_X/2 - d_chamfer - 0.10, -INSERT_KEY_LEN_Y/2]
        p2 = [INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + d_chamfer + 0.10]
        chamfer_tri = Polygon([[p1[0], p1[1] - 0.20],
                               [p2[0] + 0.20, p2[1]],
                               [p2[0] + 0.20, p1[1] - 0.20]])
    else:
        # Chamfer bottom-left corner of the lip
        p1 = [-INSERT_KEY_W_X/2 + d_chamfer + 0.10, -INSERT_KEY_LEN_Y/2]
        p2 = [-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + d_chamfer + 0.10]
        chamfer_tri = Polygon([[p1[0], p1[1] - 0.20],
                               [p2[0] - 0.20, p2[1]],
                               [p2[0] - 0.20, p1[1] - 0.20]])
        
    key_poly = key_poly_raw.difference(chamfer_tri)
    m_key_mask = extrude_shapely_geom(key_poly, height=(z2 - z1) + 0.20)
    m_key_mask.apply_translation([0, 0, z1 - 0.10])
    m_key = m_key_frustum.intersection(m_key_mask, engine='manifold')
    
    # Solid insert: body is 100% untouched, only the lip has the polarized chamfer and self-centering taper
    m_solid = m_body.union(m_key, engine='manifold')
    
    if is_hollow:
        slit_poly_raw = box(-inner_hole_w/2, -inner_hole_l/2, inner_hole_w/2, inner_hole_l/2)
        slit_cutter = extrude_shapely_geom(slit_poly_raw, height=z2 + 2.0)
        slit_cutter.apply_translation([0, 0, -0.5])
        return m_solid.difference(slit_cutter, engine='manifold')
    return m_solid

def build_cooling_tower_mesh(radius=2.0, height=20.50):
    """Builds a sacrificial cylindrical cooling / heatbreak tower (Ø4mm x 20.50mm tall) for 1-click print plate placement.
    Forces the nozzle to travel away from the delicate shaft support towers (Z = 14.09mm) and shaft rocker (Z = 19.86mm)
    on high layers, giving each layer of the delicate tips dedicated time to cool and solidify."""
    tower = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    tower.apply_translation([0, 0, height / 2.0])  # Base flat at Z = 0.00mm
    return tower

def build_indexed_assembly_mesh(main_mesh, insert_mesh=None, shaft_mesh=None, include_cooling_tower=True):
    """Creates the complete 3D build-plate layout with the main part (with in-place printed slit shrouds),
    the shaft rocker mechanism, and a sacrificial cooling tower arranged on the same plane (Z = 0.00mm)
    for 1-click support-free 3D printing."""
    meshes = [main_mesh]
    if shaft_mesh is not None:
        shaft_plate = shaft_mesh.copy()
        shaft_plate.apply_translation([27.50, 6.00, 0.00])
        meshes.append(shaft_plate)
        
    if include_cooling_tower:
        cool_tower = build_cooling_tower_mesh(radius=2.0, height=20.50)
        cool_tower.apply_translation([27.50, -18.00, 0.00])
        meshes.append(cool_tower)
    return trimesh.util.concatenate(meshes)

def build_insert_backside_breakaway_supports_mesh():
    """Builds thin, sacrificial breakaway support struts under the back side of the integrated slit inserts.
    - Sits on the build plate (Z = 0.00mm) inside the relief cutout area.
    - Supports the steep 32.5° overhang of the insert back wall from Z = 0.20mm (tip ridge) up to Z = 1.56mm (floor).
    - Twin slender struts (0.60mm wide in X) spaced at X = cx ± 0.90mm for each insert (cx = -7.853mm, cx = +8.453mm).
    - Leaves an open 1.20mm center window directly under the 1.10mm slit through-hole so no support material enters or clogs the hole.
    - Thin 0.60mm wall snaps cleanly off the insert face with needle-nose pliers or peels off with the bed pad.
    """
    cx_left, cx_right = -7.853, 8.453
    y_tip = -9.418
    z_tip = 0.198
    y_floor = -11.553
    z_floor = 1.556
    
    pts_yz = [
        (-11.80, 0.00),         # bed anchor back
        (-9.20,  0.00),         # bed anchor front
        (-9.20,  z_tip),        # tip support front
        (y_tip,  z_tip),        # tip ridge contact
        (y_floor, z_floor),     # floor junction contact
        (-11.80, z_floor),      # back vertical
    ]
    poly_yz = Polygon(pts_yz)
    
    strut_w = 0.60
    offsets = [-0.90, 0.90]
    
    prongs = []
    for cx in [cx_left, cx_right]:
        for xo in offsets:
            m2d = trimesh.creation.extrude_polygon(poly_yz, height=strut_w)
            v = m2d.vertices.copy()
            v_3d = np.column_stack([v[:, 2] - strut_w/2.0 + cx + xo, v[:, 0], v[:, 1]])
            m_p = trimesh.Trimesh(vertices=v_3d, faces=m2d.faces.copy(), process=True)
            if m_p.volume < 0:
                m_p.faces = np.fliplr(m_p.faces)
            prongs.append(m_p)
            
    return trimesh.util.concatenate(prongs)

def build_45deg_supported_part_mesh(base_mesh, base_poly=None, include_pip_shaft=True):
    """Generates the 45-degree tilted main part with in-place slit shrouds, baked-in breakaway Support Fins,
    and Print-in-Place (PIP) captive safety lever with dedicated breakaway plunger support strut:
    - Tilted 45 deg about X: Re-orients layer planes so inter-layer cleavage failure on the half moon is eliminated.
    - Captive PIP Shaft Rocker: Printed in place inside the enclosed 360° bridged towers with 0.25mm radial/lateral clearances.
    - Dedicated Breakaway Plunger Strut: Vertical column rising from the bed pad up to 0.20mm below the plunger belly.
    - Hardcoded 45° angled breakaway supports for bottom clips (211.3° & 327.5°) coming out of the stem.
    - Solid 0.60mm bed adhesion pad with relief openings under the in-place shroud tips.
    - Thin breakaway twin support struts under the back side of each integrated insert (1.2mm center gap clears slit holes).
    - 5 vertical fin walls under the 45 deg inclined backplate:
      * Inner pair at X = +/-8.0mm (Y: -5.80 to +14.00mm) — primary support under brackets and shaft towers.
      * Outer pair at X = +/-14.0mm (Y: -3.00 to +10.00mm) — catches outer baseplate floor overhangs.
      * Center fin at X = 0.0mm (Y: -3.00 to +10.00mm) — catches mid-plane wall/floor overhangs.
    - 0.24mm release gap (tweaked from 0.20mm) with periodic horizontal breakaway tines (0.55mm W x 0.45mm L)
      every 4.5mm (tweaked from 3.1mm) for effortless, clean breakaway.
    - Lateral sway braces at X = -22.20mm and X = +21.32mm stabilizing the tall tilted part.
    """
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    fin_components = []
    
    # 1. Monolithic Bed Adhesion Pad (48mm wide x 33mm long x 0.60mm thick on bed Z in [0, 0.60]mm)
    pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
    pad_mesh.apply_translation([0.0, -2.50, 0.30])
    
    # In-place shroud tip relief windows to prevent tip fusing into bed pad
    cx_left, cx_right = -7.853, 8.453
    relief_l = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_l.apply_translation([cx_left, -9.5, 0.30])
    relief_r = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_r.apply_translation([cx_right, -9.5, 0.30])
    try:
        pad_mesh = pad_mesh.difference(trimesh.util.concatenate([relief_l, relief_r]), engine='manifold')
    except Exception:
        pass
    fin_components.append(pad_mesh)
    
    # 1b. Thin Breakaway Supports under Back Side of Integrated Slit Inserts (prevents 32.5° overhang sagging)
    insert_supps = build_insert_backside_breakaway_supports_mesh()
    fin_components.append(insert_supps)
    
    # 1c. Dedicated Breakaway Support Strut under Print-in-Place Plunger Belly
    # Rises from bed pad at X = 10.284mm (center of through-hole & plunger blade), Y' = 11.30mm
    # Standoff release micro-gap = 0.20mm below the Z' = 15.63mm plunger tip
    z_plunger_lowest = 2.52 - z_min  # ~15.63mm
    z_strut_top = z_plunger_lowest - 0.20  # 0.20mm release micro-gap
    strut_h = z_strut_top - 0.60
    if strut_h > 1.0:
        trunk_h = strut_h - 1.20
        trunk = trimesh.creation.box([1.40, 1.80, trunk_h])
        trunk.apply_translation([10.284, 11.30, 0.60 + trunk_h / 2.0])
        fin_components.append(trunk)
        
        tip = trimesh.creation.box([0.70, 1.00, 1.20])
        tip.apply_translation([10.284, 11.30, z_strut_top - 0.60])
        fin_components.append(tip)
    
    # 2. Main Support Fins under the 45° inclined backplate
    #    Calibrated tines: 0.55mm width x 0.45mm length, 0.24mm standoff, 4.5mm pitch for clean release
    fin_thick_x = 0.80  # 2 nozzle perimeters
    standoff = 0.24     # 0.24mm release gap (tweaked for easy peeling)
    z_bed = 0.60
    tine_w_x = 0.55     # Slimmed from 0.80 to 0.55mm (-31% contact width)
    tine_l_y = 0.45     # Shortened from 0.60 to 0.45mm (-25% contact length)
    tine_pitch = 4.50   # Expanded pitch from 3.10 to 4.50mm (~30% fewer contact points)
    
    # --- Inner Fin Pair (X = ±8.0mm): extended Y from -5.80 to +14.00mm ---
    y_start_inner = -5.80
    y_end_inner = 14.00   # Extended from 12.30 to 14.00mm (+1.70mm) for upper baseplate coverage
    z_start_inner = y_start_inner - z_min - standoff
    z_end_inner = y_end_inner - z_min - standoff
    
    for x_pos in [-8.0, 8.0]:
        pts_yz = [
            (y_start_inner, z_bed),
            (y_start_inner, z_start_inner),
            (y_end_inner, z_end_inner),
            (y_end_inner, z_bed)
        ]
        poly_yz = Polygon(pts_yz)
        if poly_yz.is_valid and poly_yz.area > 0.1:
            m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
            v = m_fin_raw.vertices.copy()
            v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
            m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
            fin_components.append(m_fin)
            
            # Horizontal breakaway tines along this fin
            y_tine_stations = np.arange(y_start_inner + 2.0, y_end_inner - 1.0, tine_pitch)
            for yt in y_tine_stations:
                zt_underside = yt - z_min
                tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.05])
                fin_components.append(tine)
                
    # --- Outer Fin Pair (X = ±14.0mm): catches outer baseplate floor overhangs ---
    y_start_outer = -3.00
    y_end_outer = 10.00
    z_start_outer = y_start_outer - z_min - standoff
    z_end_outer = y_end_outer - z_min - standoff
    
    for x_pos in [-14.0, 14.0]:
        pts_yz = [
            (y_start_outer, z_bed),
            (y_start_outer, z_start_outer),
            (y_end_outer, z_end_outer),
            (y_end_outer, z_bed)
        ]
        poly_yz = Polygon(pts_yz)
        if poly_yz.is_valid and poly_yz.area > 0.1:
            m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
            v = m_fin_raw.vertices.copy()
            v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
            m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
            fin_components.append(m_fin)
            
            # Horizontal breakaway tines
            y_tine_stations = np.arange(y_start_outer + 2.0, y_end_outer - 1.0, tine_pitch)
            for yt in y_tine_stations:
                zt_underside = yt - z_min
                tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.05])
                fin_components.append(tine)
    
    # --- Center Fin (X = 0.0mm): catches mid-plane wall/floor overhangs ---
    y_start_center = -3.00
    y_end_center = 10.00
    z_start_center = y_start_center - z_min - standoff
    z_end_center = y_end_center - z_min - standoff
    
    pts_yz_center = [
        (y_start_center, z_bed),
        (y_start_center, z_start_center),
        (y_end_center, z_end_center),
        (y_end_center, z_bed)
    ]
    poly_yz_center = Polygon(pts_yz_center)
    if poly_yz_center.is_valid and poly_yz_center.area > 0.1:
        m_fin_raw = trimesh.creation.extrude_polygon(poly_yz_center, height=fin_thick_x)
        v = m_fin_raw.vertices.copy()
        v_reorient = np.column_stack([v[:, 2] + 0.0 - fin_thick_x/2.0, v[:, 0], v[:, 1]])
        m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
        fin_components.append(m_fin)
        
        # Horizontal breakaway tines for center fin
        y_tine_stations = np.arange(y_start_center + 2.0, y_end_center - 1.0, tine_pitch)
        for yt in y_tine_stations:
            zt_underside = yt - z_min
            tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
            tine.apply_translation([0.0, yt, zt_underside - standoff/2.0 + 0.05])
            fin_components.append(tine)
                
    # 3. Sway Braces for Lateral Stability (at X = -22.20mm and X = +21.32mm)
    # Left sway wall
    sway_l = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_l.apply_translation([-22.20, -1.0, 9.30])
    fin_components.append(sway_l)
    for z_t in [10.0, 14.0, 17.5]:
        tine_l = trimesh.creation.box([2.00, 0.60, 0.28])
        tine_l.apply_translation([-21.70, -1.0, z_t])
        fin_components.append(tine_l)
        
    # Right sway wall
    sway_r = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_r.apply_translation([21.32, -1.0, 9.30])
    fin_components.append(sway_r)
    for z_t in [10.0, 14.0, 17.5]:
        tine_r = trimesh.creation.box([2.00, 0.60, 0.28])
        tine_r.apply_translation([20.82, -1.0, z_t])
        fin_components.append(tine_r)

    all_fins = trimesh.util.concatenate(fin_components)
    try:
        fin_bodies = all_fins.split(only_watertight=False)
        fixed_fins = []
        for b in fin_bodies:
            if abs(b.volume) > 0.001:
                if b.volume < 0:
                    b.faces = np.fliplr(b.faces)
                fixed_fins.append(b)
        fins_solid = trimesh.boolean.union(fixed_fins, engine='manifold')
        combined = trimesh.boolean.union([m_tilted, fins_solid], engine='manifold')
        # Filter any micro-slivers from boolean intersection
        bodies = combined.split(only_watertight=False)
        main_bodies = [b for b in bodies if abs(b.volume) > 0.01]
        if len(main_bodies) == 1:
            combined = main_bodies[0]
        elif len(main_bodies) > 1:
            combined = trimesh.boolean.union(main_bodies, engine='manifold')
    except Exception:
        combined = trimesh.util.concatenate([m_tilted, all_fins])
        
    if include_pip_shaft:
        try:
            from build_shaft import build_shaft_rocker_mesh
            shaft_mesh = build_shaft_rocker_mesh(hub_w=7.20, in_assembly_coords=True, with_supports=False)
            shaft_tilted = shaft_mesh.copy().apply_transform(R)
            shaft_tilted.apply_translation([0, 0, -z_min])
            combined = trimesh.util.concatenate([combined, shaft_tilted])
        except Exception as e:
            print(f"Warning: could not add PIP shaft to 45° model: {e}")
            
    return combined, m_tilted, all_fins

# ==============================================================================
# RENDER PLOTS & EXPORT OPENSCAD
# ==============================================================================
def render_plots(mesh, base_poly):
    fig = plt.figure(figsize=(22, 7.5), dpi=150)
    
    # 1. 2D Top View with backside features
    ax1 = fig.add_subplot(1, 3, 1)
    if base_poly.geom_type == 'Polygon':
        x, y = base_poly.exterior.xy
        ax1.plot(x, y, color='#1f77b4', linewidth=2.5, label='Outer Perimeter Wall (6.77mm)')
        for interior in base_poly.interiors:
            ix, iy = interior.xy
            ax1.plot(ix, iy, color='#d62728', linewidth=1.5)
            
    # Arch wall (6.77mm)
    arch_poly = create_arch_wall_poly()
    ax1.plot(*arch_poly.exterior.xy, color='#1f77b4', linewidth=1.8)
    
    # Brackets
    brackets_poly = create_all_brackets_poly()
    for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
        bx, by = geom.exterior.xy
        ax1.plot(bx, by, color='#2ca02c', linewidth=1.5)
        
    # Bracket Seating Ribs (1.15mm tall)
    seating_ribs_poly = create_bracket_seating_ribs_poly()
    for geom in (seating_ribs_poly.geoms if hasattr(seating_ribs_poly, 'geoms') else [seating_ribs_poly]):
        sx, sy = geom.exterior.xy
        ax1.fill(sx, sy, color='#d32f2f', alpha=0.85, label='1.15mm Seating Ribs' if min(sy) < -4.0 else "")
        ax1.plot(sx, sy, color='#b71c1c', linewidth=1.0)
        
    # Center Curved Feature (10.5mm tall)
    c_feat_poly = create_center_curved_feature_poly()
    for geom in (c_feat_poly.geoms if hasattr(c_feat_poly, 'geoms') else [c_feat_poly]):
        cx, cy = geom.exterior.xy
        ax1.fill(cx, cy, color='#ab47bc', alpha=0.5, label='Center Curved Feature (10.5mm)')
        ax1.plot(cx, cy, color='#8e24aa', linewidth=1.5)
        for interior in geom.interiors:
            ix, iy = interior.xy
            ax1.plot(ix, iy, color='#8e24aa', linewidth=1.2)
        
    # Ribs
    ribs_poly = create_grid_ribs_poly(base_poly)
    for geom in (ribs_poly.geoms if hasattr(ribs_poly, 'geoms') else [ribs_poly]):
        rx, ry = geom.exterior.xy
        ax1.plot(rx, ry, color='#ff7f0e', linewidth=0.8, alpha=0.7)
        
    # Shaft Support Towers (magenta)
    towers_poly = create_shaft_support_towers_poly()
    for geom in (towers_poly.geoms if hasattr(towers_poly, 'geoms') else [towers_poly]):
        tx, ty = geom.exterior.xy
        ax1.fill(tx, ty, color='#e377c2', alpha=0.85, label='Shaft Supports (12.59mm)' if tx[0] < 5 else "")
        ax1.plot(tx, ty, color='#c51b7d', linewidth=1.5)
        
    # Backside slit boss walls (dashed purple)
    bosses_poly = create_backside_slit_bosses_poly()
    for geom in (bosses_poly.geoms if hasattr(bosses_poly, 'geoms') else [bosses_poly]):
        bx, by = geom.exterior.xy
        ax1.plot(bx, by, color='#9467bd', linestyle='--', linewidth=1.8, label='Backside Slit Walls (2.47mm)' if bx[0] < 0 else "")
        
    ax1.set_title('Top-Down 2D Profile (Vector Geometry)', fontsize=11, fontweight='bold')
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='upper right', fontsize=7.5)

    # 2. 3D Isometric View (Top Side)
    ax2 = fig.add_subplot(1, 3, 2, projection='3d')
    vertices = mesh.vertices
    faces = mesh.faces
    
    mesh_collection = Poly3DCollection(vertices[faces], alpha=0.75, edgecolor='#333333', linewidths=0.2)
    mesh_collection.set_facecolor('#4A90E2')
    ax2.add_collection3d(mesh_collection)
    
    ax2.set_xlim(-24, 24)
    ax2.set_ylim(-24, 24)
    ax2.set_zlim(-4, 16)
    ax2.view_init(elev=25, azim=215)
    ax2.set_title(f'3D Isometric (Top Side - Towers: {TOWER_HEIGHT}mm)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_zlabel('Z (mm)')

    # 3. 3D Isometric View (Bottom / Back Side showing 2.47mm Slit Walls)
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    mesh_collection_back = Poly3DCollection(vertices[faces], alpha=0.85, edgecolor='#333333', linewidths=0.2)
    mesh_collection_back.set_facecolor('#50E3C2')
    ax3.add_collection3d(mesh_collection_back)
    
    ax3.set_xlim(-24, 24)
    ax3.set_ylim(-24, 24)
    ax3.set_zlim(-4, 16)
    ax3.view_init(elev=-45, azim=225)
    ax3.set_title('3D Isometric (Back Side - Slit Walls: 2.47mm)', fontsize=11, fontweight='bold')
    ax3.set_xlabel('X (mm)')
    ax3.set_ylabel('Y (mm)')
    ax3.set_zlabel('Z (mm)')
    
    plt.tight_layout()
    plt.savefig('part_preview.png', dpi=200)
    print("Saved updated part_preview.png")

def export_openscad_exact(base_poly):
    """Write exact polygon points into part.scad so OpenSCAD model is 100% faithful."""
    ext_coords = list(base_poly.exterior.coords)
    poly_pts_str = ",\n    ".join([f"[{x:.4f}, {y:.4f}]" for x, y in ext_coords])
    
    scad_content = f"""/*
 * Parametric 3D Replacement Part - EXACT SVG Vector Geometry
 * Dimensions in Millimeters (mm)
 */

$fn = 100;

// Dimensions
base_thickness      = {BASE_THICK};
outer_wall_height   = {OUTER_WALL_HEIGHT};
outer_wall_thick    = {OUTER_WALL_THICK};
rib_height          = {RIB_HEIGHT};
rib_thick           = {RIB_THICK};
rib_grid_x          = {RIB_GRID_X};
rib_grid_y          = {RIB_GRID_Y};
bracket_h           = {BRACKET_HEIGHT};
bracket_seating_rib_h = {BRACKET_SEATING_RIB_HEIGHT};
bracket_seating_rib_ext = {BRACKET_SEATING_RIB_EXT};
clip_height         = {CLIP_HEIGHT};
clip_gap_depth      = {CLIP_GAP_DEPTH};
clip_arm_thick      = {CLIP_ARM_THICK};
clip_arm_width      = {CLIP_ARM_WIDTH};
clip_slot_clearance = {CLIP_SLOT_CLEARANCE};
clip_hook_depth     = {CLIP_HOOK_DEPTH};
clip_hook_height    = {CLIP_HOOK_HEIGHT};
slit_boss_height    = {SLIT_BOSS_HEIGHT};
slit_boss_wall      = {SLIT_BOSS_WALL};

// Exact non-circular perimeter points from SVG
svg_perimeter_pts = [
    {poly_pts_str}
];

module base_perimeter_2d() {{
    polygon(points = svg_perimeter_pts);
}}

module base_plate_2d() {{
    difference() {{
        base_perimeter_2d();
        
        // Top-Right rectangular hole
        translate([10.28 - 5.35/2, 10.83 - 4.51/2])
            square([5.35, 4.51]);
            
        // Left Slit Hole (X = -7.853mm, 1.20 x 3.40mm)
        translate([{-7.853 - SLIT_W_X/2:.3f}, {-13.589 - SLIT_LEN_Y/2:.3f}])
            square([{SLIT_W_X:.3f}, {SLIT_LEN_Y:.3f}]);
            
        // Right Slit Hole (X = +8.453mm, 1.20 x 3.40mm)
        translate([{8.453 - SLIT_W_X/2:.3f}, {-13.589 - SLIT_LEN_Y/2:.3f}])
            square([{SLIT_W_X:.3f}, {SLIT_LEN_Y:.3f}]);
    }}
}}

module bracket_seating_ribs_2d() {{
    // Left Pair (all 4 stations)
    for (y = [{", ".join(f"{y:.2f}" for y in BRACKET_SEATING_RIB_Y)}]) {{
        translate([{-9.857:.3f}, y - {BRACKET_SEATING_RIB_THICK}/2])
            square([{BRACKET_SEATING_RIB_EXT}, {BRACKET_SEATING_RIB_THICK}]);
        translate([{-2.701 - BRACKET_SEATING_RIB_EXT:.3f}, y - {BRACKET_SEATING_RIB_THICK}/2])
            square([{BRACKET_SEATING_RIB_EXT}, {BRACKET_SEATING_RIB_THICK}]);
    }}
    // Right Pair (top 3 stations separate)
    for (y = [{", ".join(f"{y:.2f}" for y in BRACKET_SEATING_RIB_Y[:3])}]) {{
        translate([{2.701:.3f}, y - {BRACKET_SEATING_RIB_THICK}/2])
            square([{BRACKET_SEATING_RIB_EXT}, {BRACKET_SEATING_RIB_THICK}]);
        translate([{9.857 - BRACKET_SEATING_RIB_EXT:.3f}, y - {BRACKET_SEATING_RIB_THICK}/2])
            square([{BRACKET_SEATING_RIB_EXT}, {BRACKET_SEATING_RIB_THICK}]);
    }}
    // One Pair Below Half Moon (extends all the way across and fuses with half moon base at Y = -4.30)
    translate([{2.701:.3f}, {-4.950:.3f}])
        square([{9.857 - 2.701:.3f}, {0.650:.3f}]);
}}

module complete_part() {{
    union() {{
        // Base plate
        linear_extrude(height = base_thickness)
            base_plate_2d();
            
        // 100% UNTOUCHED Outer Wall with constant thickness following exact perimeter
        difference() {{
            linear_extrude(height = outer_wall_height)
                base_plate_2d();
            translate([0, 0, base_thickness])
                linear_extrude(height = outer_wall_height + 1)
                    offset(r = -outer_wall_thick)
                        base_plate_2d();
        }}
        
        // Bracket Seating Ribs (1.15mm tall on 1.0mm base)
        translate([0, 0, base_thickness])
            linear_extrude(height = bracket_seating_rib_h)
                bracket_seating_ribs_2d();
    }}
}}

complete_part();
"""
    with open('part.scad', 'w') as f:
        f.write(scad_content)
    print("Exported exact geometry to part.scad!")

if __name__ == '__main__':
    print("Building 3D Mesh with EXACT SVG non-circular geometry...")
    part_mesh_flat, base_poly = build_exact_3d_model()
    
    print("Building 45° Tilted Main Part with Baked-In Support Fins (Slant3D / Support Fins spec)...")
    part_mesh_45, _, _ = build_45deg_supported_part_mesh(part_mesh_flat, base_poly)
    
    # Primary production deliverables: 45° Tilted Main Part with Baked-In Support Fins
    part_mesh_45.export('part.stl')
    part_mesh_45.export('part.obj')
    print("Exported part.stl and part.obj successfully! (45° Tilted with Baked-In Support Fins)")
    
    print("Building separate 3D-printable slit insert mesh with indexing key...")
    insert_mesh = build_slit_insert_mesh()
    insert_mesh.export('slit_insert.stl')
    insert_mesh.export('slit_insert.obj')
    print("Exported slit_insert.stl and slit_insert.obj successfully!")
    
    # Export pair of inserts (Left + Right polarized) for single build-plate 3D printing
    ins_left_print = build_slit_insert_mesh(is_right=False)
    ins_left_print.apply_translation([-4.0, 0, 0])
    ins_right_print = build_slit_insert_mesh(is_right=True)
    ins_right_print.apply_translation([4.0, 0, 0])
    pair_mesh = trimesh.util.concatenate([ins_left_print, ins_right_print])
    pair_mesh.export('slit_inserts_pair.stl')
    print("Exported slit_inserts_pair.stl successfully!")
    
    # Export shaft rocker models
    print("Building separate 3D-printable shaft/rocker mechanism...")
    try:
        from build_shaft import build_shaft_rocker_mesh
        shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)
        shaft_assembled.export('shaft_rocker_assembled.stl')
        shaft_assembled.export('shaft_rocker_assembled.obj')
        
        shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
        shaft_printable.export('shaft_rocker.stl')
        shaft_printable.export('shaft_rocker.obj')
        print("Exported shaft_rocker.stl and shaft_rocker_assembled.stl successfully!")
    except Exception as e:
        print(f"Warning: could not generate shaft rocker: {e}")
        shaft_printable = None
    
    part_mesh_flat.export('part_flat.stl')
    
    # Export complete assembled model with 45° tilted supported main part (includes captive PIP lever)
    assembly_mesh = build_indexed_assembly_mesh(part_mesh_45, insert_mesh, shaft_mesh=None, include_cooling_tower=False)
    assembly_mesh.export('complete_assembly.stl')
    assembly_mesh.export('complete_assembly.obj')
    print("Exported complete_assembly.stl successfully! (45° Supported PIP Main Part + Slit Inserts on Z=0.00mm)")
    
    render_plots(part_mesh_flat, base_poly)
    export_openscad_exact(base_poly)
    print("All tasks complete!")
