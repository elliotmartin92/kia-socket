import sys
sys.path.insert(0, '.')
import trimesh
import numpy as np
import math
from shapely.geometry import LineString
import build_part
from build_part import get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT, BASE_THICK, CLIP_ANGLES, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_HOOK_DEPTH, CLIP_BLUNT_HEIGHT, CLIP_ARM_WIDTH, find_boundary_point_and_normal

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
all_walls_poly = outer_body_poly.difference(inner_poly)
mesh_wall = build_part.extrude_shapely_geom(all_walls_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
mesh_wall.apply_translation([0, 0, BASE_THICK])

stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT
N = 16

hooks = []
for angle_deg in CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
    
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
            po = np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
        else:
            po = ray_dir * r_est
        n_dir = po / np.linalg.norm(po)
        ps = po + n_dir * CLIP_HOOK_DEPTH
        # Overlap inward into the wall by 0.20mm so the boolean union dissolves the interface completely!
        p_in = po - n_dir * 0.20
        
        outer_coords.append(po)
        shelf_coords.append(ps)
        inner_overlap_coords.append(p_in)
        
    inner_overlap_coords = np.array(inner_overlap_coords)
    shelf_coords = np.array(shelf_coords)
    
    v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
    v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
    v_face = np.column_stack([shelf_coords, np.full(N, stem_h + CLIP_BLUNT_HEIGHT)])
    v2 = np.column_stack([inner_overlap_coords, np.full(N, CLIP_HEIGHT)])
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
    
    hm = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
    if hm.volume < 0:
        hm.faces = np.fliplr(hm.faces)
    hooks.append(hm)

print(f"Created {len(hooks)} overlapping hook meshes.")
# Boolean union with mesh_wall
united_wall = mesh_wall
for h in hooks:
    united_wall = united_wall.union(h, engine='manifold')

print("United wall watertight:", united_wall.is_watertight)
print("United wall volume:", united_wall.volume)
bodies = united_wall.split(only_watertight=False)
print(f"Number of separate bodies in united wall: {len(bodies)} (should be 1!)")
