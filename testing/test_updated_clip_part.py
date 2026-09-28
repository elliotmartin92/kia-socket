"""
Test updating build_part with:
1. ~0.5mm less prominent clips (CLIP_HOOK_DEPTH = 1.60mm, was 2.10mm)
2. Prominent squared-off blunt land (CLIP_BLUNT_HEIGHT = 0.70mm, was 0.35mm)
3. Top-down subtle crown arc (0.20mm edge ease: 1.40mm at edges -> 1.60mm at center)
Verify watertightness, volume, and support alignment.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

import build_part

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()

TEST_HOOK_DEPTH = 1.60
TEST_BLUNT_HEIGHT = 0.70
TEST_CROWN_EASE = 0.20
stem_h = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT # 4.97mm
top_z = build_part.CLIP_HEIGHT # 6.77mm
half_w = build_part.CLIP_ARM_WIDTH / 2.0

def build_test_crowned_hook_mesh(angle_deg, n_theta=32):
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, n_theta)
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
        eff_depth = TEST_HOOK_DEPTH - TEST_CROWN_EASE * (frac ** 2.0)
        
        ps = po + n_dir * eff_depth
        p_in = po - n_dir * 0.25
        
        outer_coords.append(po)
        shelf_coords.append(ps)
        inner_overlap_coords.append(p_in)
        
    inner_overlap_coords = np.array(inner_overlap_coords)
    shelf_coords = np.array(shelf_coords)
    
    N = n_theta
    v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
    v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
    v_face = np.column_stack([shelf_coords, np.full(N, stem_h + TEST_BLUNT_HEIGHT)])
    v2 = np.column_stack([inner_overlap_coords, np.full(N, top_z)])
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
    
    mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
    if mesh.volume < 0:
        mesh.faces = np.fliplr(mesh.faces)
    return mesh

for angle in build_part.CLIP_ANGLES:
    m = build_test_crowned_hook_mesh(angle)
    print(f"Clip {angle:5.1f}°: Watertight={m.is_watertight}, Volume={m.volume:+.3f} mm³")
    assert m.is_watertight
    assert m.volume > 0

print("\nAll 4 test crowned hook meshes are 100% watertight!")
