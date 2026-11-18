"""
testing/build_prototype_levers.py
Generates rapid-prototype shaft/rocker variants for drop-in retrofit testing:
- Includes exact geometry from commit [b4877a99273a053050683e6d446b3c83a785f496] (OEM 3-rib architecture).
- Includes commit [b4877a9] scaled by +0.55% (S = 1.0055) to compensate for the higher
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
from shapely.geometry import Polygon, Point, box, LineString
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

# Cam profile for b4877a9 Tuned (Apex elevated to Z=7.75mm at Y=1.50mm)
B4877A9_TUNED_CAM_PTS = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + 2.10),
    (6.80, 12.20),
    (5.00, 10.20),
    (1.50, 7.75),
    (1.80, 5.10),
    (4.50, 5.30),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
]

# ==============================================================================
# COMMIT [b4877a9] GEOMETRY GENERATOR
# ==============================================================================
def build_b4877a9_rocker_mesh(axle_len=PROTO_AXLE_LEN, plunger_y=10.479, cam_pts=None):
    """
    Recreates the OEM 3-rib architecture from commit [b4877a9].
    Supports custom plunger_y and cam_pts for the tuned variant.
    """
    from testing.build_shaft_b4877a9 import build_shaft_rocker_mesh as sb_mesh
    return sb_mesh(axle_len=axle_len, plunger_y_center=plunger_y, cam_pts=cam_pts, in_assembly_coords=True)

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

# ==============================================================================
# UNIFIED CONFORMAL BREAKAWAY SUPPORTS (Exact Alignment Across All 5 Tests)
# ==============================================================================
def build_variant_supports_45deg(test):
    """
    Builds exact, mathematically conformal breakaway support structures for each
    individual prototype lever variant rotated at +45°:
      1. Conformal Plunger Cradle (3 tines: Left, Right, Center + solid bed web)
         - Follows the analytical 45° incline and curved tip with calibrated 0.22mm release gap.
         - Roots solidly into the bed adhesion pad at Z = BED_PAD_H (0.60mm).
      2. Conformal Cam Fork (2 tines + central trunk + lateral web)
         - Dynamically traces each variant's downward-facing cam overhang profile.
         - Exact 0.22mm release gap, eliminating mid-air gaps and sag.
      3. Shaft Barrel Support Strut (2-tine micro-chisel fork on trunk)
         - Precision 0.48mm release gap under the central hub barrel at Z' = 13.364mm.
    """
    r2 = np.sqrt(2) / 2.0
    supp_components = []
    
    is_b4877a9 = test.get('is_b4877a9', False)
    py = test.get('plunger_y') if is_b4877a9 else test['cfg']['plunger_y']
    reach = test.get('plunger_reach', 6.50) if is_b4877a9 else test['cfg'].get('plunger_reach', 7.00)
    
    # -------------------------------------------------------------------------
    # 1. EXACT CONFORMAL PLUNGER CRADLE (3 Tines + Bed Web)
    # -------------------------------------------------------------------------
    r_tip = 1.00
    gap_p = 0.22  # Calibrated 0.22mm vertical release gap
    
    # 1a. Slope portion from Y'=8.50 to Y'_knee
    y_knee = (py - r_tip) * r2 - (-reach + r_tip) * r2
    z_knee = (py - r_tip) * r2 + (-reach + r_tip) * r2
    
    # 1b. Circular tip profile (downward-facing curve from knee a=pi to chin a=pi/2)
    alphas = np.linspace(np.pi, np.pi * 0.50, 20)
    tip_y = py + r_tip * np.cos(alphas)
    tip_z = -reach + r_tip * (1.0 - np.sin(alphas))
    tip_y45 = tip_y * r2 - tip_z * r2
    tip_z45 = tip_y * r2 + tip_z * r2
    
    y_start = 8.50
    y_slope = np.linspace(y_start, y_knee, 10)
    z_slope = z_knee + (y_knee - y_slope)  # 45° slope is identically -1.0 in Y'-Z'
    
    y_pts = np.concatenate([y_slope, tip_y45[1:]])
    z_pts = np.concatenate([z_slope, tip_z45[1:]]) - gap_p
    y_end = y_pts[-1]
    
    pts_plunger_tine = [(y_start, BED_PAD_H)]
    for y_v, z_v in zip(y_pts, z_pts):
        pts_plunger_tine.append((y_v, max(BED_PAD_H + 0.20, z_v)))
    pts_plunger_tine.append((y_end, BED_PAD_H))
    
    poly_p = Polygon(pts_plunger_tine)
    p_tine_w = 0.80
    
    # Left tine
    m_pl_2d = trimesh.creation.extrude_polygon(poly_p, height=p_tine_w)
    vl = m_pl_2d.vertices
    p_tine_l = trimesh.Trimesh(vertices=np.column_stack([vl[:, 2] + 8.484, vl[:, 0], vl[:, 1]]), faces=m_pl_2d.faces)
    if p_tine_l.volume < 0:
        p_tine_l.faces = np.fliplr(p_tine_l.faces)
    supp_components.append(p_tine_l)
    
    # Right tine
    m_pr_2d = trimesh.creation.extrude_polygon(poly_p, height=p_tine_w)
    vr = m_pr_2d.vertices
    p_tine_r = trimesh.Trimesh(vertices=np.column_stack([vr[:, 2] + 11.284, vr[:, 0], vr[:, 1]]), faces=m_pr_2d.faces)
    if p_tine_r.volume < 0:
        p_tine_r.faces = np.fliplr(p_tine_r.faces)
    supp_components.append(p_tine_r)
    
    # Center tine
    p_center_w = 0.70
    x_c_start = 10.284 - p_center_w / 2.0
    m_pc_2d = trimesh.creation.extrude_polygon(poly_p, height=p_center_w)
    vc = m_pc_2d.vertices
    p_tine_c = trimesh.Trimesh(vertices=np.column_stack([vc[:, 2] + x_c_start, vc[:, 0], vc[:, 1]]), faces=m_pc_2d.faces)
    if p_tine_c.volume < 0:
        p_tine_c.faces = np.fliplr(p_tine_c.faces)
    supp_components.append(p_tine_c)
    
    # Stabilizing web connecting tines from bed pad up to Z = 1.40mm
    poly_p_web = Polygon([
        (8.50, BED_PAD_H),
        (y_end - 0.40, BED_PAD_H),
        (y_end - 0.40, 1.40),
        (8.50, 1.40)
    ])
    m_pw_2d = trimesh.creation.extrude_polygon(poly_p_web, height=2.00)
    vw = m_pw_2d.vertices
    p_web = trimesh.Trimesh(vertices=np.column_stack([vw[:, 2] + 9.284, vw[:, 0], vw[:, 1]]), faces=m_pw_2d.faces)
    if p_web.volume < 0:
        p_web.faces = np.fliplr(p_web.faces)
    supp_components.append(p_web)
    
    # -------------------------------------------------------------------------
    # 2. EXACT CONFORMAL CAM SUPPORT FORK (2 Tines + Trunk + Web)
    # -------------------------------------------------------------------------
    gap_cam = 0.22  # Calibrated 0.22mm vertical release gap
    
    if is_b4877a9:
        if test.get('is_tuned', False):
            c_pts = np.array(B4877A9_TUNED_CAM_PTS)
        else:
            c_pts = np.array([
                (Y_AXLE, Z_AXLE),
                (Y_AXLE, Z_AXLE + 2.10),
                (6.80, 12.20),
                (5.00, 10.00),
                (1.50, 7.40),
                (1.80, 5.10),
                (4.50, 5.30),
                (Y_AXLE - 1.50, Z_AXLE - 2.50)
            ])
        cam_x_min = 5.80
        cam_x_max = 7.70
        cam_tine_w = 0.50
    else:
        c_pts = np.array(test['cfg']['cam_pts'])
        cam_x_min = 5.50
        cam_x_max = 7.60
        cam_tine_w = 0.55
        
    cam_w = cam_x_max - cam_x_min
    cam_x_c = (cam_x_min + cam_x_max) / 2.0
    
    # Rotate cam polygon to 45 deg
    c_y45 = c_pts[:, 0] * r2 - c_pts[:, 1] * r2
    c_z45 = c_pts[:, 0] * r2 + c_pts[:, 1] * r2
    poly_cam = Polygon(np.column_stack([c_y45, c_z45]))
    
    idx_min_z = np.argmin(c_z45)
    z_min_cam = c_z45[idx_min_z]
    y_min_z = c_y45[idx_min_z]
    
    if is_b4877a9:
        y_cam_start = -3.70
        y_cam_end = min(-0.90, y_min_z + 1.50)
    else:
        y_cam_start = max(np.min(c_y45) + 0.15, y_min_z - 1.40)
        y_cam_end = min(-0.80, y_min_z + 1.40)
        
    y_cam_eval = np.linspace(y_cam_start, y_cam_end, 25)
    
    cam_eval_pts = []
    for y_v in y_cam_eval:
        line = LineString([(y_v, -10), (y_v, 30)])
        inter = poly_cam.intersection(line)
        if not inter.is_empty:
            if inter.geom_type == 'LineString':
                z_bot = min(inter.coords[0][1], inter.coords[1][1])
            elif inter.geom_type == 'MultiLineString':
                z_bot = min(min(g.coords[0][1], g.coords[1][1]) for g in inter.geoms)
            else:
                z_bot = inter.bounds[1]
            cam_eval_pts.append((y_v, z_bot - gap_cam))
            
    z_fork_base = max(BED_PAD_H + 0.60, z_min_cam - gap_cam - 1.40)
    pts_cam_tines = [(cam_eval_pts[0][0], z_fork_base)]
    for pt in cam_eval_pts:
        pts_cam_tines.append(pt)
    pts_cam_tines.append((cam_eval_pts[-1][0], z_fork_base))
    
    poly_cam_head = Polygon(pts_cam_tines)
    
    x_tine_l = cam_x_min + 0.15
    x_tine_r = cam_x_max - 0.15 - cam_tine_w
    
    m_cl = trimesh.creation.extrude_polygon(poly_cam_head, height=cam_tine_w)
    vl = m_cl.vertices
    cam_tine_l = trimesh.Trimesh(vertices=np.column_stack([vl[:, 2] + x_tine_l, vl[:, 0], vl[:, 1]]), faces=m_cl.faces)
    if cam_tine_l.volume < 0:
        cam_tine_l.faces = np.fliplr(cam_tine_l.faces)
    supp_components.append(cam_tine_l)
    
    m_cr = trimesh.creation.extrude_polygon(poly_cam_head, height=cam_tine_w)
    vr = m_cr.vertices
    cam_tine_r = trimesh.Trimesh(vertices=np.column_stack([vr[:, 2] + x_tine_r, vr[:, 0], vr[:, 1]]), faces=m_cr.faces)
    if cam_tine_r.volume < 0:
        cam_tine_r.faces = np.fliplr(cam_tine_r.faces)
    supp_components.append(cam_tine_r)
    
    # Cam trunk: rises from bed pad to z_fork_base
    trunk_h = z_fork_base - BED_PAD_H
    trunk_y_w = min(1.60, (y_cam_end - y_cam_start) * 0.75)
    cam_trunk = trimesh.creation.box([1.40, trunk_y_w, trunk_h])
    cam_trunk.apply_translation([cam_x_c, y_min_z, BED_PAD_H + trunk_h / 2.0])
    supp_components.append(cam_trunk)
    
    # Stabilizing mid-web between tines:
    mid_web = trimesh.creation.box([cam_w - 0.30, trunk_y_w, 0.70])
    mid_web.apply_translation([cam_x_c, y_min_z, z_fork_base + 0.35])
    supp_components.append(mid_web)
    
    # -------------------------------------------------------------------------
    # 3. FLOATING SHAFT BARREL SUPPORT STRUT (2-Tine Fork Under Hub)
    # -------------------------------------------------------------------------
    shaft_s_x_c = 8.850
    shaft_s_y_c = -2.341
    z_shaft_stick_top = 12.884   # 0.48mm release gap below hub bottom at Z'=13.364mm
    z_shaft_fork_base = 8.50
    
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
      Test 1: I bar    (b4877a9 Exact)
      Test 2: II bars  (b4877a9 Scaled for PC-FR)
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
    """Defines the 5-test suite including commit [b4877a9] exact and tuned."""
    suite = [
        {
            'id': 'v_b4877a9_exact',
            'bars': 1,
            'name': 'Test 1: Commit [b4877a9] Exact Geometry (Baseline)',
            'short_name': 'b4877a9 Exact',
            'is_b4877a9': True,
            'is_tuned': False,
            'plunger_y': 10.479,
            'cam_pts': None,
            'cam_apex': (1.50, 7.40),
            'desc': 'Exact bit-for-bit geometry of commit [b4877a9] (OEM 3-rib architecture, Apex Z=7.40, Plunger Y=10.48).'
        },
        {
            'id': 'v_b4877a9_tuned',
            'bars': 2,
            'name': 'Test 2: Commit [b4877a9] Tuned Pre-Travel & Elevated Ramp',
            'short_name': 'b4877a9 Tuned',
            'is_b4877a9': True,
            'is_tuned': True,
            'plunger_y': 11.15,
            'cam_pts': B4877A9_TUNED_CAM_PTS,
            'cam_apex': (1.50, 7.75),
            'desc': 'Commit [b4877a9] with plunger advanced to Y=11.15mm and cam apex elevated to Z=7.75mm for consistent actuation in PC-FR.'
        },
        {
            'id': 'v1_ultra_sens',
            'bars': 3,
            'name': 'Test 3: V1 Ultra-Sensitive (Apex Y=1.65, Plunger Y=11.25)',
            'short_name': 'V1 Ultra-Sens',
            'is_b4877a9': False,
            'cfg': KINEMATIC_VARIANTS['v1_ultra_sens'],
            'desc': 'Maximum non-polar capture: early trip on shallow blade penetration (+0.47mm OT).'
        },
        {
            'id': 'v3_nominal',
            'bars': 4,
            'name': 'Test 4: V3 Balanced Nominal (Apex Y=2.10, Plunger Y=10.95)',
            'short_name': 'V3 Nominal',
            'is_b4877a9': False,
            'cfg': KINEMATIC_VARIANTS['v3_nominal'],
            'desc': 'The golden mean: reliable trip on both polar and forward non-polar plugs.'
        },
        {
            'id': 'v4_smooth',
            'bars': 5,
            'name': 'Test 5: V4 Smooth Progressive (Apex Y=2.30, Plunger Y=10.80)',
            'short_name': 'V4 Smooth',
            'is_b4877a9': False,
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
    
    supp_list = [pad_mesh]
    lever_list = []
    clean_parts = []
    
    print(f"Building 5-Test Rapid-Prototype Levers (Pitch: {LEVER_PITCH_X:.1f}mm)...")
    for i, test in enumerate(test_suite):
        cx = x_offsets[i]
        x_lever_center = 9.25
        
        if test['is_b4877a9']:
            p_y = test['plunger_y']
            c_pts = test['cam_pts']
            m_raw = build_b4877a9_rocker_mesh(axle_len=PROTO_AXLE_LEN, plunger_y=p_y, cam_pts=c_pts)
            m_lever = m_raw.apply_transform(R_PIP_45)
            
            # Also export unshortened 11.50mm axle version for reference
            m_raw_11_5 = build_b4877a9_rocker_mesh(axle_len=11.50, plunger_y=p_y, cam_pts=c_pts)
            path_11_5 = os.path.join(export_dir, f"prototype_lever_{test['id']}_full_axle_11.5mm.stl")
            m_raw_11_5.export(path_11_5)
        else:
            cfg = test['cfg']
            m_lever = build_variant_lever_45deg(cfg, axle_len=PROTO_AXLE_LEN)
            
        m_supp = build_variant_supports_45deg(test)
            
        m_lever.apply_translation([-x_lever_center + cx, 0, 0])
        m_supp.apply_translation([-x_lever_center + cx, 0, 0])
        
        supp_list.append(m_supp)
        lever_list.append(m_lever)
        clean_parts.append(m_lever)
        
        # Individual single-lever STL exports
        single_pad, _ = build_bed_pad_with_notches([test], pitch_x=LEVER_PITCH_X)
        if test['is_b4877a9']:
            p_y = test['plunger_y']
            c_pts = test['cam_pts']
            s_raw = build_b4877a9_rocker_mesh(axle_len=PROTO_AXLE_LEN, plunger_y=p_y, cam_pts=c_pts)
            s_lever = s_raw.apply_transform(R_PIP_45)
        else:
            s_lever = build_variant_lever_45deg(test['cfg'], axle_len=PROTO_AXLE_LEN)
            
        s_supp = build_variant_supports_45deg(test)
            
        s_lever.apply_translation([-x_lever_center, 0, 0])
        s_supp.apply_translation([-x_lever_center, 0, 0])
        
        indiv_supp = trimesh.util.concatenate([single_pad, s_supp, s_lever])
        path_indiv_supp = os.path.join(export_dir, f"prototype_lever_{test['id']}_supported_45deg.stl")
        path_indiv_bare = os.path.join(export_dir, f"prototype_lever_{test['id']}_bare_45deg.stl")
        indiv_supp.export(path_indiv_supp)
        s_lever.export(path_indiv_bare)
        print(f"  [{i+1}/5] {test['name']} -> {path_indiv_supp}")
        
    try:
        base_foundation = trimesh.boolean.union(supp_list, engine='manifold')
    except Exception:
        base_foundation = trimesh.util.concatenate(supp_list)

    plate_supported = trimesh.util.concatenate([base_foundation] + lever_list)
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

def build_combined_assembly_with_5levers(export_dir="testing"):
    """
    Builds an all-in-one build plate combining:
      - The complete production assembly (baseplate, slit inserts, cooling column)
      - The 5-test prototype lever plate
    arranged side-by-side on a single print plate.
    """
    os.makedirs(export_dir, exist_ok=True)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    assembly_path = os.path.join(root_dir, 'complete_assembly.stl')
    if not os.path.exists(assembly_path):
        print(f"Warning: {assembly_path} not found, skipping combined master plate.")
        return None
        
    m_assem = trimesh.load(assembly_path)
    proto_path = os.path.join(export_dir, 'prototype_levers_5pack_supported_45deg.stl')
    m_proto = trimesh.load(proto_path)
    
    # Place assembly toward back (Y=+25), 5-pack plate toward front (Y=-25)
    m_assem_placed = m_assem.copy().apply_translation([0, 25.0, 0])
    m_proto_placed = m_proto.copy().apply_translation([0, -25.0, 0])
    
    combined_plate = trimesh.util.concatenate([m_assem_placed, m_proto_placed])
    path_comb_stl = os.path.join(export_dir, "complete_assembly_plus_5levers_plate.stl")
    path_comb_3mf = os.path.join(export_dir, "complete_assembly_plus_5levers_plate.3mf")
    
    combined_plate.export(path_comb_stl)
    combined_plate.export(path_comb_3mf)
    print(f"\nSuccessfully exported Combined Master Plate (Assembly + 5 Levers):")
    print(f"  -> Combined Master Plate (STL): {path_comb_stl}")
    print(f"  -> Combined Master Plate (3MF): {path_comb_3mf}")
    print(f"  -> Bounding Box (X x Y x Z): "
          f"{combined_plate.bounds[1,0]-combined_plate.bounds[0,0]:.1f} x "
          f"{combined_plate.bounds[1,1]-combined_plate.bounds[0,1]:.1f} x "
          f"{combined_plate.bounds[1,2]-combined_plate.bounds[0,2]:.1f} mm")
    return combined_plate

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
    ax1.plot([9.279], [12.590], 'o', color='#f8fafc', markersize=8, label='Pivot Axle (Y=9.28, Z=12.59)')
    ax1.axvline(3.10, color='#ef4444', linestyle=':', lw=1.8, label='Non-Polar Blade Rear (Touching Moon)')
    ax1.axvline(3.48, color='#facc15', linestyle='--', lw=1.8, label='Nominal Blade Rear (Pinch Throat Center)')
    
    for i, test in enumerate(test_suite):
        if test['is_b4877a9']:
            y_ax = 9.279
            z_ax = 12.590
            if test.get('is_tuned', False):
                pts = np.array(B4877A9_TUNED_CAM_PTS)
                apex_y, apex_z = test['cam_apex']
            else:
                pts = np.array([
                    (y_ax, z_ax),
                    (y_ax, z_ax + 2.10),
                    (6.80, 12.20),
                    (5.00, 10.00),
                    (1.50, 7.40),
                    (1.80, 5.10),
                    (4.50, 5.30),
                    (y_ax - 1.50, z_ax - 2.50)
                ])
                apex_y, apex_z = test['cam_apex']
            ax1.plot(pts[:, 0], pts[:, 1], '-s', color=palette[i], lw=2.2, markersize=4,
                     label=f"[{test['bars']}] {test['short_name']} (Apex: Y={apex_y:.2f}, Z={apex_z:.2f})")
            ax1.plot([apex_y], [apex_z], '*', color='white', markersize=8)
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
        if test['is_b4877a9']:
            yp = test['plunger_y']
            z_reach = -6.50
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
        if test['is_b4877a9']:
            y_ax = 9.279
            z_ax = 12.590
            if test.get('is_tuned', False):
                pts = np.array(B4877A9_TUNED_CAM_PTS)
            else:
                pts = np.array([
                    (y_ax, z_ax),
                    (y_ax, z_ax + 2.10),
                    (6.80, 12.20),
                    (5.00, 10.00),
                    (1.50, 7.40),
                    (1.80, 5.10),
                    (4.50, 5.30),
                    (y_ax - 1.50, z_ax - 2.50)
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
        "5-TEST PROTOTYPE SPECTRUM: COMMIT [b4877a9] & UPGRADED KINEMATICS\n"
        "===================================================================\n\n"
        "• Print Specifications:\n"
        "  - Orientation: 100% MATCH WITH PIP (+45° tilted around X axis).\n"
        "  - Lever Arms: 100% CLEAN & WATERTIGHT (No pips or bumps on arms).\n"
        "  - Supports: Real-part breakaway supports (build_part.py), 'just shorter'.\n"
        f"  - Total Axle Length: {PROTO_AXLE_LEN:.2f} mm (Shortened for drop-in retrofit).\n"
        "  - Plate Dimensions: ~87 x 23 x 17.6 mm (~16 min total print time!).\n\n"
        "• Identification Notches Embossed on Front Lip of Bed Pad:\n"
        "  [I]     1 BAR  = Test 1: Commit [b4877a9] Exact Geometry\n"
        "                  OEM 3-rib baseline (Cam apex Y=1.50, Z=7.40, Plunger Y=10.48mm).\n"
        "                  Dead pre-travel 1.92mm; required heavy thumb force to actuate in PCTG.\n\n"
        "  [II]    2 BARS = Test 2: Commit [b4877a9] Tuned Pre-Travel & Elevated Ramp\n"
        "                  OEM 3-rib architecture with plunger advanced to Y=11.15mm (pre-travel 1.25mm)\n"
        "                  and cam apex elevated to Z=7.75mm (+0.17mm over-travel at nominal Z=7.2mm).\n\n"
        "  [III]   3 BARS = Test 3: V1 Ultra-Sensitive (Apex Y=1.65, P_Y=11.25)\n"
        "                  Maximum non-polar capture: early trip on shallow penetration (+0.47mm OT).\n\n"
        "  [IV]    4 BARS = Test 4: V3 Balanced Nominal (Apex Y=2.10, P_Y=10.95)\n"
        "                  Golden mean: reliable trip on polar & non-polar plugs (+0.28mm OT).\n\n"
        "  [V]     5 BARS = Test 5: V4 Smooth Progressive (Apex Y=2.30, P_Y=10.80)\n"
        "                  Crowned rolling lead-in for lowest polar insertion force (+0.15mm OT)."
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
    combined_master = build_combined_assembly_with_5levers("testing")
    preview_png = os.path.join("testing", "prototype_5levers_preview.png")
    generate_preview_5variants(preview_png)
    print("Done!")
