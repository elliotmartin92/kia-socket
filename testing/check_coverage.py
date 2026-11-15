"""
Check exact geometric clearance and coverage between support prongs and shelf for Clip 327.5° vs Clip 211.3°.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    build_bottom_clip_45deg_supports_mesh,
    CLIP_ANGLES, CLIP_HOOK_DEPTH_BY_ANGLE, CLIP_HOOK_DEPTH,
    CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_CROWN_EASE,
    CLIP_BLUNT_HEIGHT
)

def check_coverage():
    base_poly, outer_poly, _ = get_exact_base_polygon()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT # 4.72 mm
    
    for angle_deg in [211.3, 327.5]:
        center_rad = np.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = CLIP_ARM_WIDTH / r_est
        hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        
        print(f"\n=======================================================")
        print(f"Coverage analysis for Clip {angle_deg}°:")
        print(f"=======================================================")
        
        # Build 3D mesh of the hook for this angle
        N = 32
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        half_w = CLIP_ARM_WIDTH / 2.0
        
        outer_coords = []
        shelf_coords = []
        for th in theta_vals:
            ray_dir = np.array([np.cos(th), np.sin(th)])
            po = ray_dir * r_est
            n_dir = po / np.linalg.norm(po)
            t = (th - center_rad) * r_est
            frac = abs(t / half_w)
            eff_depth = hook_depth - CLIP_CROWN_EASE * (frac ** 2.0)
            ps = po + n_dir * eff_depth
            shelf_coords.append(ps)
            outer_coords.append(po)
            
        shelf_coords = np.array(shelf_coords)
        outer_coords = np.array(outer_coords)
        
        # Get support mesh
        supports = build_bottom_clip_45deg_supports_mesh(base_poly)
        
        # Filter support for this clip
        matched_comps = []
        for c in supports.split():
            c_center = c.centroid
            ang = (np.degrees(np.arctan2(c_center[1], c_center[0])) + 360) % 360
            if abs(ang - angle_deg) < 15:
                matched_comps.append(c)
                
        print(f"Found {len(matched_comps)} support prongs for {angle_deg}°")
        
        # Check radial extent of shelf vs radial extent of support
        for idx, comp in enumerate(matched_comps):
            # Transform to local clip coords (R, T, Z)
            # Origin at p
            v = comp.vertices
            dv = v[:, :2] - p
            # Project onto u_r, u_t
            u_r = p / np.linalg.norm(p)
            u_t = np.array([-u_r[1], u_r[0]])
            
            r_proj = dv[:, 0] * u_r[0] + dv[:, 1] * u_r[1]
            t_proj = dv[:, 0] * u_t[0] + dv[:, 1] * u_t[1]
            z_proj = v[:, 2]
            
            print(f"  Prong {idx+1}:")
            print(f"    Tangential range (T): [{t_proj.min():.2f}, {t_proj.max():.2f}] mm (Clip arm half width = {half_w:.2f})")
            print(f"    Radial reach (R):      [{r_proj.min():.2f}, {r_proj.max():.2f}] mm (Hook depth = {hook_depth:.2f})")
            print(f"    Z range:               [{z_proj.min():.2f}, {z_proj.max():.2f}] mm (Shelf Z = {stem_h:.2f}, contact Z = 4.44)")
            
            # Check machine coordinates
            v_mach = (R[:3, :3] @ v.T).T
            print(f"    Machine Z' range:      [{v_mach[:, 2].min():.2f}, {v_mach[:, 2].max():.2f}] mm")

if __name__ == '__main__':
    check_coverage()
