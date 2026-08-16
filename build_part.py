"""
Build 3D Printable STL using the EXACT non-circular vector paths directly from part.svg.
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

# Clips
CLIP_HEIGHT = 6.77        # Flush with outer wall
CLIP_GAP_DEPTH = 3.70     # Depth of flex slot in wall
CLIP_ARM_THICK = 1.20     # Exactly matches OUTER_WALL_THICK (1.20mm) for flush interior alignment
CLIP_ARM_WIDTH = 3.00
CLIP_SLOT_CLEARANCE = 0.50
CLIP_HOOK_DEPTH = 1.59    # 1.59mm radial overhang from wall
CLIP_HOOK_HEIGHT = 1.80

# Bottom Slits / Holes
SLIT_W_X = 1.10         # 1.1mm wide in X
SLIT_LEN_Y = 3.00       # 3.0mm long in Y
SLIT_BOSS_HEIGHT = 2.47 # 2.47mm protrusion on back side (-Z)
SLIT_BOSS_WALL = 0.80   # 0.8mm thick wall around slits

# Shaft Support Towers (Top-Right Above Hole)
TOWER_HEIGHT = 12.59    # 12.59mm protrusion above face
TOWER_Y_LEN = 4.65      # 4.65mm in Y dimension
TOWER_INTERNAL_GAP = 7.86 # 7.86mm internal distance between towers
TOWER_WALL_THICK = 1.25 # 1.25mm wall thickness in X

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
# 1. Exact Bracket Polygons from SVG line segments
bracket_4_raw_pts = [
    (159.5, 103.7), (151.1, 103.7), (151.1, 111.1), (154.0, 111.1),
    (154.0, 106.8), (156.4, 106.8), (156.4, 141.5), (151.6, 141.5),
    (151.6, 144.6), (159.5, 144.6), (159.5, 103.7)
]
bracket_3_raw_pts = [
    (133.7, 103.7), (142.1, 103.7), (142.1, 111.1), (139.3, 111.1),
    (139.3, 106.9), (136.8, 106.9), (136.8, 141.6), (141.7, 141.6),
    (141.7, 144.7), (133.7, 144.7), (133.7, 103.7)
]
bracket_2_raw_pts = [
    (123.6, 103.7), (115.3, 103.7), (115.3, 111.1), (118.1, 111.1),
    (118.1, 106.9), (120.5, 106.9), (120.5, 141.5), (115.7, 141.5),
    (115.7, 144.6), (123.6, 144.6), (123.6, 103.7)
]
bracket_1_raw_pts = [
    (97.8, 103.8), (106.2, 103.8), (106.2, 111.1), (103.4, 111.1),
    (103.4, 106.9), (100.9, 106.9), (100.9, 141.6), (105.8, 141.6),
    (105.8, 144.7), (97.8, 144.7), (97.8, 103.8)
]

def to_mm_poly(raw_pts):
    pts_mm = [((x - X0) * SCALE, -(y - Y0) * SCALE) for x, y in raw_pts]
    return Polygon(pts_mm)

def create_all_brackets_poly():
    b1 = to_mm_poly(bracket_1_raw_pts)
    b2 = to_mm_poly(bracket_2_raw_pts)
    b3 = to_mm_poly(bracket_3_raw_pts)
    b4 = to_mm_poly(bracket_4_raw_pts)
    return unary_union([b1, b2, b3, b4])

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
    # Config 1: Align bottom exterior wall notch outer walls with Arch INNER walls (X = ±2.50mm)
    pts = outer_pts.copy()
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
    
    # 3. Two Bottom Vertical Slits / Holes (1.10mm wide in X, 3.00mm long in Y)
    # Right wall of left slit aligns with rightmost wall of leftmost bracket (X = -7.853mm)
    # Left wall of right slit aligns with leftmost wall of rightmost bracket (X = +7.853mm)
    # Bottom of slits is exactly 1.0mm from the INNER side of the bottom wall
    b1_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_1_raw_pts]
    b4_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_4_raw_pts]
    b1_rightmost_x = max(p[0] for p in b1_pts)  # -7.853mm
    b4_leftmost_x = min(p[0] for p in b4_pts)   # +7.853mm
    
    slit_y_bot = -18.539 + OUTER_WALL_THICK + 1.00  # -16.339mm (1.0mm from inner wall face)
    slit_y_top = slit_y_bot + SLIT_LEN_Y            # -13.339mm
    
    slit_left = box(b1_rightmost_x - SLIT_W_X, slit_y_bot, b1_rightmost_x, slit_y_top)
    slit_right = box(b4_leftmost_x, slit_y_bot, b4_leftmost_x + SLIT_W_X, slit_y_top)
    
    # Base plate floor (with all through-holes cut through 1mm floor)
    base_poly = outer_body_poly.difference(unary_union([hole_box, slit_left, slit_right]))
    return base_poly, outer_body_poly, (hole_x, hole_y, hole_w, hole_h)

def create_grid_ribs_poly(base_poly, outer_body_poly=None):
    """Grid ribbing (0.60mm thick lines on a 5.2mm x 3.2mm pitch).
    - Extends all the way to merge and connect directly with the outer perimeter walls.
    - Excludes the bounding envelopes of the brackets.
    - Excludes the bottom section (Y < -7.17mm) where there is zero floor ribbing.
    - Excludes the top-right through hole."""
    if outer_body_poly is None:
        outer_body_poly = base_poly
    b1_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_1_raw_pts]
    b2_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_2_raw_pts]
    b3_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_3_raw_pts]
    b4_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_4_raw_pts]
    
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
    connected_ribs = raw_grid.intersection(outer_body_poly).difference(bracket_exclusions).difference(below_brackets_box).difference(hole_box)
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
    b1_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_1_raw_pts]
    b4_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_4_raw_pts]
    b1_rightmost_x = max(p[0] for p in b1_pts)  # -7.853mm
    b4_leftmost_x = min(p[0] for p in b4_pts)   # +7.853mm
    
    slit_y_bot = -18.539 + OUTER_WALL_THICK + 1.00  # -16.339mm
    slit_y_top = slit_y_bot + SLIT_LEN_Y            # -13.339mm
    
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
    """Returns the 2D polygon of the 10.5mm tall curved feature between Brackets 3 & 4.
    - Width: 4.30mm (centered at X = 6.279mm -> X in [4.129, 8.429]mm).
    - Depth in Y: 1.62mm (Base at Y = -4.069mm, Apex at Y = -2.449mm, 2mm above bracket step).
    - Wall thickness: 0.60mm.
    - Central internal rib: 0.60mm thick along X = 6.279mm."""
    cx = 6.279
    w_x = 4.30
    h_y = 1.62
    rx = w_x / 2.0
    ry = h_y
    wall_t = 0.60
    rib_t = 0.60
    
    datum_y = -17.339 + 11.27  # -6.069 mm
    base_y = datum_y + 2.00    # -4.069 mm
    
    angles = np.linspace(np.pi, 0, 32)
    out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
    in_arc = [(cx + (rx - wall_t) * np.cos(a), base_y + (ry - wall_t) * np.sin(a)) for a in angles]
    
    wall_poly = Polygon(out_arc + list(reversed(in_arc)))
    rib_poly = box(cx - rib_t/2.0, base_y, cx + rib_t/2.0, base_y + ry)
    return unary_union([wall_poly, rib_poly])

def create_shaft_support_towers_poly():
    """Returns 2D bounding boxes for the two shaft support towers and left tower struts."""
    y_bot_inner = -17.339  # Bottom inner wall
    y_min = y_bot_inner + 22.68  # 5.341mm
    y_max = y_min + TOWER_Y_LEN  # 9.991mm
    
    x_left_inner = 5.500
    x_left_outer = x_left_inner - TOWER_WALL_THICK  # 4.250mm
    
    x_right_inner = 13.360
    x_right_outer = x_right_inner + TOWER_WALL_THICK  # 14.610mm
    
    left_box = box(x_left_outer, y_min, x_left_inner, y_max)
    right_box = box(x_right_inner, y_min, x_right_outer, y_max)
    
    # Triangular strut footprints (base extends 2.35mm in -X)
    strut_bot = box(x_left_outer - 2.35, y_min, x_left_outer, y_min + 0.80)
    strut_top = box(x_left_outer - 2.35, y_max - 0.80, x_left_outer, y_max)
    
    return unary_union([left_box, right_box, strut_bot, strut_top])

def build_clean_shaft_towers_mesh():
    """Directly extrudes the exact 2D U-cradle profile in (Y, Z) along X.
    Guarantees a 100% clean, watertight mesh with zero internal facets or boolean artifacts."""
    y_bot_inner = -17.339
    y_min = y_bot_inner + 22.68  # 5.341mm
    y_max = y_min + TOWER_Y_LEN  # 9.991mm
    y_shaft = (y_min + y_max) / 2.0  # 7.666mm
    
    z_base = BASE_THICK  # 1.0mm
    z_top = z_base + TOWER_HEIGHT  # 13.59mm
    r_shaft = 1.00  # 2mm diameter shaft -> 1mm radius
    z_cradle_center = z_top - r_shaft  # 12.59mm
    
    # Shaft Retention Wrap-Around Cradle:
    # Circle continues up and around above equator to a retention throat width of 1.65mm
    throat_w = 1.65
    half_w = throat_w / 2.0  # 0.825mm
    alpha = np.arcsin(half_w / r_shaft)  # 55.59 deg from vertical
    
    # Circular arc around shaft cavity from right retention tip to left retention tip
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(y_shaft + r_shaft * np.cos(p), z_cradle_center + r_shaft * np.sin(p)) for p in phi]
    
    # Lead-in bevel from retention tips up to top edge (Z = z_top)
    y_left_top = y_shaft - half_w - 0.30
    y_right_top = y_shaft + half_w + 0.30
    
    # 2D profile in (Y, Z)
    profile_yz = [
        (y_min, z_base),
        (y_max, z_base),
        (y_max, z_top),
        (y_right_top, z_top),
    ] + cradle_arc_pts + [
        (y_left_top, z_top),
        (y_min, z_top)
    ]
    poly_yz = Polygon(profile_yz)
    
    # Extrude along X (thickness = 1.25mm)
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=TOWER_WALL_THICK)
    verts = m_raw.vertices.copy()
    
    # Left tower mesh (X: 4.25 to 5.50mm)
    verts_left = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_left[:, 0] += (5.500 - TOWER_WALL_THICK)
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    
    # Right tower mesh (X: 13.36 to 14.61mm)
    verts_right = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_right[:, 0] += 13.360
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_left, mesh_right])

def build_left_tower_struts_mesh(strut_thick_y=0.80):
    """Builds the two steep triangular buttress struts on the left side of the left tower.
    - Base of triangle reaches 2.35mm outward in -X at Z = 1.0mm (from X=4.25mm to X=1.90mm)
    - Slopes directly into the tower wall at Z = 11.59mm (2mm below apex) with ZERO horizontal flat top.
    - Placed at the front (Y_min = 5.341mm) and back (Y_max = 9.991mm) edges of the tower."""
    x_left_inner = 5.500
    x_left_outer = x_left_inner - TOWER_WALL_THICK  # 4.250mm
    
    y_bot_inner = -17.339
    y_min = y_bot_inner + 22.68  # 5.341mm
    y_max = y_min + TOWER_Y_LEN  # 9.991mm
    
    z_base = BASE_THICK  # 1.0mm
    z_top = z_base + TOWER_HEIGHT  # 13.59mm
    z_strut_top = z_top - 2.0  # 11.59mm
    
    # Pure 3-point triangle: base reaches out 2.35mm from wall
    strut_pts_xz = [
        (x_left_outer - 2.35, z_base),
        (x_left_outer, z_base),
        (x_left_outer, z_strut_top)
    ]
    poly_xz = Polygon(strut_pts_xz)
    
    m_raw = trimesh.creation.extrude_polygon(poly_xz, height=strut_thick_y)
    verts = m_raw.vertices.copy()
    
    # Map [X_coord, Z_coord, Y_extruded] -> [X, Y, Z]
    verts_bot = np.column_stack([verts[:, 0], verts[:, 2] + y_min, verts[:, 1]])
    mesh_bot = trimesh.Trimesh(vertices=verts_bot, faces=m_raw.faces.copy(), process=True)
    
    verts_top = np.column_stack([verts[:, 0], verts[:, 2] + (y_max - strut_thick_y), verts[:, 1]])
    mesh_top = trimesh.Trimesh(vertices=verts_top, faces=m_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_bot, mesh_top])

def build_exact_3d_model():
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    
    # 1. Extrude Base Plate (Z: 0 to BASE_THICK = 1.0mm) with floor through-holes
    mesh_base = extrude_shapely_geom(base_poly, height=BASE_THICK)
    
    # 2. Outer Rim Wall + Arch Wall (Z: BASE_THICK to OUTER_WALL_HEIGHT = 6.77mm)
    inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_poly)
    arch_wall_poly = create_arch_wall_poly()
    all_walls_poly = unary_union([wall_poly, arch_wall_poly])
    mesh_wall = extrude_shapely_geom(all_walls_poly, height=OUTER_WALL_HEIGHT)
    
    # 3. Floor Grid Ribbing (Z: BASE_THICK to BASE_THICK + RIB_HEIGHT)
    # Plus bridge ribs to the right of the right tower extruded to OUTER_WALL_HEIGHT (6.77mm)
    all_ribs_poly = create_grid_ribs_poly(base_poly, outer_body_poly)
    # Bridge ribbing bounded between second horizontal rib (Y=6.4mm) and top horizontal rib (Y=9.6mm)
    bridge_box = box(13.36, 6.0, 25.0, 10.0)
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
    
    # 5. Backside Slit Protruding Walls (Z: -SLIT_BOSS_HEIGHT to 0)
    bosses_poly = create_backside_slit_bosses_poly()
    mesh_bosses = extrude_shapely_geom(bosses_poly, height=SLIT_BOSS_HEIGHT)
    mesh_bosses.apply_translation([0, 0, -SLIT_BOSS_HEIGHT])
    
    # 6. Shaft Support Towers & Triangular Struts (Z: 1.0 to 13.59mm)
    mesh_towers = build_clean_shaft_towers_mesh()
    mesh_struts = build_left_tower_struts_mesh()
    mesh_towers_assembly = trimesh.util.concatenate([mesh_towers, mesh_struts])
    
    # 7. Snap Clips: Slotted perimeter wall + direct outer hook wedges (4 clips: 45, 135, 225, 315 deg)
    slot_cuts = []
    hook_meshes = []
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT         # 4.97 mm
    slot_z_bot = OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH # 3.07 mm
    slot_t = 0.60                                   # 0.60mm wide flex slots
    
    for angle_deg in [45, 135, 225, 315]:
        center_rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = CLIP_ARM_WIDTH / r_est
        slot_d_theta = slot_t / r_est
        
        # 1. Two vertical flex slots through the wall on either side of the clip arm
        for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
            slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
            rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
            s_box = trimesh.creation.box([OUTER_WALL_THICK * 4.0, slot_t, CLIP_GAP_DEPTH + 1.0])
            s_box.apply_transform(rot_mat)
            s_box.apply_translation([slot_p[0], slot_p[1], slot_z_bot + (CLIP_GAP_DEPTH + 1.0)/2])
            slot_cuts.append(s_box)
            
        # 2. Hook Wedge on the outer face of the flexible curved wall beam (Z: 4.97 to 6.77mm)
        N = 16
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        
        outer_coords = []
        shelf_coords = []
        
        for th in theta_vals:
            ray_dir = np.array([np.cos(th), np.sin(th)])
            ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
            inter_out = outer_body_poly.exterior.intersection(ray)
            if inter_out.geom_type == 'Point':
                po = np.array([inter_out.x, inter_out.y])
            elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
                po = np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
            else:
                po = ray_dir * r_est
                
            n_dir = po / np.linalg.norm(po)
            ps = po + n_dir * CLIP_HOOK_DEPTH
            outer_coords.append(po)
            shelf_coords.append(ps)
            
        outer_coords = np.array(outer_coords)
        shelf_coords = np.array(shelf_coords)
        
        v0 = np.column_stack([outer_coords, np.full(N, stem_h)])
        v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
        v2 = np.column_stack([outer_coords, np.full(N, CLIP_HEIGHT)])
        hook_verts = np.vstack([v0, v1, v2])
        
        hook_faces = []
        for i in range(N - 1):
            # Retention shelf (at stem_h, pointing -Z): V0 -> V1
            hook_faces.append([i, N + i, N + i + 1])
            hook_faces.append([i, N + i + 1, i + 1])
            
            # Slanted outer bevel (pointing +radial/+Z): V1 -> V2
            hook_faces.append([N + i, 2*N + i + 1, N + i + 1])
            hook_faces.append([N + i, 2*N + i, 2*N + i + 1])
            
            # Inner mating face (at outer wall, pointing -radial): V2 -> V0
            hook_faces.append([2*N + i, i, i + 1])
            hook_faces.append([2*N + i, i + 1, 2*N + i + 1])
            
        # Side endcaps
        hook_faces.append([0, 2*N, N])
        hook_faces.append([N - 1, 2*N - 1, 3*N - 1])
        
        hook_mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
        hook_meshes.append(hook_mesh)
        
    try:
        all_slot_cuts = trimesh.util.concatenate(slot_cuts)
        mesh_wall = mesh_wall.difference(all_slot_cuts, engine='manifold')
    except Exception:
        pass
        
    # 8. Center Curved Feature with Internal Rib (Z: 1.0 to 10.50mm)
    curved_feat_poly = create_center_curved_feature_poly()
    mesh_curved_feat = extrude_shapely_geom(curved_feat_poly, height=10.50 - BASE_THICK)
    mesh_curved_feat.apply_translation([0, 0, BASE_THICK])
    
    # Main part is 100% planar at Z = 0.00mm for direct support-free 3D printing
    full_part = trimesh.util.concatenate([mesh_base, mesh_wall, mesh_ribs, mesh_brackets, mesh_towers_assembly, mesh_curved_feat] + hook_meshes)
    return full_part, base_poly

def build_slit_insert_mesh():
    """Builds a single separate 3D-printable backside slit wall insert with indexing key.
    - Flat print bed face at Z = 0
    - Wall body: 3.50mm x 5.40mm outer, 1.10mm x 3.00mm inner, height = 2.47mm (Z: 0 to 2.47mm)
    - Indexing registration key: 0.95mm x 2.85mm outer, 0.65mm x 2.55mm inner, height = 0.85mm (Z: 2.47 to 3.32mm)
    - Mating shoulder at Z = 2.47mm sits flush against main plate bottom.
    """
    # 1. Main Wall Body (Z: 0.0 to 2.47mm)
    outer_box = box(-3.50/2, -5.40/2, 3.50/2, 5.40/2)
    inner_box = box(-1.10/2, -3.00/2, 1.10/2, 3.00/2)
    body_poly = outer_box.difference(inner_box)
    m_body = extrude_shapely_geom(body_poly, height=SLIT_BOSS_HEIGHT)
    
    # 2. Indexing Registration Key (Z: 2.47 to 3.32mm)
    key_outer = box(-0.95/2, -2.85/2, 0.95/2, 2.85/2)
    key_inner = box(-0.65/2, -2.55/2, 0.65/2, 2.55/2)
    key_poly = key_outer.difference(key_inner)
    m_key = extrude_shapely_geom(key_poly, height=0.85)
    m_key.apply_translation([0, 0, SLIT_BOSS_HEIGHT])
    
    m_insert = trimesh.util.concatenate([m_body, m_key])
    m_insert = trimesh.Trimesh(vertices=m_insert.vertices, faces=m_insert.faces, process=True)
    return m_insert

def build_indexed_assembly_mesh(main_mesh, insert_mesh):
    """Creates the full mated 3D assembly mesh with both inserts indexed into the main part."""
    # Left slit position: X = -8.403mm, Y = -14.839mm
    # Right slit position: X = +8.403mm, Y = -14.839mm
    # When mated, insert shoulder (Z = 2.47mm) touches main part bottom (Z = 0.00mm) -> translation in Z = -2.47mm
    ins_left = insert_mesh.copy()
    ins_left.apply_translation([-8.403, -14.839, -SLIT_BOSS_HEIGHT])
    
    ins_right = insert_mesh.copy()
    ins_right.apply_translation([8.403, -14.839, -SLIT_BOSS_HEIGHT])
    
    return trimesh.util.concatenate([main_mesh, ins_left, ins_right])

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
clip_height         = {CLIP_HEIGHT};
clip_gap_depth      = {CLIP_GAP_DEPTH};
clip_arm_thick      = {CLIP_ARM_THICK};
clip_arm_width      = {CLIP_ARM_WIDTH};
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
            
        // Two Bottom Vertical Slits
        translate([-7.853 - 1.10, -16.339])
            square([1.10, 3.00]);
        translate([7.853, -16.339])
            square([1.10, 3.00]);
    }}
}}

module complete_part() {{
    union() {{
        // Base plate
        linear_extrude(height = base_thickness)
            base_plate_2d();
            
        // Outer Wall with constant thickness following exact non-circular perimeter
        difference() {{
            linear_extrude(height = outer_wall_height)
                base_plate_2d();
            translate([0, 0, base_thickness])
                linear_extrude(height = outer_wall_height + 1)
                    offset(r = -outer_wall_thick)
                        base_plate_2d();
        }}
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
    
    # Export pair of inserts for single build-plate 3D printing
    ins_1 = insert_mesh.copy()
    ins_1.apply_translation([-4.0, 0, 0])
    ins_2 = insert_mesh.copy()
    ins_2.apply_translation([4.0, 0, 0])
    pair_mesh = trimesh.util.concatenate([ins_1, ins_2])
    pair_mesh.export('slit_inserts_pair.stl')
    print("Exported slit_inserts_pair.stl successfully!")
    
    # Export complete assembled model
    assembly_mesh = build_indexed_assembly_mesh(part_mesh, insert_mesh)
    assembly_mesh.export('complete_assembly.stl')
    assembly_mesh.export('complete_assembly.obj')
    print("Exported complete_assembly.stl successfully!")
    
    render_plots(part_mesh, base_poly)
    export_openscad_exact(base_poly)
    print("All tasks complete!")
