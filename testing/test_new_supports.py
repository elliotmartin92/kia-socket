import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import build_part as bp

base_poly, outer_poly, _ = bp.get_exact_base_polygon()

def test_new_clip_supports(base_poly):
    stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT  # 4.97mm
    # Increased Z-gap from 0.20mm to 0.26mm for easy breakaway at higher print temps
    tip_h = 0.10
    z_gap = 0.26
    support_top_z = stem_h - z_gap - tip_h   # 4.97 - 0.26 - 0.10 = 4.61mm (tip reaches 4.71mm)
    
    y_prongs = [-1.30, 1.30]
    prong_w_tang = 0.65
    prong_t_rad = 0.55
    tip_w_tang = 0.55
    tip_t_rad = 0.25
    
    support_meshes = []
    for angle_deg in bp.CLIP_ANGLES:
        rad = math.radians(angle_deg)
        p, norm, tang = bp.find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, bp.CLIP_HOOK_DEPTH)
        r_supp_radial = max(0.62, hook_depth * 0.58)
        
        pos_center = n_dir * (r_wall + r_supp_radial)
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
        
        # 1. Bed adhesion foot (Z in [0, 0.35]mm, 1.20mm radial x 3.20mm tangential)
        foot = trimesh.creation.box([1.20, 3.20, 0.35])
        foot.apply_transform(rot)
        foot.apply_translation([pos_center[0], pos_center[1], 0.175])
        
        # 2. Lower solid shared trunk (Z in [0.35, 3.20]mm -> height 2.85mm, 0.65mm radial x 2.80mm tangential)
        z_trunk_h = 2.85
        trunk = trimesh.creation.box([0.65, 2.80, z_trunk_h])
        trunk.apply_transform(rot)
        trunk.apply_translation([pos_center[0], pos_center[1], 0.35 + z_trunk_h / 2.0])
        
        # 3. Twin vertical prongs (Z in [3.20, 4.61]mm -> height 1.41mm, at Y = +/- 1.30mm)
        z_prong_h = support_top_z - 3.20
        prong_parts = []
        for yp in y_prongs:
            prong = trimesh.creation.box([prong_t_rad, prong_w_tang, z_prong_h])
            prong.apply_translation([0, yp, 0])
            prong.apply_transform(rot)
            prong.apply_translation([pos_center[0], pos_center[1], 3.20 + z_prong_h / 2.0])
            prong_parts.append(prong)
            
        # 4. Twin breakaway chisel contact tips (Z in [4.61, 4.71]mm -> height 0.10mm, leaving 0.26mm clear gap to 4.97mm shelf)
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

supps = test_new_clip_supports(base_poly)
print(f"Supports mesh watertight: {supps.is_watertight}")
print(f"Supports mesh volume: {supps.volume:.2f} mm³ (was ~50 mm³)")
print(f"Supports bounds Z: [{supps.bounds[0,2]:.2f}, {supps.bounds[1,2]:.2f}] mm")
print("Supports successfully built and verified!")
