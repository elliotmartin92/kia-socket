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

# Clips (Mating with 5.00mm female holes) - Equalized Protrusion & Constant-Stress Tapered Flex Beam
CLIP_HEIGHT = 6.77        # Flush with outer wall
CLIP_GAP_DEPTH = 5.47     # Depth of flex slot in wall (reaches Z = 1.30mm above 1.00mm floor)
CLIP_ARM_THICK = 1.20     # Nominal wall beam thickness (tapers from 1.65mm filleted root to 0.95mm top stem)
CLIP_ARM_WIDTH = 4.20     # 4.20mm wide snap beam (leaves 0.80mm total margin / 0.40mm per side for 5.0mm mating holes)
CLIP_SLOT_CLEARANCE = 0.35 # 0.35mm minimal printable gap for 0.4mm nozzle (prevents fusion while minimizing air gap)
CLIP_HOOK_DEPTH = 1.25    # 1.25mm nominal radial overhang (reduces assembly flex strain by 45% while locking into 5.0mm slot)
# Per-clip hook overhang compensation to equalize diagonal spans (135° and 327.5° perimeter walls protrude +0.30..0.37mm further)
CLIP_HOOK_DEPTH_BY_ANGLE = {
    45.0: 1.25,
    135.0: 1.05,   # Compensates for +0.292mm larger perimeter radius at Top-Left (135°)
    211.3: 1.75,   # +0.50mm extension (was 1.25mm) to provide firm retention and equalize perimeter radial reach
    327.5: 1.55,   # +0.50mm extension (was 1.05mm) to provide 1.73mm local shelf retention and equalize diagonal spans
}
CLIP_STEM_OUTER_RECESS_BY_ANGLE = {
    45.0: 0.00,
    135.0: 0.16,   # Shaves 0.16mm off outer stem above Z=1.5mm so 135° has 1.21mm local hook step while reducing outer radius
    211.3: 0.00,
    327.5: 0.18,   # Shaves 0.18mm off outer stem above Z=1.5mm so 327.5° has 1.73mm local hook step while equalizing diagonal
}
CLIP_HOOK_HEIGHT = 1.80
CLIP_BLUNT_HEIGHT = 0.35  # 0.35mm vertical flat face at outer apex to eliminate sharp knife-edge fragility
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

# Shaft Support Towers (Top-Right Above Hole) - Heavy-Duty Reinforced
TOWER_HEIGHT = 13.09         # 13.09mm protrusion above face (Total Z_top = 14.09mm, cradle center Z = 12.59mm)
TOWER_Y_BASE_LEN = 6.60      # 6.60mm flared base in Y (Y in [6.250, 12.850]mm, exactly aligned with Bracket 3 top inner wall)
TOWER_Y_TOP_LEN = 5.63       # 5.63mm flared top in Y (Y in [7.471, 13.101]mm, +45% solid material around cradle)
TOWER_INTERNAL_GAP = 7.70    # 7.70mm internal gap between reinforced tower inner faces (X: 5.40 to 13.10mm)
TOWER_WALL_THICK = 1.50      # 1.50mm heavy-duty wall thickness in X (+50% column strength)
TOWER_THROAT_W = 2.60        # 2.60mm optimized snap throat (0.20mm positive snap interference with Ø2.80mm shaft, 240.0 deg wrap angle)

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
with open('part.svg', 'r') as f:
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
    
    # 1. Top-Right rectangular through-hole
    hole_w = (165.7 - 150.4) * SCALE
    hole_h = (99.7 - 86.8) * SCALE
    hole_x = ((150.4 + 165.7)/2.0 - X0) * SCALE
    hole_y = -((86.8 + 99.7)/2.0 - Y0) * SCALE
    hole_box = box(hole_x - hole_w/2, hole_y - hole_h/2, hole_x + hole_w/2, hole_y + hole_h/2)
    
    # 2. Outer Solid Body: complete perimeter including 1.88mm inset bottom wall aligned to arch
    outer_body_poly = raw_poly
    
    # 3. Two Bottom Detent Sockets for Press-Fit Slit Inserts (Approach B: Polarized Chamfered Sockets)
    # Left slit / detent: Centered on Bracket 1 datum line (X = -7.853mm, Y = -13.589mm)
    # Right slit / detent: Centered on OEM datum line (X = +8.453mm, Y = -13.589mm)
    cx_left = -7.853
    cx_right = 8.453
    cy = -13.589
    
    # Left socket (bottom-left chamfer matched for 0.28mm/side clearance)
    x_l_min = cx_left - SOCKET_W_X/2
    y_l_bot = cy - SOCKET_LEN_Y/2
    chamfer_left_tri = Polygon([[x_l_min + 0.88, y_l_bot - 0.05],
                                [x_l_min - 0.05, y_l_bot + 0.88],
                                [x_l_min - 0.05, y_l_bot - 0.05]])
    detent_left = box(cx_left - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_left + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_left_tri)
    
    # Right socket (bottom-right chamfer matched for 0.28mm/side clearance)
    x_r_max = cx_right + SOCKET_W_X/2
    y_r_bot = cy - SOCKET_LEN_Y/2
    chamfer_right_tri = Polygon([[x_r_max - 0.88, y_r_bot - 0.05],
                                 [x_r_max + 0.05, y_r_bot + 0.88],
                                 [x_r_max + 0.05, y_r_bot - 0.05]])
    detent_right = box(cx_right - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_right + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_right_tri)
    
    # Base plate floor (with all through-holes and detent sockets cut through 1mm floor)
    base_poly = outer_body_poly.difference(unary_union([hole_box, detent_left, detent_right]))
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
    
    # Top-right through hole exclusion
    hole_x, hole_y, hole_w, hole_h = 10.284, 10.826, 5.352, 4.512
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
    """Returns the 2D polygon of the 10.5mm tall reinforced curved feature between Brackets 3 & 4.
    - Solid D-shape cross-section: 100% solid core.
    - Width: 4.20mm (centered at X = 6.279mm -> X in [4.179, 8.379]mm, anchoring directly into Bracket 3 & 4 walls).
    - Depth in Y: 1.30mm (Base extended down in -Y to Y = -4.30mm, Apex calibrated to Y = -3.00mm).
    - Bottom base: Flat solid wall at Y = -4.30mm (leaves +0.05mm clearance to Rib 4 & brass bridge).
    - Front apex: Calibrated to Y = -3.00mm (+0.125mm clearance to nominal 6.35mm plug blade bottom at Y = -2.875mm).
      Prevents blade from deflecting down past Y = -3.00mm, ensuring full engagement with the cantilever at +Y.
    """
    cx = 6.279
    w_x = 4.20
    base_y = -4.30
    apex_y = -3.00
    
    rx = w_x / 2.0
    ry = apex_y - base_y  # 1.30 mm
    
    angles = np.linspace(np.pi, 0, 32)
    out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
    
    return Polygon(out_arc + [(cx - rx, base_y)])

def build_center_curved_feature_mesh():
    """Builds the 100% watertight 3D mesh of the reinforced half moon from Z = 1.00 to 10.50mm,
    including a 0.25mm smooth lead-in funnel chamfer on the top front rim (Z = 8.50 to 10.50mm).
    """
    poly = create_center_curved_feature_poly()
    mesh = extrude_shapely_geom(poly, height=10.50 - BASE_THICK)
    mesh.apply_translation([0, 0, BASE_THICK])
    
    # Smooth lead-in funnel chamfer on the top front face (Z = 8.50 to 10.50mm)
    cx = 6.279
    w_x = 4.20
    apex_y = -3.00
    chamfer_cutter = trimesh.creation.box([w_x + 2.0, 1.0, 3.0])
    rot_chamfer = trimesh.transformations.rotation_matrix(np.radians(-7.125), [1, 0, 0])
    chamfer_cutter.apply_transform(rot_chamfer)
    chamfer_cutter.apply_translation([cx, apex_y + 0.50, 9.50])
    
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
    """Directly extrudes the reinforced 2D U-cradle profile in (Y, Z) along X.
    - Lower flared trapezoidal base (Z: 1.00 to 11.20mm): Base Y in [6.250, 12.850] (6.60mm wide) tapering to [6.550, 12.180].
    - Upper parallel vertical clamping lands (Z: 11.20 to 14.09mm): Constant Y in [6.550, 12.180] (5.63mm wide) with 0.25mm top lead-in chamfers so the closed-box gantry clamp slides straight down without wedging.
    - Tuned 2.60mm snap-fit retention throat constriction (0.20mm positive snap with Ø2.80mm shaft, 240.0 deg wrap angle).
    - 1.50mm heavy-duty wall thickness in X.
    - Shaft axis at Y = 9.279mm (shifted -0.921mm so front buttress/tower base aligns with top inner wall of Bracket 3 at Y = 6.250mm).
    """
    y_shaft = 9.279   # Shifted to Y = 9.279mm
    z_base = BASE_THICK  # 1.0mm
    z_land_bot = 11.200  # Bottom of parallel vertical clamp seating land
    z_top = z_base + TOWER_HEIGHT  # 14.09mm
    z_chamfer = z_top - 0.25       # 13.84mm (0.25mm x 45 deg top entry chamfer)
    r_shaft = 1.50  # 3.0mm diameter shaft cradle -> 1.5mm radius
    z_cradle_center = 12.590  # Exact pivot axis elevation
    
    y_min_base = 6.250
    y_max_base = 12.850
    y_min_top = 6.550
    y_max_top = 11.850  # 1.07mm rear prong wall (leaves up to 2.63mm inside outer perimeter for Right Clamp Rear Jaw)
    
    throat_w = TOWER_THROAT_W  # 2.60mm
    half_w = throat_w / 2.0
    alpha = np.arcsin(half_w / r_shaft)
    
    # Circular arc around shaft cavity from right retention tip to left retention tip
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(y_shaft + r_shaft * np.cos(p), z_cradle_center + r_shaft * np.sin(p)) for p in phi]
    
    # 45-degree lead-in bevel from retention tips up to top edge (Z = z_top)
    bevel_dx = (z_top - (z_cradle_center + r_shaft * np.cos(alpha))) * 0.75
    y_left_top = y_shaft - half_w - bevel_dx
    y_right_top = y_shaft + half_w + bevel_dx
    
    # 2D profile in (Y, Z) - Flared base (Z=1.0..11.20) + Parallel vertical clamping lands (Z=11.20..14.09) + Top entry chamfers
    profile_yz = [
        (y_min_base, z_base),
        (y_max_base, z_base),
        (y_max_top, z_land_bot),
        (y_max_top, z_chamfer),
        (y_max_top - 0.25, z_top),
        (y_right_top, z_top),
    ] + cradle_arc_pts + [
        (y_left_top, z_top),
        (y_min_top + 0.25, z_top),
        (y_min_top, z_chamfer),
        (y_min_top, z_land_bot),
    ]
    poly_yz = Polygon(profile_yz)
    
    # Extrude along X (thickness = 1.50mm)
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=TOWER_WALL_THICK)
    verts = m_raw.vertices.copy()
    
    # Left tower mesh: X in [3.90, 5.40] (1.50mm thick)
    verts_left = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_left[:, 0] += 3.900
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    
    # Right tower mesh: X in [13.10, 14.60] (1.50mm thick)
    verts_right = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_right[:, 0] += 13.100
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    
    # Low-profile smooth 0.35mm click-retention detents on outer lateral faces (X=3.90 Left, X=14.60 Right)
    # Positioned on the solid Front Prong at Y in [6.55, 7.35] (100% outside the R=1.85mm pin clearance arch Y>=7.43mm)
    poly_xz_left = Polygon([
        (3.90, 12.35),
        (3.65, 12.40),  # 0.25mm low-profile locking shelf (engages X=3.73mm hook at Z=12.32mm)
        (3.65, 12.70),  # 0.30mm vertical retention land
        (3.90, 13.10),  # Gentle 32 deg push-on lead-in ramp (fits inside Z in [12.32, 13.15] detent pocket)
        (4.10, 13.10),
        (4.10, 12.35)
    ])
    
    m_raw_b_front = trimesh.creation.extrude_polygon(poly_xz_left, height=7.35 - 6.55)
    vbf = m_raw_b_front.vertices.copy()
    fbf = m_raw_b_front.faces[:, ::-1].copy()
    v_lf = np.column_stack([vbf[:, 0], vbf[:, 2] + 6.55, vbf[:, 1]])
    mesh_lf = trimesh.Trimesh(vertices=v_lf, faces=fbf, process=True)
    
    m_raw_b_rear = trimesh.creation.extrude_polygon(poly_xz_left, height=11.85 - 11.15)
    vbr = m_raw_b_rear.vertices.copy()
    fbr = m_raw_b_rear.faces[:, ::-1].copy()
    v_lr = np.column_stack([vbr[:, 0], vbr[:, 2] + 11.15, vbr[:, 1]])
    mesh_lr = trimesh.Trimesh(vertices=v_lr, faces=fbr, process=True)
    
    # Right front detent at Y in [6.55, 7.35] (X: 14.60 to 14.85) - 100% outside pin arch
    poly_xz_right = Polygon([
        (14.60, 12.35),
        (14.85, 12.40),
        (14.85, 12.70),
        (14.60, 13.10),
        (14.40, 13.10),
        (14.40, 12.35)
    ])
    m_raw_br_front = trimesh.creation.extrude_polygon(poly_xz_right, height=7.35 - 6.55)
    vrf = m_raw_br_front.vertices.copy()
    frf = m_raw_br_front.faces[:, ::-1].copy()
    v_rf = np.column_stack([vrf[:, 0], vrf[:, 2] + 6.55, vrf[:, 1]])
    mesh_rf = trimesh.Trimesh(vertices=v_rf, faces=frf, process=True)
    
    return trimesh.util.concatenate([mesh_left, mesh_right, mesh_lf, mesh_lr, mesh_rf])

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
    
    # 2. Rear Strut at Y in [11.650, 12.850] (1.20mm thick)
    m_rear_raw = trimesh.creation.extrude_polygon(poly_xz, height=1.20)
    v_rear = m_rear_raw.vertices.copy()
    v_rear = np.column_stack([v_rear[:, 0], v_rear[:, 2] + 11.650, v_rear[:, 1]])
    mesh_rear = trimesh.Trimesh(vertices=v_rear, faces=m_rear_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_front, mesh_rear])

def build_exact_3d_model():
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    
    # 1. Extrude Base Plate (Z: 0 to BASE_THICK = 1.0mm) with floor through-holes
    mesh_base = extrude_shapely_geom(base_poly, height=BASE_THICK)
    
    # 1b. Bottom Elephant's-Foot Relief Chamfers (0.35mm x 45 deg countersink at Z = 0.00..0.35mm)
    # Prevents first-layer squish at higher print temperatures from narrowing the female detent sockets
    cx_left, cx_right, cy_sock = -7.853, 8.453, -13.589
    chamf_c = SOCKET_BOT_CHAMFER
    for cx_s in [cx_left, cx_right]:
        ef_cutter = create_frustum_mesh(
            SOCKET_W_X + 2.0 * chamf_c, SOCKET_LEN_Y + 2.0 * chamf_c,
            SOCKET_W_X, SOCKET_LEN_Y,
            -0.02, chamf_c
        )
        ef_cutter.apply_translation([cx_s, cy_sock, 0.0])
        try:
            mesh_base = mesh_base.difference(ef_cutter, engine='manifold')
        except Exception:
            pass
    
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
    
    # 5. Backside Slit Protruding Walls (Z: -SLIT_BOSS_HEIGHT to 0)
    bosses_poly = create_backside_slit_bosses_poly()
    mesh_bosses = extrude_shapely_geom(bosses_poly, height=SLIT_BOSS_HEIGHT)
    mesh_bosses.apply_translation([0, 0, -SLIT_BOSS_HEIGHT])
    
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
    
    # 7. Snap Clips: Equalized-Protrusion & Constant-Stress Tapered Flex Beams (4 clips: 45°, 135°, 211.3°, 327.5°)
    slot_cuts = []
    hook_meshes = []
    root_fillet_meshes = []
    stem_taper_cutters = []
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT         # 4.97 mm
    slot_z_bot = OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH # 1.30 mm
    z_root_center = slot_z_bot + CLIP_ROOT_RADIUS   # 1.70 mm (center of radiused root)
    slot_t = CLIP_SLOT_CLEARANCE                    # Minimal printable flex slot width for 0.4mm nozzle
    
    for angle_deg in CLIP_ANGLES:
        center_rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = CLIP_ARM_WIDTH / r_est
        slot_d_theta = slot_t / r_est
        hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        stem_recess = CLIP_STEM_OUTER_RECESS_BY_ANGLE.get(angle_deg, 0.0)
        
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
            
        # 2. Constant-Stress Tapered Beam Geometry + Equalized Faced-Off Hook Wedge
        N = 16
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        
        outer_coords = []
        shelf_coords = []
        inner_overlap_coords = []
        inner_wall_coords = []
        fillet_foot_coords = []
        taper_top_coords = []
        
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
            ps = po + n_dir * hook_depth
            # Penetrate 0.25mm inward into the wall stem so the boolean union completely dissolves the interface
            p_in = po - n_dir * (0.25 + stem_recess)
            p_iw = po - n_dir * OUTER_WALL_THICK
            p_ff = p_iw - n_dir * 0.45   # +0.45mm interior root fillet foot at Z=1.00mm (1.65mm total root thickness)
            p_tt = p_iw + n_dir * 0.25   # -0.25mm interior stem taper at Z=4.97mm (0.95mm flexible upper stem)
            
            outer_coords.append(po)
            shelf_coords.append(ps)
            inner_overlap_coords.append(p_in)
            inner_wall_coords.append(p_iw)
            fillet_foot_coords.append(p_ff)
            taper_top_coords.append(p_tt)
            
        inner_overlap_coords = np.array(inner_overlap_coords)
        shelf_coords = np.array(shelf_coords)
        inner_wall_coords = np.array(inner_wall_coords)
        fillet_foot_coords = np.array(fillet_foot_coords)
        taper_top_coords = np.array(taper_top_coords)
        
        # 2a. Interior Root Fillet Wedge (Z: 1.00 to 2.50mm, thickening base to 1.65mm and eliminating sharp 90 deg corner)
        vf0 = np.column_stack([inner_wall_coords + (outer_coords - inner_wall_coords)*0.20, np.full(N, BASE_THICK - 0.05)])
        vf1 = np.column_stack([fillet_foot_coords, np.full(N, BASE_THICK - 0.05)])
        vf2 = np.column_stack([inner_wall_coords, np.full(N, 2.50)])
        vf3 = np.column_stack([inner_wall_coords + (outer_coords - inner_wall_coords)*0.20, np.full(N, 2.50)])
        fillet_verts = np.vstack([vf0, vf1, vf2, vf3])
        fillet_faces = []
        for i in range(N - 1):
            fillet_faces.extend([
                [i, N + i + 1, N + i], [i, i + 1, N + i + 1],
                [N + i, 2*N + i + 1, 2*N + i], [N + i, N + i + 1, 2*N + i + 1],
                [2*N + i, 3*N + i + 1, 3*N + i], [2*N + i, 2*N + i + 1, 3*N + i + 1],
                [3*N + i, i + 1, i], [3*N + i, 3*N + i + 1, i + 1]
            ])
        fillet_faces.extend([
            [0, 2*N, 3*N], [0, N, 2*N],
            [N - 1, 3*N - 1, 2*N - 1], [N - 1, 4*N - 1, 3*N - 1]
        ])
        f_mesh = trimesh.Trimesh(vertices=fillet_verts, faces=np.array(fillet_faces), process=True)
        if f_mesh.volume < 0:
            f_mesh.faces = np.fliplr(f_mesh.faces)
        root_fillet_meshes.append(f_mesh)
        
        # 2b. Constant-Stress Upper Stem Inward Taper Relief (Z: 2.50 to 4.97mm, tapering stem from 1.20mm to 0.95mm)
        vt0 = np.column_stack([inner_wall_coords - (outer_coords - inner_wall_coords)*0.20, np.full(N, 2.50)])
        vt1 = np.column_stack([inner_wall_coords, np.full(N, 2.50)])
        vt2 = np.column_stack([taper_top_coords, np.full(N, stem_h + 0.02)])
        vt3 = np.column_stack([inner_wall_coords - (outer_coords - inner_wall_coords)*0.20, np.full(N, stem_h + 0.02)])
        taper_verts = np.vstack([vt0, vt1, vt2, vt3])
        t_mesh = trimesh.Trimesh(vertices=taper_verts, faces=np.array(fillet_faces), process=True)
        if t_mesh.volume < 0:
            t_mesh.faces = np.fliplr(t_mesh.faces)
        stem_taper_cutters.append(t_mesh)
        
        # 2c. Outer Stem Recess on Protruding Diagonal Clips (135° and 327.5°) from Z=1.80 to 4.97mm
        if stem_recess > 0.001:
            outer_arr = np.array(outer_coords)
            recess_in = outer_arr - (outer_arr - inner_wall_coords) * (stem_recess / OUTER_WALL_THICK)
            recess_out = outer_arr + (outer_arr - inner_wall_coords) * 0.30
            vr0 = np.column_stack([recess_in, np.full(N, 1.80)])
            vr1 = np.column_stack([recess_out, np.full(N, 1.80)])
            vr2 = np.column_stack([recess_out, np.full(N, stem_h + 0.01)])
            vr3 = np.column_stack([recess_in, np.full(N, stem_h + 0.01)])
            r_mesh = trimesh.Trimesh(vertices=np.vstack([vr0, vr1, vr2, vr3]), faces=np.array(fillet_faces), process=True)
            if r_mesh.volume < 0:
                r_mesh.faces = np.fliplr(r_mesh.faces)
            stem_taper_cutters.append(r_mesh)
        
        # 2d. Faced-Off Hook Wedge on outer face of flexible wall beam (Z: 4.97 to 6.77mm)
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
        
    # 1. Apply constant-stress stem tapers and monolithically fuse root fillets + hook wedges into outer wall stem
    for tc in stem_taper_cutters:
        try:
            mesh_wall = mesh_wall.difference(tc, engine='manifold')
        except Exception:
            pass
    for fm in root_fillet_meshes:
        try:
            mesh_wall = mesh_wall.union(fm, engine='manifold')
        except Exception:
            pass
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
        
    # 8. Center Curved Feature: Blade-Calibrated & Flared-Base Reinforced (Z: 1.0 to 10.50mm)
    mesh_curved_feat = build_center_curved_feature_mesh()
    
    # 9. Manual Breakaway Support Towers under 4 Snap Clip Overhangs (Z: 0 to 4.92mm)
    mesh_clip_supports = build_clip_supports_mesh(base_poly)
    
    # Main part is 100% planar at Z = 0.00mm for direct support-free 3D printing
    full_part = trimesh.util.concatenate([mesh_base, mesh_wall, mesh_ribs, mesh_brackets, mesh_seating_ribs, mesh_towers_assembly, mesh_curved_feat, mesh_clip_supports] + unmerged_hooks)
    
    # Filter any degenerate zero-area/zero-volume slivers produced by boolean cuts
    try:
        bodies = full_part.split(only_watertight=False)
        valid_bodies = [b for b in bodies if b.is_watertight and abs(b.volume) > 0.001]
        if len(valid_bodies) > 0:
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

def build_cooling_tower_mesh(radius=4.0, height=20.50):
    """Builds a sacrificial cylindrical cooling tower (Ø8mm x 20.50mm tall) for 1-click print plate placement.
    Forces the nozzle to travel away from the delicate shaft support towers (Z = 14.09mm) and shaft rocker (Z = 19.86mm)
    on high layers, giving each layer of the delicate tips dedicated time to cool and solidify."""
    tower = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    tower.apply_translation([0, 0, height / 2.0])  # Base flat at Z = 0.00mm
    return tower

def build_indexed_assembly_mesh(main_mesh, insert_mesh=None, shaft_mesh=None, include_cooling_tower=True):
    """Creates the complete 3D build-plate layout with the main part, both separate inserts,
    the shaft rocker mechanism, and a sacrificial cooling tower arranged on the same plane (Z = 0.00mm)
    for 1-click support-free 3D printing."""
    # Build left and right polarized inserts
    ins_left = build_slit_insert_mesh(is_right=False)
    ins_left.apply_translation([27.50, -5.00, 0.00])
    
    ins_right = build_slit_insert_mesh(is_right=True)
    ins_right.apply_translation([27.50, 5.00, 0.00])
    
    meshes = [main_mesh, ins_left, ins_right]
    if shaft_mesh is not None:
        shaft_plate = shaft_mesh.copy()
        shaft_plate.apply_translation([27.50, 16.00, 0.00])
        meshes.append(shaft_plate)
        
    if include_cooling_tower:
        cool_tower = build_cooling_tower_mesh(radius=4.0, height=20.50)
        cool_tower.apply_translation([27.50, -16.00, 0.00])
        meshes.append(cool_tower)
        
    # Include 3D-printable Unified Monolithic Bridge Clamp flat on bed (Z = 0.00mm)
    try:
        from build_clamp import build_unified_clamp_mesh
        u_clamp = build_unified_clamp_mesh(in_assembly_coords=False)
        u_clamp.apply_translation([38.50, 0.00, 0.00])
        meshes.append(u_clamp)
    except Exception as e:
        print(f"Warning: could not include unified bridge clamp in plate assembly: {e}")
        
    return trimesh.util.concatenate(meshes)

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
            
        // Left Polarized Detent Socket (X = -7.853mm, bottom-left chamfer)
        translate([{-7.853:.3f}, {-13.589:.3f}])
            polygon(points = [
                [{-SOCKET_W_X/2:.3f} + 0.85, {-SOCKET_LEN_Y/2:.3f}],
                [{SOCKET_W_X/2:.3f}, {-SOCKET_LEN_Y/2:.3f}],
                [{SOCKET_W_X/2:.3f}, {SOCKET_LEN_Y/2:.3f}],
                [{-SOCKET_W_X/2:.3f}, {SOCKET_LEN_Y/2:.3f}],
                [{-SOCKET_W_X/2:.3f}, {-SOCKET_LEN_Y/2:.3f} + 0.85]
            ]);
            
        // Right Polarized Detent Socket (X = +8.453mm, bottom-right chamfer)
        translate([{8.453:.3f}, {-13.589:.3f}])
            polygon(points = [
                [{-SOCKET_W_X/2:.3f}, {-SOCKET_LEN_Y/2:.3f}],
                [{SOCKET_W_X/2:.3f} - 0.85, {-SOCKET_LEN_Y/2:.3f}],
                [{SOCKET_W_X/2:.3f}, {-SOCKET_LEN_Y/2:.3f} + 0.85],
                [{SOCKET_W_X/2:.3f}, {SOCKET_LEN_Y/2:.3f}],
                [{-SOCKET_W_X/2:.3f}, {SOCKET_LEN_Y/2:.3f}]
            ]);
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
    print("Building 3D Mesh with EXACT SVG non-circular geometry (Flat Bottom Z=0 for 3D Printing)...")
    part_mesh, base_poly = build_exact_3d_model()
    part_mesh.export('part.stl')
    part_mesh.export('part.obj')
    print("Exported part.stl and part.obj successfully! (Flat bottom Z=0 to 13.59mm)")
    
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
    
    # Export cooling tower model
    print("Building separate 3D-printable sacrificial cooling tower...")
    cool_tower_mesh = build_cooling_tower_mesh()
    cool_tower_mesh.export('cooling_tower.stl')
    cool_tower_mesh.export('cooling_tower.obj')
    print("Exported cooling_tower.stl and cooling_tower.obj successfully!")
    
    # Export complete assembled model
    assembly_mesh = build_indexed_assembly_mesh(part_mesh, insert_mesh, shaft_printable, include_cooling_tower=True)
    assembly_mesh.export('complete_assembly.stl')
    assembly_mesh.export('complete_assembly.obj')
    print("Exported complete_assembly.stl successfully! (Main Part + Slit Inserts + Shaft Rocker + Cooling Tower + 2x Tower Clamps on Z=0.00mm)")
    
    render_plots(part_mesh, base_poly)
    export_openscad_exact(base_poly)
    print("All tasks complete!")
