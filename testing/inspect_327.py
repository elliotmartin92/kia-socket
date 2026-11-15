"""
Inspect Clip 327.5° slice and layers in machine build coordinates.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_HOOK_DEPTH_BY_ANGLE, CLIP_HOOK_DEPTH,
    CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_CROWN_EASE,
    CLIP_BLUNT_HEIGHT
)

def inspect_327():
    base_poly, outer_poly, _ = get_exact_base_polygon()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    
    # Let's inspect the hook geometry at 327.5
    angle_deg = 327.5
    center_rad = np.radians(angle_deg)
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT # 4.72 mm
    
    # Look at theta range:
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, 32)
    
    print(f"Clip 327.5°:")
    print(f"  Center Rad: {np.degrees(center_rad):.2f}°")
    print(f"  Theta span: [{np.degrees(theta_vals[0]):.2f}°, {np.degrees(theta_vals[-1]):.2f}°]")
    
    # In machine coordinates:
    # Build layers are planes of Z' = constant.
    # As Z' increases from bed (Z'=0) upwards:
    # What Z' elevation are the vertices of the hook at 327.5°?
    
    # Let's check hook vertices in machine space:
    v_shelf = []
    v_blunt = []
    v_top = []
    
    for th in theta_vals:
        ray_dir = np.array([np.cos(th), np.sin(th)])
        po = ray_dir * r_est
        n_dir = po / np.linalg.norm(po)
        half_w = CLIP_ARM_WIDTH / 2.0
        t = (th - center_rad) * r_est
        frac = abs(t / half_w)
        eff_depth = hook_depth - CLIP_CROWN_EASE * (frac ** 2.0)
        ps = po + n_dir * eff_depth
        
        # Shelf point (ps, stem_h)
        p_shelf_part = np.array([ps[0], ps[1], stem_h])
        p_blunt_part = np.array([ps[0], ps[1], stem_h + CLIP_BLUNT_HEIGHT])
        p_top_part   = np.array([po[0], po[1], CLIP_HEIGHT])
        
        v_shelf.append(R[:3, :3] @ p_shelf_part)
        v_blunt.append(R[:3, :3] @ p_blunt_part)
        v_top.append(R[:3, :3] @ p_top_part)
        
    v_shelf = np.array(v_shelf)
    v_blunt = np.array(v_blunt)
    v_top = np.array(v_top)
    
    print(f"  Machine Z' range:")
    print(f"    Shelf: [{v_shelf[:, 2].min():.2f}, {v_shelf[:, 2].max():.2f}] mm")
    print(f"    Blunt: [{v_blunt[:, 2].min():.2f}, {v_blunt[:, 2].max():.2f}] mm")
    print(f"    Top:   [{v_top[:, 2].min():.2f}, {v_top[:, 2].max():.2f}] mm")
    
    # Notice the order of printing in machine Z'!
    # Which feature prints first as Z' increases?
    # Look at the Z' values!
    z_min_overall = min(v_shelf[:, 2].min(), v_blunt[:, 2].min(), v_top[:, 2].min())
    print(f"    Lowest Z' feature of the hook: {z_min_overall:.2f} mm")
    
    # Also let's check the support for 327.5 in machine space:
    from build_part import build_bottom_clip_45deg_supports_mesh
    supports = build_bottom_clip_45deg_supports_mesh(base_poly)
    supp_mach = supports.copy().apply_transform(R)
    
    # Find components for 327.5
    for c in supp_mach.split():
        c_part = c.copy().apply_transform(np.linalg.inv(R))
        angle_c = (np.degrees(np.arctan2(c_part.centroid[1], c_part.centroid[0])) + 360) % 360
        if 315 < angle_c < 340:
            print(f"  Support component machine Z' bounds: [{c.bounds[0,2]:.2f}, {c.bounds[1,2]:.2f}], part centroid: {c_part.centroid[:2]}")

if __name__ == '__main__':
    inspect_327()
