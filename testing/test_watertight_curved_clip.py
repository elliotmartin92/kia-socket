"""
Test 100% watertight single-solid curved snap clip mesh.
"""
import math
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString
import trimesh

from build_part import (
    OUTER_WALL_THICK, OUTER_WALL_HEIGHT,
    CLIP_HEIGHT, CLIP_GAP_DEPTH, CLIP_ARM_WIDTH,
    CLIP_HOOK_DEPTH, CLIP_HOOK_HEIGHT, find_boundary_point_and_normal,
    get_exact_base_polygon
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

def build_single_solid_curved_clip(angle_deg):
    center_rad = math.radians(angle_deg)
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    
    N = 16
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
    
    inner_coords = []
    outer_coords = []
    shelf_coords = []
    
    for th in theta_vals:
        ray_dir = np.array([np.cos(th), np.sin(th)])
        ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
        
        # Outer intersection
        inter_out = outer_body_poly.exterior.intersection(ray)
        if inter_out.geom_type == 'Point':
            po = np.array([inter_out.x, inter_out.y])
        elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
            po = np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
        else:
            po = ray_dir * r_est
            
        # Inner intersection
        inter_in = inner_wall_poly.exterior.intersection(ray)
        if inter_in.geom_type == 'Point':
            pi = np.array([inter_in.x, inter_in.y])
        elif hasattr(inter_in, 'geoms') and len(inter_in.geoms) > 0:
            pi = np.array([inter_in.geoms[-1].x, inter_in.geoms[-1].y])
        else:
            pi = po - (po / np.linalg.norm(po)) * OUTER_WALL_THICK
            
        n_dir = po / np.linalg.norm(po)
        ps = po + n_dir * CLIP_HOOK_DEPTH
        
        inner_coords.append(pi)
        outer_coords.append(po)
        shelf_coords.append(ps)
        
    inner_coords = np.array(inner_coords)
    outer_coords = np.array(outer_coords)
    shelf_coords = np.array(shelf_coords)
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
    z_bot = 0.0
    z_top = CLIP_HEIGHT
    
    # Vertices arrays:
    # 0..N-1:      V0 = (inner, z_bot)
    # N..2N-1:     V1 = (outer, z_bot)
    # 2N..3N-1:    V2 = (outer, stem_h)
    # 3N..4N-1:    V3 = (shelf, stem_h)
    # 4N..5N-1:    V4 = (inner, z_top)
    v0 = np.column_stack([inner_coords, np.full(N, z_bot)])
    v1 = np.column_stack([outer_coords, np.full(N, z_bot)])
    v2 = np.column_stack([outer_coords, np.full(N, stem_h)])
    v3 = np.column_stack([shelf_coords, np.full(N, stem_h)])
    v4 = np.column_stack([inner_coords, np.full(N, z_top)])
    
    verts = np.vstack([v0, v1, v2, v3, v4])
    
    faces = []
    for i in range(N - 1):
        # 1. Bottom face (Z = 0): V0 -> V1 pointing -Z
        faces.append([i, i + 1, N + i + 1])
        faces.append([i, N + i + 1, N + i])
        
        # 2. Outer stem wall (Z: 0 to stem_h): V1 -> V2 pointing +radial
        faces.append([N + i, N + i + 1, 2*N + i + 1])
        faces.append([N + i, 2*N + i + 1, 2*N + i])
        
        # 3. Retention shelf (at stem_h): V2 -> V3 pointing -Z
        faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
        faces.append([2*N + i, 3*N + i + 1, 3*N + i])
        
        # 4. Slanted top bevel: V3 -> V4 pointing +radial/+Z
        faces.append([3*N + i, 3*N + i + 1, 4*N + i + 1])
        faces.append([3*N + i, 4*N + i + 1, 4*N + i])
        
        # 5. Inner curved face (Z: 0 to z_top): V4 -> V0 pointing -radial
        faces.append([4*N + i, 4*N + i + 1, i + 1])
        faces.append([4*N + i, i + 1, i])
        
    # Side endcaps (Left at i = 0, Right at i = N-1)
    # Left endcap (pointing -tangent):
    # Polygon formed by: v0[0] -> v1[0] -> v2[0] -> v3[0] -> v4[0]
    # Triangulate left cap:
    # (v0[0], v2[0], v1[0]), (v0[0], v3[0], v2[0]), (v0[0], v4[0], v3[0])
    faces.append([0, 2*N, N])
    faces.append([0, 3*N, 2*N])
    faces.append([0, 4*N, 3*N])
    
    # Right endcap (pointing +tangent):
    # Polygon formed by: v0[N-1] -> v4[N-1] -> v3[N-1] -> v2[N-1] -> v1[N-1]
    e0 = N - 1
    e1 = 2*N - 1
    e2 = 3*N - 1
    e3 = 4*N - 1
    e4 = 5*N - 1
    faces.append([e0, e1, e2])
    faces.append([e0, e2, e3])
    faces.append([e0, e3, e4])
    
    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
    return mesh

clip = build_single_solid_curved_clip(45)
print("Curved clip watertight status:", clip.is_watertight)
assert clip.is_watertight, "Mesh must be watertight!"
print("SUCCESS: 100% Watertight Curved Snap Clip created!")
