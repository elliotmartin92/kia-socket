import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
import build_part

# Let's verify monkey-patched full build_exact_3d_model
CLIP_HEIGHT = 6.77
CLIP_HOOK_HEIGHT = 1.80
CLIP_ARM_WIDTH = 4.20
CLIP_HOOK_DEPTH = 2.39   # -0.10mm faced-off
BLUNT_H = 0.35           # 0.35mm vertical flat face
CLIP_GAP_DEPTH = 5.47    # Z reaches 1.30mm (5.47mm flex length)
r_root = 0.40            # 0.80mm diameter circular root
slot_t = build_part.CLIP_SLOT_CLEARANCE

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
wall_2d = outer_body_poly.difference(inner_wall_poly)

mesh_base = trimesh.creation.extrude_polygon(base_poly, height=build_part.BASE_THICK)
mesh_wall = trimesh.creation.extrude_polygon(wall_2d, height=CLIP_HEIGHT - build_part.BASE_THICK)
mesh_wall.apply_translation([0, 0, build_part.BASE_THICK])

# Brackets & ribs
all_brackets_poly = build_part.create_all_brackets_poly()
mesh_brackets = build_part.extrude_shapely_geom(all_brackets_poly, height=build_part.BRACKET_HEIGHT)
mesh_brackets.apply_translation([0, 0, build_part.BASE_THICK])

all_ribs_poly = build_part.create_grid_ribs_poly(base_poly)
mesh_ribs = build_part.extrude_shapely_geom(all_ribs_poly, height=build_part.RIB_HEIGHT)
mesh_ribs.apply_translation([0, 0, build_part.BASE_THICK])

seating_ribs_poly = build_part.create_bracket_seating_ribs_poly()
mesh_seating_ribs = build_part.extrude_shapely_geom(seating_ribs_poly, height=build_part.BRACKET_SEATING_RIB_THICK)
mesh_seating_ribs.apply_translation([0, 0, build_part.BASE_THICK])

# Towers assembly
mesh_towers = build_part.build_clean_shaft_towers_mesh()
mesh_struts = build_part.build_left_tower_struts_mesh()
mesh_towers_assembly = trimesh.util.concatenate([mesh_towers, mesh_struts])

# 45 deg clip clearance relief on towers
p45, norm45, _ = build_part.find_boundary_point_and_normal(base_poly, 45.0)
center_rad_45 = math.radians(45.0)
clearance_box = trimesh.creation.box([build_part.CLIP_ARM_WIDTH + 1.0, 3.0, 7.0])
rot_45 = trimesh.transformations.rotation_matrix(center_rad_45, [0, 0, 1])
clearance_box.apply_transform(rot_45)
p_cut = p45 - norm45 * (build_part.OUTER_WALL_THICK + 1.0)
clearance_box.apply_translation([p_cut[0], p_cut[1], 3.5 + build_part.BASE_THICK])
mesh_towers_assembly = mesh_towers_assembly.difference(clearance_box, engine='manifold')

# Slots and hooks
slot_cuts = []
hook_meshes = []
stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
slot_z_bot = CLIP_HEIGHT - CLIP_GAP_DEPTH  # 1.30mm
z_root_center = slot_z_bot + r_root        # 1.70mm

for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    slot_d_theta = slot_t / r_est
    
    # Radiused slots
    for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
        slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
        rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
        
        box_h = (CLIP_HEIGHT + 1.0) - z_root_center
        s_box = trimesh.creation.box([build_part.OUTER_WALL_THICK * 4.0, slot_t, box_h])
        s_box.apply_transform(rot_mat)
        s_box.apply_translation([slot_p[0], slot_p[1], z_root_center + box_h / 2.0])
        
        cyl = trimesh.creation.cylinder(radius=r_root, height=build_part.OUTER_WALL_THICK * 4.0, sections=16)
        rot_to_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
        cyl.apply_transform(rot_to_x)
        cyl.apply_transform(rot_mat)
        cyl.apply_translation([slot_p[0], slot_p[1], z_root_center])
        
        slot_cutter = trimesh.util.concatenate([s_box, cyl])
        slot_cuts.append(slot_cutter)
        
    # Faced-off hook wedge
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
    hook_meshes.append(hook_mesh)

all_slot_cuts = trimesh.util.concatenate(slot_cuts)
mesh_wall = mesh_wall.difference(all_slot_cuts, engine='manifold')
mesh_towers_assembly = mesh_towers_assembly.difference(all_slot_cuts, engine='manifold')

# Center curved feature
curved_feat_poly = build_part.create_center_curved_feature_poly()
mesh_curved_feat = build_part.extrude_shapely_geom(curved_feat_poly, height=10.50 - build_part.BASE_THICK)
mesh_curved_feat.apply_translation([0, 0, build_part.BASE_THICK])

# Supports
build_part.CLIP_HOOK_DEPTH = CLIP_HOOK_DEPTH
mesh_clip_supports = build_part.build_clip_supports_mesh(base_poly)

full_part = trimesh.util.concatenate([
    mesh_base, mesh_wall, mesh_ribs, mesh_brackets, mesh_seating_ribs,
    mesh_towers_assembly, mesh_curved_feat, mesh_clip_supports
] + hook_meshes)

print(f"Full part watertight: {full_part.is_watertight}")
print(f"Full part volume: {full_part.volume:.2f} mm³")
print(f"Full part bounds: {full_part.bounds}")
assert full_part.is_watertight
print("INTEGRATED PART VERIFICATION PASSED 100%!")
