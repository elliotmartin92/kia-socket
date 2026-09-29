"""
testing/test_bottom_clip_stem_support.py
Tests integrating the 45-degree support directly into the bottom clips (211.3° and 327.5°)
coming out of the stem.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString
import matplotlib.pyplot as plt

import build_part as bp

def run_test():
    base_poly, outer_body_poly, _ = bp.get_exact_base_polygon()
    
    # Check bottom clips
    for angle_deg in [211.3, 327.5]:
        center_rad = math.radians(angle_deg)
        p, norm, tang = bp.find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = bp.CLIP_ARM_WIDTH / r_est
        hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, bp.CLIP_HOOK_DEPTH)
        stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT
        
        N = 32
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        half_w = bp.CLIP_ARM_WIDTH / 2.0
        
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
            eff_depth = hook_depth - bp.CLIP_CROWN_EASE * (frac ** 2.0)
            
            ps = po + n_dir * eff_depth
            p_in = po - n_dir * 0.25
            
            outer_coords.append(po)
            shelf_coords.append(ps)
            inner_overlap_coords.append(p_in)
            
        inner_overlap_coords = np.array(inner_overlap_coords)
        shelf_coords = np.array(shelf_coords)
        
        # Bottom clips have 45° support coming out of stem:
        z_stem_start = stem_h - hook_depth
        v0 = np.column_stack([inner_overlap_coords, np.full(N, z_stem_start)])
        v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
        v_face = np.column_stack([shelf_coords, np.full(N, stem_h + bp.CLIP_BLUNT_HEIGHT)])
        v2 = np.column_stack([inner_overlap_coords, np.full(N, bp.CLIP_HEIGHT)])
        hook_verts = np.vstack([v0, v1, v_face, v2])
        
        hook_faces = []
        for i in range(N - 1):
            hook_faces.append([i, N + i + 1, N + i])
            hook_faces.append([i, i + 1, N + i + 1])
            hook_faces.append([N + i, 2*N + i + 1, 2*N + i])
            hook_faces.append([N + i, N + i + 1, 2*N + i + 1])
            hook_faces.append([2*N + i, 3*N + i + 1, 3*N + i])
            hook_faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
            hook_faces.append([3*N + i, i + 1, i])
            hook_faces.append([3*N + i, 3*N + i + 1, i + 1])
            
        hook_faces.append([0, 2*N, 3*N])
        hook_faces.append([0, N, 2*N])
        hook_faces.append([N - 1, 3*N - 1, 2*N - 1])
        hook_faces.append([N - 1, 4*N - 1, 3*N - 1])
        
        hook_mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
        if hook_mesh.volume < 0:
            hook_mesh.faces = np.fliplr(hook_mesh.faces)
            
        print(f"Angle {angle_deg}: Hook mesh watertight = {hook_mesh.is_watertight}, vol = {hook_mesh.volume:.2f} mm³")
        print(f"  Z bounds: [{hook_mesh.bounds[0,2]:.2f}, {hook_mesh.bounds[1,2]:.2f}] (starts at Z={z_stem_start:.2f} on stem)")

if __name__ == '__main__':
    run_test()
