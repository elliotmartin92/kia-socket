import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import LineString
import build_part

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
poly_wall = outer_body_poly.difference(inner_wall_poly)
mesh_wall = trimesh.creation.extrude_polygon(poly_wall, height=build_part.OUTER_WALL_HEIGHT)

print(f"Initial wall: watertight={mesh_wall.is_watertight}, vol={mesh_wall.volume:.2f}")

for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    half_w = build_part.CLIP_ARM_WIDTH / 2.0
    hook_depth = build_part.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, build_part.CLIP_HOOK_DEPTH)
    stem_h = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT
    
    N = 32
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
            po = np.array([inter_out.x, inter_out.y]) if hasattr(inter_out, 'x') else np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
        else:
            po = ray_dir * r_est
            
        n_dir = po / np.linalg.norm(po)
        t = (th - center_rad) * r_est
        frac = abs(t / half_w)
        eff_depth = hook_depth - build_part.CLIP_CROWN_EASE * (frac ** 2.0)
        
        ps = po + n_dir * eff_depth
        p_in = po - n_dir * 0.25
        
        outer_coords.append(po)
        shelf_coords.append(ps)
        inner_overlap_coords.append(p_in)
        
    inner_overlap_coords = np.array(inner_overlap_coords)
    shelf_coords = np.array(shelf_coords)
    
    v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
    v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
    v_face = np.column_stack([shelf_coords, np.full(N, stem_h + build_part.CLIP_BLUNT_HEIGHT)])
    v2 = np.column_stack([inner_overlap_coords, np.full(N, build_part.CLIP_HEIGHT)])
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
        
    print(f"Hook {angle_deg}°: watertight={hm.is_watertight}, vol={hm.volume:.3f}")
    mesh_wall = mesh_wall.union(hm, engine='manifold')
    print(f"Wall after union with {angle_deg}°: watertight={mesh_wall.is_watertight}, vol={mesh_wall.volume:.2f}")

print("All hooks unioned cleanly into outer wall!")

# Now test slot cuts
slot_cuts = []
slot_t = build_part.CLIP_SLOT_CLEARANCE
z_root_center = build_part.OUTER_WALL_HEIGHT - build_part.CLIP_GAP_DEPTH + build_part.CLIP_ROOT_RADIUS

for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    slot_d_theta = slot_t / r_est
    
    for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
        slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
        rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
        box_h = (build_part.OUTER_WALL_HEIGHT + 1.0) - z_root_center
        s_box = trimesh.creation.box([build_part.OUTER_WALL_THICK * 4.0, slot_t, box_h])
        s_box.apply_transform(rot_mat)
        s_box.apply_translation([slot_p[0], slot_p[1], z_root_center + box_h / 2.0])
        
        cyl = trimesh.creation.cylinder(radius=build_part.CLIP_ROOT_RADIUS, height=build_part.OUTER_WALL_THICK * 4.0, sections=16)
        rot_to_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
        cyl.apply_transform(rot_to_x)
        cyl.apply_transform(rot_mat)
        cyl.apply_translation([slot_p[0], slot_p[1], z_root_center])
        
        slot_cuts.append(trimesh.util.concatenate([s_box, cyl]))

all_slot_cuts = trimesh.util.concatenate(slot_cuts)
wall_slotted = mesh_wall.difference(all_slot_cuts, engine='manifold')
print(f"Wall after cutting flex slots: watertight={wall_slotted.is_watertight}, vol={wall_slotted.volume:.2f}")

