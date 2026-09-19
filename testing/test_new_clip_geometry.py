import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import LineString
import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

CLIP_HEIGHT = 6.77
CLIP_HOOK_HEIGHT = 1.80
CLIP_ARM_WIDTH = 4.20
CLIP_HOOK_DEPTH = 2.39  # 0.10mm less protrusion
BLUNT_H = 0.35          # 0.35mm vertical faced-off land
stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm

for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    
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
    v_face = np.column_stack([shelf_coords, np.full(N, stem_h + BLUNT_H)])
    v2 = np.column_stack([outer_coords, np.full(N, CLIP_HEIGHT)])
    hook_verts = np.vstack([v0, v1, v_face, v2])
    
    hook_faces = []
    for i in range(N - 1):
        # 1. Retention shelf (at stem_h, pointing -Z): V0 -> V1
        hook_faces.append([i, N + i + 1, N + i])
        hook_faces.append([i, i + 1, N + i + 1])
        
        # 2. Faced-off vertical blunt tip: V1 -> V_face
        hook_faces.append([N + i, 2*N + i + 1, 2*N + i])
        hook_faces.append([N + i, N + i + 1, 2*N + i + 1])
        
        # 3. Slanted lead-in ramp: V_face -> V2
        hook_faces.append([2*N + i, 3*N + i + 1, 3*N + i])
        hook_faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
        
        # 4. Inner mating face (at outer wall): V2 -> V0
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
    print(f"Angle {angle_deg:5.1f}° hook: Watertight={hook_mesh.is_watertight}, Volume={hook_mesh.volume:+.3f} mm³")
    assert hook_mesh.is_watertight, f"Hook at {angle_deg}° not watertight!"
    assert hook_mesh.volume > 0, f"Hook at {angle_deg}° volume must be positive!"
print("All 4 faced-off hook meshes are 100% watertight with positive volume!")
