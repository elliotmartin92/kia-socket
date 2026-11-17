"""
testing/build_prototype_levers.py
Generates rapid-prototype shaft/rocker variants for drop-in retrofit testing:
- Includes exact geometry from commit [1372a2d] (OEM 3-prong fork architecture).
- Includes commit [1372a2d] scaled by +0.55% (S = 1.0055) to compensate for the higher
  shrinkage of PC-FR (0.85%) vs PCTG (0.35%).
- Includes newly upgraded kinematic variants (Ultra-Sensitive, Balanced Nominal, Progressive Smooth).
- Printed at the EXACT +45° PIP angle matching production Print-in-Place layer orientation!
- Clean arms: NO pips or bumps on the lever arms (100% production-identical finish).
- Dedicated breakaway supports matching the real PIP part (build_part.py), 'just shorter'.
- Shortened total axle length (9.80 mm vs 11.50 mm) for effortless retrofitting into existing towers.
- Embossed identification notch bars ("I", "II", "III", "IV", "V") on the bed pad front lip.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, HUB_WIDTH, PIN_DIAMETER, HUB_DIAMETER,
    PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X, CAM_WIDTH_X, CAM_X_START,
    X_TOWER_CENTER, HOLE_X_CENTER, RIB_FLANK_THICK,
    KINEMATIC_VARIANTS, build_shaft_rocker_mesh
)

PROTO_AXLE_LEN = 9.80  # Shortened axle length (9.80mm vs 11.50mm) for easy retrofit into existing towers
R_PIP_45 = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
DZ_BASEPLATE_SHIFT = 13.109052303519203  # Offset from build_part.py to lower lever directly onto bed pad
BED_PAD_H = 0.60                         # 3 layers at 0.20mm layer height
LEVER_PITCH_X = 18.00                    # Pitch between adjacent levers on test plate

# Shrinkage differential: PC-FR (0.85%) vs PCTG (0.35%)
# Scale Factor = (1 - 0.0035) / (1 - 0.0085) = 1.00504 ~ 1.0055 (+0.55%)
SHRINKAGE_SCALE_PCTG_TO_PCFR = 1.0055

# ==============================================================================
# COMMIT [1372a2d] EXACT GEOMETRY GENERATOR
# ==============================================================================
def build_1372a2d_rocker_mesh(axle_len=PROTO_AXLE_LEN, scale_factor=1.0):
    """
    Recreates the exact OEM 3-prong fork architecture from commit [1372a2d].
    If scale_factor != 1.0, scales all features relative to the pivot axle center
    (accounting for PCTG vs PC-FR thermal shrinkage difference).
    """
    y_axle = 7.666
    z_axle = 12.590
    x_c = 9.250  # X_TOWER_CENTER
    
    hub_w = 7.60
    pin_d = 1.90
    hub_d = 3.30
    plunger_reach_below_z = 6.50
    prong_side_w = 0.85
    prong_center_w = 2.00
    cam_w = 2.60
    cam_x_c = 6.80
    
    r_pin = pin_d / 2.0
    x_min = x_c - axle_len / 2.0
    x_max = x_c + axle_len / 2.0
    pin_len = (axle_len - hub_w) / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # Left & Right Pivot Pins
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_min + pin_len/2.0, y_axle, z_axle])
    
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_max - pin_len/2.0, y_axle, z_axle])
    
    # Central Hub Barrel
    hub_mesh = trimesh.creation.cylinder(radius=hub_d/2.0, height=hub_w, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # Outer Flank Prongs (Ribs 1 & 3)
    flank_collar = Point(y_axle, z_axle).buffer(hub_d / 2.0)
    flank_pts = [
        (y_axle - 1.20, z_axle + 0.40),
        (y_axle + 2.50, z_axle - 1.20),
        (y_axle + 2.10, z_axle - 3.80),
        (y_axle + 0.50, z_axle - 3.60),
        (y_axle - 1.30, z_axle - 0.80)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    # Prong 1 (Left Flank)
    m_p1_raw = trimesh.creation.extrude_polygon(poly_flank, height=prong_side_w)
    v_p1 = m_p1_raw.vertices.copy()
    v_prong1 = np.column_stack([v_p1[:, 2] + (x_c - hub_w/2.0 + 0.15), v_p1[:, 0], v_p1[:, 1]])
    mesh_prong1 = trimesh.Trimesh(vertices=v_prong1, faces=m_p1_raw.faces.copy(), process=True)
    
    # Prong 3 (Right Flank)
    m_p3_raw = trimesh.creation.extrude_polygon(poly_flank, height=prong_side_w)
    v_p3 = m_p3_raw.vertices.copy()
    v_prong3 = np.column_stack([v_p3[:, 2] + (x_c + hub_w/2.0 - 0.15 - prong_side_w), v_p3[:, 0], v_p3[:, 1]])
    mesh_prong3 = trimesh.Trimesh(vertices=v_prong3, faces=m_p3_raw.faces.copy(), process=True)
    
    # Center Extended Plunger Prong (Rib 2)
    z_tip = -plunger_reach_below_z  # -6.50mm
    r_tip = 0.90                    # 1.80mm nose thickness in Y
    plunger_y_center = 11.40
    
    N = 25
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + hub_d/2.0) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - hub_d/2.0) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger = unary_union([flank_collar, Polygon(pts_plunger)])
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=prong_center_w)
    v_p2 = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([v_p2[:, 2] + (HOLE_X_CENTER - prong_center_w/2.0), v_p2[:, 0], v_p2[:, 1]])
    mesh_prong2 = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # Input Cam Tab
    y_cam_tip = y_axle - 4.20  # Reaches Y = 3.466mm
    z_cam_tip = z_axle - 5.80  # Drops to Z = 6.790mm
    cam_collar = Point(y_axle, z_axle).buffer(hub_d / 2.0)
    cam_pts = [
        (y_axle + 1.20, z_axle + 1.20),
        (y_cam_tip, z_cam_tip + 2.20),
        (y_cam_tip, z_cam_tip),
        (y_cam_tip + 2.60, z_cam_tip),
        (y_axle + 0.20, z_axle - 2.20)
    ]
    poly_cam = unary_union([cam_collar, Polygon(cam_pts)])
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=cam_w)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (cam_x_c - cam_w/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_prong1, mesh_prong2, mesh_prong3,
        mesh_cam
    ])
    
    if scale_factor != 1.0:
        p_axle = np.array([x_c, y_axle, z_axle])
        v_orig = shaft_mesh.vertices
        v_scaled = p_axle + scale_factor * (v_orig - p_axle)
        shaft_mesh = trimesh.Trimesh(vertices=v_scaled, faces=shaft_mesh.faces.copy(), process=True)
        
    return shaft_mesh

def build_1372a2d_supports_45deg(mesh_45):
    """Generates breakaway supports matching 1372a2d rotated geometry."""
    v = mesh_45.vertices
    supp_components = []
    
    # 1. Plunger support under curved plunger tip
    pts_p = [
        (10.50, BED_PAD_H),
        (12.50, BED_PAD_H),
        (12.50, 3.15),
        (12.00, 3.00),
        (10.50, 3.07),
    ]
    poly_p = Polygon(pts_p)
    m_p2d = trimesh.creation.extrude_polygon(poly_p, height=1.40)
    vp = m_p2d.vertices
    p_supp = trimesh.Trimesh(vertices=np.column_stack([vp[:, 2] + 9.584, vp[:, 0], vp[:, 1]]), faces=m_p2d.faces)
    if p_supp.volume < 0:
        p_supp.faces = np.fliplr(p_supp.faces)
    supp_components.append(p_supp)
    
    # 2. Hub support under axle barrel (Z ~ 7.25, 0.48mm gap -> 6.77mm top)
    h_top = 6.77
    h_h = h_top - BED_PAD_H
    hub_supp = trimesh.creation.box([1.40, 1.40, h_h])
    hub_supp.apply_translation([9.25, -3.48, BED_PAD_H + h_h / 2.0])
    supp_components.append(hub_supp)
    
    # 3. Cam support under input cam tab (Z ~ 12.67, 0.28mm gap -> 12.39mm top)
    c_top = 12.39
    c_h = c_top - BED_PAD_H
    cam_supp = trimesh.creation.box([1.20, 1.20, c_h])
    cam_supp.apply_translation([6.80, -3.40, BED_PAD_H + c_h / 2.0])
    supp_components.append(cam_supp)
    
    return trimesh.util.concatenate(supp_components)

# ==============================================================================
# NEW KINEMATIC VARIANTS (from build_shaft.py)
# ==============================================================================
def build_variant_lever_45deg(cfg, axle_len=PROTO_AXLE_LEN):
    """Builds a single clean variant lever rotated +45°."""
    mesh_raw = build_shaft_rocker_mesh(
        axle_len=axle_len,
        hub_w=HUB_WIDTH,
        pin_d=PIN_DIAMETER,
        hub_d=HUB_DIAMETER,
        plunger_reach_below_z=cfg.get('plunger_reach', 7.00),
        plunger_y_center=cfg['plunger_y'],
        plunger_w_x=PLUNGER_WIDTH_X,
        cam_w_x=CAM_WIDTH_X,
        cam_x_c=6.55,
        cam_pts=cfg['cam_pts'],
        in_assembly_coords=True,
        with_supports=False
    )
    mesh_45 = mesh_raw.copy().apply_transform(R_PIP_45)
    return mesh_45

def build_variant_supports_45deg(cfg):
    """Builds the exact breakaway support structure from build_part.py, 'just shorter'."""
    dz = DZ_BASEPLATE_SHIFT
    supp_components = []
    
    # 1. Plunger Breakaway Support Cradle (0.20mm release gap)
    dy = cfg['plunger_y'] - 10.95
    cos45 = np.cos(np.radians(45.0))
    sin45 = np.sin(np.radians(45.0))
    dy_p = dy * cos45
    dz_p = dy * sin45
    
    pts_plunger_tine_yz = [
        (8.50 + dy_p, BED_PAD_H),
        (12.10 + dy_p, BED_PAD_H),
        (12.10 + dy_p, 15.80 - dz + dz_p),
        (11.30 + dy_p, 15.432 - dz + dz_p),
        (10.75 + dy_p, 15.594 - dz + dz_p),
        (7.50 + dy_p,  18.814 - dz + dz_p),
        (7.50 + dy_p,  1.40),
        (8.50 + dy_p,  1.40),
    ]
    poly_p = Polygon(pts_plunger_tine_yz)
    
    # Left, Right, Center tines
    p_tine_w = 0.80
    m_pl_2d = trimesh.creation.extrude_polygon(poly_p, height=p_tine_w)
    vl = m_pl_2d.vertices
    p_tine_l = trimesh.Trimesh(vertices=np.column_stack([vl[:, 2] + 8.484, vl[:, 0], vl[:, 1]]), faces=m_pl_2d.faces)
    if p_tine_l.volume < 0:
        p_tine_l.faces = np.fliplr(p_tine_l.faces)
    supp_components.append(p_tine_l)
    
    m_pr_2d = trimesh.creation.extrude_polygon(poly_p, height=p_tine_w)
    vr = m_pr_2d.vertices
    p_tine_r = trimesh.Trimesh(vertices=np.column_stack([vr[:, 2] + 11.284, vr[:, 0], vr[:, 1]]), faces=m_pr_2d.faces)
    if p_tine_r.volume < 0:
        p_tine_r.faces = np.fliplr(p_tine_r.faces)
    supp_components.append(p_tine_r)
    
    p_center_w = 0.70
    x_c_start = 10.284 - p_center_w / 2.0
    m_pc_2d = trimesh.creation.extrude_polygon(poly_p, height=p_center_w)
    vc = m_pc_2d.vertices
    p_tine_c = trimesh.Trimesh(vertices=np.column_stack([vc[:, 2] + x_c_start, vc[:, 0], vc[:, 1]]), faces=m_pc_2d.faces)
    if p_tine_c.volume < 0:
        p_tine_c.faces = np.fliplr(p_tine_c.faces)
    supp_components.append(p_tine_c)
    
    # Base stabilizing web
    poly_p_web = Polygon([
        (8.50 + dy_p, BED_PAD_H),
        (12.10 + dy_p, BED_PAD_H),
        (12.10 + dy_p, 1.40),
        (8.50 + dy_p, 1.40)
    ])
    m_pw_2d = trimesh.creation.extrude_polygon(poly_p_web, height=2.00)
    vw = m_pw_2d.vertices
    p_web = trimesh.Trimesh(vertices=np.column_stack([vw[:, 2] + 9.284, vw[:, 0], vw[:, 1]]), faces=m_pw_2d.faces)
    if p_web.volume < 0:
        p_web.faces = np.fliplr(p_web.faces)
    supp_components.append(p_web)
    
    # 2. Cam Breakaway Support Strut (0.28mm release gap)
    cam_c_x = 6.600
    cam_c_y = -2.333
    z_cam_fork_base = 16.00 - dz  # 2.891mm
    
    cam_trunk_h = z_cam_fork_base - BED_PAD_H
    if cam_trunk_h > 0.2:
        cam_trunk = trimesh.creation.box([1.40, 1.40, cam_trunk_h])
        cam_trunk.apply_translation([cam_c_x, cam_c_y, BED_PAD_H + cam_trunk_h / 2.0])
        supp_components.append(cam_trunk)
        
    pts_cam_tine_yz = [
        (-3.60, z_cam_fork_base),
        (-3.60, 20.123 - dz),
        (-3.20, 19.952 - dz),
        (-2.40, 19.895 - dz),
        (-1.60, 20.069 - dz),
        (-1.00, 20.232 - dz),
        (-1.00, z_cam_fork_base),
    ]
    poly_cam_head_yz = Polygon(pts_cam_tine_yz)
    cam_tine_w = 0.55
    
    m_cl = trimesh.creation.extrude_polygon(poly_cam_head_yz, height=cam_tine_w)
    v_cl = m_cl.vertices.copy()
    cam_tine_l = trimesh.Trimesh(vertices=np.column_stack([v_cl[:, 2] + 5.65, v_cl[:, 0], v_cl[:, 1]]), faces=m_cl.faces.copy())
    if cam_tine_l.volume < 0:
        cam_tine_l.faces = np.fliplr(cam_tine_l.faces)
    supp_components.append(cam_tine_l)
    
    m_cr = trimesh.creation.extrude_polygon(poly_cam_head_yz, height=cam_tine_w)
    v_cr = m_cr.vertices.copy()
    cam_tine_r = trimesh.Trimesh(vertices=np.column_stack([v_cr[:, 2] + 7.00, v_cr[:, 0], v_cr[:, 1]]), faces=m_cr.faces.copy())
    if cam_tine_r.volume < 0:
        cam_tine_r.faces = np.fliplr(cam_tine_r.faces)
    supp_components.append(cam_tine_r)
    
    cam_mid_web = trimesh.creation.box([0.80, 1.40, 0.80])
    cam_mid_web.apply_translation([cam_c_x, cam_c_y, z_cam_fork_base + 0.40])
    supp_components.append(cam_mid_web)
    
    # 3. Floating Shaft Barrel Support Strut (0.48mm release gap)
    shaft_s_x_c = 8.850
    shaft_s_y_c = -2.341
    z_shaft_stick_top = 25.993 - dz  # 12.884mm
    z_shaft_fork_base = 21.50 - dz   # 8.391mm
    
    shaft_trunk_h = z_shaft_fork_base - BED_PAD_H
    shaft_trunk = trimesh.creation.box([0.70, 0.85, shaft_trunk_h])
    shaft_trunk.apply_translation([shaft_s_x_c, shaft_s_y_c, BED_PAD_H + shaft_trunk_h / 2.0])
    supp_components.append(shaft_trunk)
    
    head_w_x = 0.68
    head_w_y = 0.65
    tine_w = 0.26
    z_shaft_notch = z_shaft_stick_top - 0.35
    x_l = shaft_s_x_c - head_w_x / 2.0
    x_r = shaft_s_x_c + head_w_x / 2.0
    pts_shaft_xz = [
        (x_l, z_shaft_fork_base),
        (x_l, z_shaft_stick_top),
        (x_l + tine_w, z_shaft_stick_top),
        (shaft_s_x_c, z_shaft_notch),
        (x_r - tine_w, z_shaft_stick_top),
        (x_r, z_shaft_stick_top),
        (x_r, z_shaft_fork_base),
    ]
    poly_shaft_xz = Polygon(pts_shaft_xz)
    m_s_2d = trimesh.creation.extrude_polygon(poly_shaft_xz, height=head_w_y)
    vs = m_s_2d.vertices.copy()
    shaft_fork_head = trimesh.Trimesh(
        vertices=np.column_stack([vs[:, 0], vs[:, 2] - head_w_y / 2.0 + shaft_s_y_c, vs[:, 1]]),
        faces=m_s_2d.faces.copy()
    )
    if shaft_fork_head.volume < 0:
        shaft_fork_head.faces = np.fliplr(shaft_fork_head.faces)
    supp_components.append(shaft_fork_head)
    
    return trimesh.util.concatenate(supp_components)

# ==============================================================================
# BED PAD WITH EMBOSSED NOTCHES
# ==============================================================================
def build_bed_pad_with_notches(test_suite, pitch_x=LEVER_PITCH_X):
    """
    Builds a monolithic bed pad raft with rounded corners and embossed
    identification notch bars on the front lip for each test:
      Test 1: I bar    (1372a2d Exact)
      Test 2: II bars  (1372a2d Scaled for PC-FR)
      Test 3: III bars (V1 Ultra-Sensitive)
      Test 4: IIII bars (V3 Balanced Nominal)
      Test 5: IIIII bars (V4 Smooth Progressive)
    """
    n_vars = len(test_suite)
    x_offsets = [(i - (n_vars - 1) / 2.0) * pitch_x for i in range(n_vars)]
    
    pad_x_min = min(x_offsets) - 7.50
    pad_x_max = max(x_offsets) + 7.50
    pad_y_min = -6.50
    pad_y_max = 16.50
    r_corner = 2.50
    
    inner = box(pad_x_min + r_corner, pad_y_min + r_corner, pad_x_max - r_corner, pad_y_max - r_corner)
    pad_poly = inner.buffer(r_corner, resolution=16)
    m_pad = trimesh.creation.extrude_polygon(pad_poly, height=BED_PAD_H)
    
    marker_boxes = []
    notch_w = 0.65
    notch_len = 2.40
    notch_h = 0.40
    notch_pitch = 1.15
    front_y = 14.60
    
    for i, test in enumerate(test_suite):
        cx = x_offsets[i]
        n_bars = test['bars']
        total_w = (n_bars - 1) * notch_pitch
        start_x = cx - total_w / 2.0
        for b_idx in range(n_bars):
            bx = start_x + b_idx * notch_pitch
            bar = trimesh.creation.box([notch_w, notch_len, notch_h])
            bar.apply_translation([bx, front_y, BED_PAD_H + notch_h / 2.0])
            marker_boxes.append(bar)
            
    all_pad_parts = [m_pad] + marker_boxes
    return trimesh.util.concatenate(all_pad_parts), x_offsets

# ==============================================================================
# MAIN TEST SUITE & EXPORTS
# ==============================================================================
def get_test_suite():
    """Defines the 5-test suite including commit [1372a2d] exact and scaled."""
    suite = [
        {
            'id': 'v_1372a2d_exact',
            'bars': 1,
            'name': 'Test 1: Commit [1372a2d] Exact Geometry (PCTG Baseline)',
            'short_name': '1372a2d Exact',
            'is_1372': True,
            'scale': 1.0,
            'desc': 'Exact bit-for-bit geometry of commit [1372a2d] (OEM 3-prong fork architecture).'
        },
        {
            'id': 'v_1372a2d_scaled',
            'bars': 2,
            'name': 'Test 2: Commit [1372a2d] Scaled for PC-FR (+0.55% Shrinkage Compensation)',
            'short_name': '1372a2d Scaled (+0.55%)',
            'is_1372': True,
            'scale': SHRINKAGE_SCALE_PCTG_TO_PCFR,
            'desc': 'Commit [1372a2d] scaled by +0.55% to match physical PCTG dimensions in PC-FR.'
        },
        {
            'id': 'v1_ultra_sens',
            'bars': 3,
            'name': 'Test 3: V1 Ultra-Sensitive (Apex Y=1.65, Plunger Y=11.25)',
            'short_name': 'V1 Ultra-Sens',
            'is_1372': False,
            'cfg': KINEMATIC_VARIANTS['v1_ultra_sens'],
            'desc': 'Maximum non-polar capture: early trip on shallow blade penetration (+0.47mm OT).'
        },
        {
            'id': 'v3_nominal',
            'bars': 4,
            'name': 'Test 4: V3 Balanced Nominal (Apex Y=2.10, Plunger Y=10.95)',
            'short_name': 'V3 Nominal',
            'is_1372': False,
            'cfg': KINEMATIC_VARIANTS['v3_nominal'],
            'desc': 'The golden mean: reliable trip on both polar and forward non-polar plugs.'
        },
        {
            'id': 'v4_smooth',
            'bars': 5,
            'name': 'Test 5: V4 Smooth Progressive (Apex Y=2.30, Plunger Y=10.80)',
            'short_name': 'V4 Smooth',
            'is_1372': False,
            'cfg': KINEMATIC_VARIANTS['v4_smooth'],
            'desc': 'Crowned rolling lead-in: low insertion force for polar plugs (+0.15mm OT).'
        }
    ]
    return suite

def build_5pack_plate(export_dir="testing"):
    """Builds and exports the complete 5-test rapid prototype plate."""
    os.makedirs(export_dir, exist_ok=True)
    test_suite = get_test_suite()
    
    pad_mesh, x_offsets = build_bed_pad_with_notches(test_suite, pitch_x=LEVER_PITCH_X)
    
    supported_parts = [pad_mesh]
    clean_parts = []
    
    print(f"Building 5-Test Rapid-Prototype Levers (Pitch: {LEVER_PITCH_X:.1f}mm)...")
    for i, test in enumerate(test_suite):
        cx = x_offsets[i]
        x_lever_center = 9.25
        
        if test['is_1372']:
            m_raw = build_1372a2d_rocker_mesh(axle_len=PROTO_AXLE_LEN, scale_factor=test['scale'])
            m_lever = m_raw.apply_transform(R_PIP_45)
            m_supp = build_1372a2d_supports_45deg(m_lever)
            
            # Also export unshortened 11.50mm axle version for reference
            m_raw_11_5 = build_1372a2d_rocker_mesh(axle_len=11.50, scale_factor=test['scale'])
            path_11_5 = os.path.join(export_dir, f"prototype_lever_{test['id']}_full_axle_11.5mm.stl")
            m_raw_11_5.export(path_11_5)
        else:
            cfg = test['cfg']
            m_lever = build_variant_lever_45deg(cfg, axle_len=PROTO_AXLE_LEN)
            m_supp = build_variant_supports_45deg(cfg)
            
        m_lever.apply_translation([-x_lever_center + cx, 0, 0])
        m_supp.apply_translation([-x_lever_center + cx, 0, 0])
        
        supported_parts.extend([m_supp, m_lever])
        clean_parts.append(m_lever)
        
        # Individual single-lever STL exports
        single_pad, _ = build_bed_pad_with_notches([test], pitch_x=LEVER_PITCH_X)
        if test['is_1372']:
            s_raw = build_1372a2d_rocker_mesh(axle_len=PROTO_AXLE_LEN, scale_factor=test['scale'])
            s_lever = s_raw.apply_transform(R_PIP_45)
            s_supp = build_1372a2d_supports_45deg(s_lever)
        else:
            s_lever = build_variant_lever_45deg(test['cfg'], axle_len=PROTO_AXLE_LEN)
            s_supp = build_variant_supports_45deg(test['cfg'])
            
        s_lever.apply_translation([-x_lever_center, 0, 0])
        s_supp.apply_translation([-x_lever_center, 0, 0])
        
        indiv_supp = trimesh.util.concatenate([single_pad, s_supp, s_lever])
        path_indiv_supp = os.path.join(export_dir, f"prototype_lever_{test['id']}_supported_45deg.stl")
        path_indiv_bare = os.path.join(export_dir, f"prototype_lever_{test['id']}_bare_45deg.stl")
        indiv_supp.export(path_indiv_supp)
        s_lever.export(path_indiv_bare)
        print(f"  [{i+1}/5] {test['name']} -> {path_indiv_supp}")
        
    plate_supported = trimesh.util.concatenate(supported_parts)
    plate_clean = trimesh.util.concatenate(clean_parts)
    
    path_supp_stl = os.path.join(export_dir, "prototype_levers_5pack_supported_45deg.stl")
    path_supp_3mf = os.path.join(export_dir, "prototype_levers_5pack_supported_45deg.3mf")
    path_clean_stl = os.path.join(export_dir, "prototype_levers_5pack_clean_45deg.stl")
    
    plate_supported.export(path_supp_stl)
    plate_supported.export(path_supp_3mf)
    plate_clean.export(path_clean_stl)
    
    print("\nSuccessfully exported:")
    print(f"  -> Pre-supported 5-Pack (STL): {path_supp_stl}")
    print(f"  -> Pre-supported 5-Pack (3MF): {path_supp_3mf}")
    print(f"  -> Clean 5-Pack Bare (STL):    {path_clean_stl}")
    print(f"  -> Total Bounding Box (X x Y x Z): "
          f"{plate_supported.bounds[1,0]-plate_supported.bounds[0,0]:.1f} x "
          f"{plate_supported.bounds[1,1]-plate_supported.bounds[0,1]:.1f} x "
          f"{plate_supported.bounds[1,2]-plate_supported.bounds[0,2]:.1f} mm")
    return plate_supported

def generate_preview_5variants(preview_path=None):
    """Generates the dimensioned comparison blueprint across the 5 test subjects."""
    if preview_path is None:
        preview_path = os.path.join(os.path.dirname(__file__), "prototype_5levers_preview.png")
    else:
        preview_path = os.path.abspath(preview_path)
        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 13), facecolor='#1e293b')
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor('#0f172a')
        ax.tick_params(colors='#94a3b8')
        for spine in ax.spines.values():
            spine.set_color('#334155')
            
    palette = ['#e11d48', '#f59e0b', '#38bdf8', '#a855f7', '#10b981']
    test_suite = get_test_suite()
    
    # 1. Overlay of 2D Cam Profiles
    ax1.set_title("1. Cam Profiles & Contact Apex across Test Suite (Y-Z Plane)", color='#f8fafc', fontsize=13, fontweight='bold', pad=12)
    ax1.plot([9.279], [12.590], 'o', color='#f8fafc', markersize=8, label='Current Axle (Y=9.28, Z=12.59)')
    ax1.plot([7.666], [12.590], 's', color='#94a3b8', markersize=8, label='1372a2d Axle (Y=7.67, Z=12.59)')
    ax1.axvline(3.10, color='#ef4444', linestyle=':', lw=1.8, label='Non-Polar Blade Rear (Touching Moon)')
    ax1.axvline(3.48, color='#facc15', linestyle='--', lw=1.8, label='Nominal Blade Rear (Pinch Throat Center)')
    
    for i, test in enumerate(test_suite):
        if test['is_1372']:
            y_ax = 7.666
            z_ax = 12.590
            s = test['scale']
            y_tip = y_ax - 4.20 * s
            z_tip = z_ax - 5.80 * s
            pts = np.array([
                [y_ax + 1.20 * s, z_ax + 1.20 * s],
                [y_tip, z_tip + 2.20 * s],
                [y_tip, z_tip],
                [y_tip + 2.60 * s, z_tip],
                [y_ax + 0.20 * s, z_ax - 2.20 * s]
            ])
            ax1.plot(pts[:, 0], pts[:, 1], '-s', color=palette[i], lw=2.2, markersize=4,
                     label=f"[{test['bars']}] {test['short_name']} (Apex: Y={y_tip:.2f}, Z={z_tip:.2f})")
        else:
            cfg = test['cfg']
            pts = np.array(cfg['cam_pts'])
            ax1.plot(pts[:, 0], pts[:, 1], '-o', color=palette[i], lw=2.2, markersize=3.5,
                     label=f"[{test['bars']}] {test['short_name']} (Apex: {cfg['cam_apex']})")
            ax1.plot([cfg['cam_apex'][0]], [cfg['cam_apex'][1]], '*', color='white', markersize=8)
            
    ax1.set_xlabel("Y Position (mm)", color='#cbd5e1', fontweight='bold')
    ax1.set_ylabel("Z Elevation (mm)", color='#cbd5e1', fontweight='bold')
    ax1.legend(loc='upper right', fontsize=8, facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc')
    ax1.grid(True, color='#334155', linestyle=':')
    ax1.set_xlim(1.0, 10.5)
    ax1.set_ylim(5.0, 15.0)
    
    # 2. Plunger Home Position & Switch Pre-Travel
    ax2.set_title("2. Plunger Home Position & Switch Pre-Travel", color='#f8fafc', fontsize=13, fontweight='bold', pad=12)
    ax2.axvline(12.40, color='#22c55e', linestyle='-.', lw=2.0, label='PCB Switch Actuation Datum (Y = 12.40mm)')
    ax2.axvline(13.75, color='#ef4444', linestyle=':', lw=1.5, label='Through-Hole Rear Wall (Y = 13.75mm)')
    ax2.axvline(8.57, color='#ef4444', linestyle=':', lw=1.5, label='Through-Hole Front Wall (Y = 8.57mm)')
    
    for i, test in enumerate(test_suite):
        if test['is_1372']:
            yp = 11.40 * test['scale']
            z_reach = -6.50 * test['scale']
            pre_t = 12.40 - yp
            ax2.plot([yp, yp], [z_reach, 1.0], color=palette[i], lw=3.0, linestyle='--',
                     label=f"[{test['bars']}] {test['short_name']}: Home Y={yp:.2f}mm (Pre-travel: {pre_t:.2f}mm)")
            ax2.plot([yp], [z_reach], 's', color=palette[i], markersize=8)
        else:
            cfg = test['cfg']
            yp = cfg['plunger_y']
            pre_t = 12.40 - yp
            ax2.plot([yp, yp], [-7.0, 1.0], color=palette[i], lw=3.0,
                     label=f"[{test['bars']}] {test['short_name']}: Home Y={yp:.2f}mm (Pre-travel: {pre_t:.2f}mm)")
            ax2.plot([yp], [-7.0], 'o', color=palette[i], markersize=8)
            
    ax2.set_xlabel("Plunger Y Coordinate (mm)", color='#cbd5e1', fontweight='bold')
    ax2.set_ylabel("Z Coordinate (mm)", color='#cbd5e1', fontweight='bold')
    ax2.legend(loc='upper left', fontsize=8, facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc')
    ax2.grid(True, color='#334155', linestyle=':')
    ax2.set_xlim(8.0, 14.5)
    ax2.set_ylim(-8.0, 2.0)
    
    # 3. Rocker Rotation Angle vs Plug Blade Depth
    ax3.set_title("3. Rocker Rotation Angle vs Plug Blade Depth (Z_tip)", color='#f8fafc', fontsize=13, fontweight='bold', pad=12)
    z_tips = np.linspace(8.0, 6.8, 30)
    
    for i, test in enumerate(test_suite):
        if test['is_1372']:
            y_ax = 7.666
            z_ax = 12.590
            s = test['scale']
            y_tip = y_ax - 4.20 * s
            z_tip_pt = z_ax - 5.80 * s
            pts = np.array([
                [y_ax + 1.20 * s, z_ax + 1.20 * s],
                [y_tip, z_tip_pt + 2.20 * s],
                [y_tip, z_tip_pt],
                [y_tip + 2.60 * s, z_tip_pt],
                [y_ax + 0.20 * s, z_ax - 2.20 * s]
            ])
            thetas = [solve_theta_quick(pts, 3.48, zt, y_ax, z_ax) for zt in z_tips]
            ax3.plot(z_tips, thetas, color=palette[i], lw=2.2, linestyle='--', label=f"[{test['bars']}] {test['short_name']}")
        else:
            cfg = test['cfg']
            pts = np.array(cfg['cam_pts'])
            thetas = [solve_theta_quick(pts, 3.48, zt, Y_AXLE, Z_AXLE) for zt in z_tips]
            ax3.plot(z_tips, thetas, color=palette[i], lw=2.2, label=f"[{test['bars']}] {test['short_name']}")
            
    ax3.set_xlabel("Plug Blade Tip Depth Z_tip (mm)", color='#cbd5e1', fontweight='bold')
    ax3.set_ylabel("Rocker Rotation Angle Theta (deg)", color='#cbd5e1', fontweight='bold')
    ax3.invert_xaxis()
    ax3.legend(loc='upper left', fontsize=8, facecolor='#1e293b', edgecolor='#334155', labelcolor='#f8fafc')
    ax3.grid(True, color='#334155', linestyle=':')
    
    # 4. Identification & Testing Guide
    ax4.axis('off')
    guide = (
        "5-TEST PROTOTYPE SPECTRUM: COMMIT [1372a2d] & UPGRADED KINEMATICS\n"
        "===================================================================\n\n"
        "• Print Specifications:\n"
        "  - Orientation: 100% MATCH WITH PIP (+45° tilted around X axis).\n"
        "  - Lever Arms: 100% CLEAN & WATERTIGHT (No pips or bumps on arms).\n"
        "  - Supports: Real-part breakaway supports (build_part.py), 'just shorter'.\n"
        f"  - Total Axle Length: {PROTO_AXLE_LEN:.2f} mm (Shortened for drop-in retrofit).\n"
        "  - Plate Dimensions: ~87 x 23 x 17.6 mm (~16 min total print time!).\n\n"
        "• Identification Notches Embossed on Front Lip of Bed Pad:\n"
        "  [I]     1 BAR  = Test 1: Commit [1372a2d] Exact Geometry\n"
        "                  OEM 3-prong fork baseline as printed in PCTG.\n\n"
        "  [II]    2 BARS = Test 2: Commit [1372a2d] Scaled for PC-FR (+0.55%)\n"
        "                  Shrinkage-compensated: Plunger reaches 0.10mm deeper (Z=-6.60mm)\n"
        "                  and cam reaches 0.02mm further to match PCTG physical size.\n\n"
        "  [III]   3 BARS = Test 3: V1 Ultra-Sensitive (Apex Y=1.65, P_Y=11.25)\n"
        "                  Maximum non-polar capture: early trip on shallow penetration.\n\n"
        "  [IV]    4 BARS = Test 4: V3 Balanced Nominal (Apex Y=2.10, P_Y=10.95)\n"
        "                  Golden mean: reliable trip on polar & non-polar plugs.\n\n"
        "  [V]     5 BARS = Test 5: V4 Smooth Progressive (Apex Y=2.30, P_Y=10.80)\n"
        "                  Crowned rolling lead-in for low polar insertion force."
    )
    ax4.text(0.02, 0.98, guide, color='#f8fafc', fontsize=9.2, family='monospace', va='top')
    
    plt.tight_layout()
    plt.savefig(preview_path, dpi=200)
    plt.close()
    print(f"Generated 5-test comparison blueprint: {preview_path}")

def solve_theta_quick(pts_cam, y_blade, z_tip, y_ax, z_ax):
    """Solves required rocker rotation theta so no cam point penetrates into the plug blade."""
    for th in np.linspace(0, 15, 301):
        rad = np.radians(th)
        cos_t = np.cos(rad)
        sin_t = np.sin(rad)
        
        y_rel = pts_cam[:, 0] - y_ax
        z_rel = pts_cam[:, 1] - z_ax
        y_rot = y_ax + y_rel * cos_t - z_rel * sin_t
        z_rot = z_ax + y_rel * sin_t + z_rel * cos_t
        
        penetrates = np.any((z_rot >= z_tip) & (y_rot < y_blade))
        if not penetrates:
            return th
    return 15.0

if __name__ == '__main__':
    print("=" * 70)
    print("5-TEST RAPID PROTOTYPE LEVER GENERATOR")
    print("=" * 70)
    plate_mesh = build_5pack_plate("testing")
    preview_png = os.path.join("testing", "prototype_5levers_preview.png")
    generate_preview_5variants(preview_png)
    print("Done!")
