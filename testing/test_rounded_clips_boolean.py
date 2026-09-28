"""
Test full boolean integration of rounded clip hooks into the outer wall
with slot cutters and stress-relief roots.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

import build_part
from testing.test_rounded_clip_mesh import build_rounded_hook_mesh

print("Testing full wall + rounded hooks + slot cuts boolean operations...")

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)

# Build raw outer wall
poly_wall_2d = outer_body_poly.difference(inner_wall_poly)
mesh_wall = trimesh.creation.extrude_polygon(poly_wall_2d, height=build_part.OUTER_WALL_HEIGHT)
mesh_wall.apply_translation([0, 0, 0.0])

slot_cuts = []
hook_meshes = []

stem_h = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT
slot_z_bot = build_part.OUTER_WALL_HEIGHT - build_part.CLIP_GAP_DEPTH
z_root_center = slot_z_bot + build_part.CLIP_ROOT_RADIUS
slot_t = build_part.CLIP_SLOT_CLEARANCE

for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    slot_d_theta = slot_t / r_est
    hook_depth = build_part.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, build_part.CLIP_HOOK_DEPTH)
    
    # Slots
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
        
        s_cutter = trimesh.util.concatenate([s_box, cyl])
        slot_cuts.append(s_cutter)
        
    hm = build_rounded_hook_mesh(center_rad, r_est, d_theta, hook_depth)
    hook_meshes.append(hm)

# Boolean Union of rounded hooks into wall
for hm in hook_meshes:
    mesh_wall = mesh_wall.union(hm, engine='manifold')
print(f"Post-hook union mesh_wall watertight: {mesh_wall.is_watertight}, Volume: {mesh_wall.volume:.2f} mm³")

# Boolean Difference of slots
all_slot_cuts = trimesh.util.concatenate(slot_cuts)
mesh_wall = mesh_wall.difference(all_slot_cuts, engine='manifold')
print(f"Post-slot difference mesh_wall watertight: {mesh_wall.is_watertight}, Volume: {mesh_wall.volume:.2f} mm³")

assert mesh_wall.is_watertight, "Wall mesh after rounded hooks and slot cuts must be watertight!"
print("SUCCESS: Full boolean pipeline works flawlessly with rounded clip hooks!")
