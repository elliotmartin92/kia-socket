import trimesh
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# Build full monolithic model with in-place shrouds
def build_monolithic_part_model():
    base_poly, outer_body_poly, hole_info = bp.get_exact_base_polygon()
    
    # 1. Base plate with slit holes (no detent sockets)
    cx_left, cx_right, cy = -7.853, 8.453, -13.589
    w_slit, len_slit = bp.SLIT_W_X, bp.SLIT_LEN_Y
    
    hole_box = box(hole_info[0] - hole_info[2]/2, hole_info[1] - hole_info[3]/2,
                   hole_info[0] + hole_info[2]/2, hole_info[1] + hole_info[3]/2)
    slit_hole_l = box(cx_left - w_slit/2, cy - len_slit/2, cx_left + w_slit/2, cy + len_slit/2)
    slit_hole_r = box(cx_right - w_slit/2, cy - len_slit/2, cx_right + w_slit/2, cy + len_slit/2)
    
    base_poly_clean = outer_body_poly.difference(unary_union([hole_box, slit_hole_l, slit_hole_r]))
    mesh_base = bp.extrude_shapely_geom(base_poly_clean, height=bp.BASE_THICK)
    
    # In-place backside slit shrouds (Z: -2.47mm to 0.00mm)
    shroud_l = bp.create_frustum_mesh(bp.INSERT_BODY_W_TIP, bp.INSERT_BODY_LEN_TIP, bp.INSERT_BODY_W_X, bp.INSERT_BODY_LEN_Y, -bp.SLIT_BOSS_HEIGHT, 0.0)
    shroud_l.apply_translation([cx_left, cy, 0.0])
    shroud_r = bp.create_frustum_mesh(bp.INSERT_BODY_W_TIP, bp.INSERT_BODY_LEN_TIP, bp.INSERT_BODY_W_X, bp.INSERT_BODY_LEN_Y, -bp.SLIT_BOSS_HEIGHT, 0.0)
    shroud_r.apply_translation([cx_right, cy, 0.0])
    
    slit_cutter_l = bp.extrude_shapely_geom(slit_hole_l, height=bp.SLIT_BOSS_HEIGHT + 2.0)
    slit_cutter_l.apply_translation([0, 0, -bp.SLIT_BOSS_HEIGHT - 1.0])
    shroud_l_hollow = shroud_l.difference(slit_cutter_l, engine='manifold')
    
    slit_cutter_r = bp.extrude_shapely_geom(slit_hole_r, height=bp.SLIT_BOSS_HEIGHT + 2.0)
    slit_cutter_r.apply_translation([0, 0, -bp.SLIT_BOSS_HEIGHT - 1.0])
    shroud_r_hollow = shroud_r.difference(slit_cutter_r, engine='manifold')
    
    mesh_shrouds = trimesh.util.concatenate([shroud_l_hollow, shroud_r_hollow])
    
    # 2. Outer Rim Wall + Arch Wall
    inner_poly = outer_body_poly.buffer(-bp.OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_poly)
    arch_wall_poly = bp.create_arch_wall_poly()
    all_walls_poly = unary_union([wall_poly, arch_wall_poly])
    mesh_wall = bp.extrude_shapely_geom(all_walls_poly, height=bp.OUTER_WALL_HEIGHT - bp.BASE_THICK)
    mesh_wall.apply_translation([0, 0, bp.BASE_THICK])
    
    # 3. Floor Grid Ribbing
    all_ribs_poly = bp.create_grid_ribs_poly(base_poly_clean, outer_body_poly)
    bridge_box = box(13.10, 8.5, 25.0, 14.0)
    bridge_ribs_poly = all_ribs_poly.intersection(bridge_box)
    normal_ribs_poly = all_ribs_poly.difference(bridge_box)
    mesh_normal_ribs = bp.extrude_shapely_geom(normal_ribs_poly, height=bp.RIB_HEIGHT)
    mesh_normal_ribs.apply_translation([0, 0, bp.BASE_THICK])
    mesh_bridge_ribs = bp.extrude_shapely_geom(bridge_ribs_poly, height=bp.OUTER_WALL_HEIGHT - bp.BASE_THICK)
    mesh_bridge_ribs.apply_translation([0, 0, bp.BASE_THICK])
    mesh_ribs = trimesh.util.concatenate([mesh_normal_ribs, mesh_bridge_ribs])
    
    # 4. Guide Brackets & Seating Ribs
    brackets_poly = bp.create_all_brackets_poly()
    mesh_brackets = bp.extrude_shapely_geom(brackets_poly, height=bp.BRACKET_HEIGHT)
    mesh_brackets.apply_translation([0, 0, bp.BASE_THICK])
    mesh_seating_ribs = bp.build_chamfered_seating_ribs_mesh()
    
    # 5. Shaft Support Towers & Struts
    mesh_towers = bp.build_clean_shaft_towers_mesh()
    mesh_struts = bp.build_left_tower_struts_mesh()
    mesh_towers_assembly = trimesh.util.concatenate([mesh_towers, mesh_struts])
    
    # Relief on Right Tower behind 45 clip
    p45, norm45, _ = bp.find_boundary_point_and_normal(base_poly_clean, 45.0)
    center_rad_45 = np.radians(45.0)
    tower_clearance_box = trimesh.creation.box([bp.CLIP_ARM_WIDTH + 1.0, 3.0, 7.0])
    rot_45 = trimesh.transformations.rotation_matrix(center_rad_45, [0, 0, 1])
    tower_clearance_box.apply_transform(rot_45)
    p_cut_45 = p45 - norm45 * (bp.OUTER_WALL_THICK + 1.0)
    tower_clearance_box.apply_translation([p_cut_45[0], p_cut_45[1], 3.5 + bp.BASE_THICK])
    try:
        mesh_towers_assembly = mesh_towers_assembly.difference(tower_clearance_box, engine='manifold')
    except Exception:
        pass
        
    # Snap Clips
    slot_cuts = []
    hook_meshes = []
    stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT
    slot_z_bot = bp.OUTER_WALL_HEIGHT - bp.CLIP_GAP_DEPTH
    z_root_center = slot_z_bot + bp.CLIP_ROOT_RADIUS
    slot_t = bp.CLIP_SLOT_CLEARANCE
    
    for angle_deg in bp.CLIP_ANGLES:
        center_rad = np.radians(angle_deg)
        p, norm, tang = bp.find_boundary_point_and_normal(base_poly_clean, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = bp.CLIP_ARM_WIDTH / r_est
        slot_d_theta = slot_t / r_est
        hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, bp.CLIP_HOOK_DEPTH)
        
        for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
            slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
            rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
            box_h = (bp.OUTER_WALL_HEIGHT + 1.0) - z_root_center
            s_box = trimesh.creation.box([bp.OUTER_WALL_THICK * 4.0, slot_t, box_h])
            s_box.apply_transform(rot_mat)
            s_box.apply_translation([slot_p[0], slot_p[1], z_root_center + box_h / 2.0])
            cyl = trimesh.creation.cylinder(radius=bp.CLIP_ROOT_RADIUS, height=bp.OUTER_WALL_THICK * 4.0, sections=16)
            rot_to_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
            cyl.apply_transform(rot_to_x)
            cyl.apply_transform(rot_mat)
            cyl.apply_translation([slot_p[0], slot_p[1], z_root_center])
            slot_cuts.append(trimesh.util.concatenate([s_box, cyl]))
            
        N = 32
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        half_w = bp.CLIP_ARM_WIDTH / 2.0
        outer_coords, shelf_coords, inner_overlap_coords = [], [], []
        for th in theta_vals:
            ray_dir = np.array([np.cos(th), np.sin(th)])
            ray = bp.LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
            inter_out = outer_body_poly.exterior.intersection(ray)
            po = np.array([inter_out.x, inter_out.y]) if inter_out.geom_type == 'Point' else ray_dir * r_est
            n_dir = po / np.linalg.norm(po)
            t = (th - center_rad) * r_est
            eff_depth = hook_depth - bp.CLIP_CROWN_EASE * ((abs(t / half_w)) ** 2.0)
            outer_coords.append(po)
            shelf_coords.append(po + n_dir * eff_depth)
            inner_overlap_coords.append(po - n_dir * 0.25)
        inner_overlap_coords = np.array(inner_overlap_coords)
        shelf_coords = np.array(shelf_coords)
        v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
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
        hook_faces.append([0, N, 2*N])
        hook_faces.append([0, 2*N, 3*N])
        hook_faces.append([N - 1, 3*N - 1, 2*N - 1])
        hook_faces.append([N - 1, 4*N - 1, 3*N - 1])
        m_hook = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
        hook_meshes.append(m_hook)
        
    try:
        all_slot_cuts = trimesh.util.concatenate(slot_cuts)
        mesh_wall = mesh_wall.difference(all_slot_cuts, engine='manifold')
        mesh_towers_assembly = mesh_towers_assembly.difference(all_slot_cuts, engine='manifold')
    except Exception:
        pass
        
    mesh_curved_feat = bp.build_center_curved_feature_mesh()
    
    full_part = trimesh.util.concatenate([
        mesh_base, mesh_shrouds, mesh_wall, mesh_ribs, mesh_brackets,
        mesh_seating_ribs, mesh_towers_assembly, mesh_curved_feat
    ] + hook_meshes)
    return full_part, base_poly_clean

part, base_poly = build_monolithic_part_model()
print("Monolithic part bounds:\n", part.bounds)
print("Monolithic part watertight:", part.is_watertight)
