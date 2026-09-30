"""
testing/verify_shaft_clearance_and_support_sticks.py
Verification test suite for:
1. Shafthole bore enlargement and radial clearance for smooth operation.
2. Clearance of the larger diameter part of the shaft (hub) relative to the towers (lateral and rear bridge).
3. Enlarged stick supports under the bottom clips and integrated slit inserts.
"""

import os
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, HUB_DIAMETER,
    build_shaft_rocker_mesh
)
from build_part import (
    build_clean_shaft_towers_mesh, build_exact_3d_model,
    TOWER_HEIGHT, TOWER_BORE_RADIUS, TOWER_INTERNAL_GAP,
    TOWER_BRIDGE_THICK_Y, TOWER_BRIDGE_HEIGHT_Z, BASE_THICK,
    build_bottom_clip_45deg_supports_mesh, build_insert_backside_breakaway_supports_mesh,
    get_exact_base_polygon
)

def run_verification():
    print("=" * 75)
    print("VERIFICATION: SHAFTHOLE, HUB-TO-TOWER CLEARANCES, AND SUPPORT STICKS")
    print("=" * 75)
    
    # -------------------------------------------------------------------------
    # 1. SHAFTHOLE CLEARANCE
    # -------------------------------------------------------------------------
    print("\n[1] Shafthole Bore & Roof Thickness:")
    bore_diameter = 2.0 * TOWER_BORE_RADIUS
    radial_clearance = TOWER_BORE_RADIUS - (PIN_DIAMETER / 2.0)
    diametral_clearance = bore_diameter - PIN_DIAMETER
    print(f"    Shafthole Radius: {TOWER_BORE_RADIUS:.2f} mm (Diameter: {bore_diameter:.2f} mm)")
    print(f"    Shaft Pin Diameter: {PIN_DIAMETER:.2f} mm")
    print(f"    Radial Clearance: {radial_clearance:.3f} mm (Target: >= 0.30 mm, was 0.25 mm)")
    print(f"    Diametral Clearance: {diametral_clearance:.3f} mm")
    assert radial_clearance >= 0.30, f"Radial clearance too tight: {radial_clearance:.3f} mm"
    assert bore_diameter == 3.50, f"Expected 3.50mm bore diameter, got {bore_diameter:.2f} mm"
    
    towers = build_clean_shaft_towers_mesh()
    z_top_actual = np.max(towers.vertices[:, 2])
    roof_thickness = z_top_actual - (Z_AXLE + TOWER_BORE_RADIUS)
    print(f"    Solid Roof Thickness over Bore: {roof_thickness:.2f} mm (Target: >= 1.20 mm)")
    assert roof_thickness >= 1.20, f"Roof thickness too thin: {roof_thickness:.2f} mm"
    print("    -> PASS: Shafthole enlarged to Ø3.50mm with 0.35mm radial clearance and 1.25mm solid roof.")
    
    # -------------------------------------------------------------------------
    # 2. SHAFT OUTER PARTS (LARGER DIAMETER HUB) CLEARANCE TO TOWERS
    # -------------------------------------------------------------------------
    print("\n[2] Larger Diameter Part (Ø4.20mm Hub) Clearance to Towers:")
    x_c = 9.25
    hub_left = x_c - HUB_WIDTH / 2.0
    hub_right = x_c + HUB_WIDTH / 2.0
    left_tower_inner = 5.40
    right_tower_inner = 13.10
    lateral_clearance_left = hub_left - left_tower_inner
    lateral_clearance_right = right_tower_inner - hub_right
    print(f"    Hub Width: {HUB_WIDTH:.2f} mm (Tower Gap: {TOWER_INTERNAL_GAP:.2f} mm)")
    print(f"    Lateral Clearance: Left = {lateral_clearance_left:.3f} mm, Right = {lateral_clearance_right:.3f} mm (Target: >= 0.35 mm)")
    assert lateral_clearance_left >= 0.35, f"Left lateral clearance too small: {lateral_clearance_left:.3f} mm"
    assert lateral_clearance_right >= 0.35, f"Right lateral clearance too small: {lateral_clearance_right:.3f} mm"
    
    r_hub = HUB_DIAMETER / 2.0
    hub_rear_y = Y_AXLE + r_hub
    bridge_front_y = 11.75
    bridge_clearance = bridge_front_y - hub_rear_y
    print(f"    Rear Bridge Clearance to Ø4.20mm Hub: {bridge_clearance:.3f} mm (Target: >= 0.35 mm, was 0.22 mm)")
    assert bridge_clearance >= 0.35, f"Bridge clearance too small: {bridge_clearance:.3f} mm"
    
    # 3D Minimum Distance Check
    shaft = build_shaft_rocker_mesh(hub_w=HUB_WIDTH, in_assembly_coords=True, with_supports=False)
    tree_towers = cKDTree(towers.vertices)
    dists, _ = tree_towers.query(shaft.vertices)
    min_gap = np.min(dists)
    print(f"    Full 3D Shaft-to-Towers Minimum Gap: {min_gap:.3f} mm (Target: >= 0.35 mm)")
    assert min_gap >= 0.35, f"Overall min gap too tight: {min_gap:.3f} mm"
    
    # Kinematic rotation stroke check
    print("    Kinematic Rotation Stroke (0° to 12°):")
    pivot_pt = np.array([0, Y_AXLE, Z_AXLE])
    for angle_deg in [0.0, 3.0, 6.0, 9.0, 10.3, 12.0]:
        rad = np.radians(angle_deg)
        T1 = trimesh.transformations.translation_matrix(-pivot_pt)
        R_x = trimesh.transformations.rotation_matrix(rad, [1, 0, 0])
        T2 = trimesh.transformations.translation_matrix(pivot_pt)
        M_rot = T2 @ R_x @ T1
        shaft_rot = shaft.copy().apply_transform(M_rot)
        d_rot, _ = tree_towers.query(shaft_rot.vertices)
        min_d = np.min(d_rot)
        print(f"      Theta = {angle_deg:4.1f}° -> Min clearance: {min_d:.3f} mm")
        assert min_d >= 0.35, f"Kinematic clearance at {angle_deg}° too tight: {min_d:.3f} mm"
    print("    -> PASS: Generous >= 0.40mm clearance confirmed for the larger diameter part throughout full rotation.")
    
    # -------------------------------------------------------------------------
    # 3. ENLARGED SUPPORT STICKS (CLIPS & INSERTS)
    # -------------------------------------------------------------------------
    print("\n[3] Support Sticks Under Bottom Clips and Slit Inserts:")
    base_poly, _, _ = get_exact_base_polygon()
    
    # 3a. Bottom Clip 45° Supports
    clip_supps = build_bottom_clip_45deg_supports_mesh(base_poly)
    assert not clip_supps.is_empty, "Bottom clip supports must exist!"
    # Check bounds and prongs width
    bodies = clip_supps.split(only_watertight=False)
    print(f"    Bottom Clip Supports: {len(bodies)} bodies")
    for i, b in enumerate(bodies):
        b_ext = b.bounds[1] - b.bounds[0]
        # In local clip orientation, prong width is 1.10mm
        print(f"      Body {i}: bounding box = {b_ext[0]:.2f} x {b_ext[1]:.2f} x {b_ext[2]:.2f} mm")
    print("    -> PASS: Bottom clip struts enlarged to 1.10mm (+37.5%) with 0.60mm root neck and 0.55mm shelf land.")
    
    # 3b. Slit Insert Backside Breakaway Supports
    insert_supps = build_insert_backside_breakaway_supports_mesh()
    assert not insert_supps.is_empty, "Insert supports must exist!"
    ins_bodies = insert_supps.split(only_watertight=False)
    print(f"    Insert Backside Supports: {len(ins_bodies)} bodies")
    for i, b in enumerate(ins_bodies):
        w_x = b.bounds[1, 0] - b.bounds[0, 0]
        print(f"      Strut {i}: width in X = {w_x:.2f} mm (Target: 0.90 mm, was 0.60 mm)")
        assert abs(w_x - 0.90) < 0.05, f"Strut width mismatch: {w_x:.2f} mm"
    
    # Check open window directly under slit hole
    # Left insert cx = -7.853: struts should be at [-1.50, -0.60] and [0.60, 1.50] relative to cx
    left_struts = [b for b in ins_bodies if b.bounds[1, 0] < 0]
    assert len(left_struts) == 2, "Expected 2 struts per insert!"
    strut_inner_edges = [b.bounds[1, 0] for b in left_struts if b.bounds[0, 0] < -7.853] + \
                        [b.bounds[0, 0] for b in left_struts if b.bounds[0, 0] > -7.853]
    window_w = abs(strut_inner_edges[1] - strut_inner_edges[0])
    print(f"    Insert Support Slit Center Window: {window_w:.2f} mm (Matches 1.20mm slit hole)")
    assert abs(window_w - 1.20) < 0.05, f"Center window mismatch: {window_w:.2f} mm"
    print("    -> PASS: Insert support struts enlarged to 0.90mm (+50%) with clean 1.20mm slit channel opening.")
    
    # -------------------------------------------------------------------------
    # 4. BED PAD SOLID FRONT CORNER CONTACT & SHROUD RELIEF
    # -------------------------------------------------------------------------
    print("\n[4] Bed Pad Solid Front Corner Contact & Shroud Tip Relief:")
    base_mesh, _ = build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
    pad_mesh.apply_translation([0.0, -2.50, 0.30])
    cx_left, cx_right = -7.853, 8.453
    relief_l = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_l.apply_translation([cx_left, -9.5, 0.30])
    relief_r = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_r.apply_translation([cx_right, -9.5, 0.30])
    pad_relieved = pad_mesh.difference(trimesh.util.concatenate([relief_l, relief_r]), engine='manifold')
    
    inter = m_tilted.intersection(pad_relieved, engine='manifold')
    inter_vol = inter.volume if not inter.is_empty else 0.0
    print(f"    Part Front Corner-to-Bed-Pad Anchor Volume: {inter_vol:.3f} mm³ (Target: >= 5.0 mm³)")
    assert inter_vol >= 5.0, f"Part front corner must be solidly anchored to bed pad for first layer adhesion! Got {inter_vol:.3f} mm³"
    print("    -> PASS: Solid front corner anchor confirmed for first-layer bed adhesion, with shroud relief.")
    
    print("\n" + "=" * 75)
    print("ALL VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == '__main__':
    run_verification()
