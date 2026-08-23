"""
Test if mesh_wall.difference(all_slots) was succeeding or failing.
"""
import trimesh
from build_part import (
    build_exact_3d_model, get_exact_base_polygon,
    create_arch_wall_poly, OUTER_WALL_HEIGHT, OUTER_WALL_THICK,
    BASE_THICK, CLIP_GAP_DEPTH, CLIP_ARM_WIDTH, CLIP_SLOT_CLEARANCE,
    find_boundary_point_and_normal
)
import math

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
wall_inner = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_2d = outer_body_poly.difference(wall_inner)

mesh_wall = trimesh.creation.extrude_polygon(wall_2d, height=OUTER_WALL_HEIGHT - BASE_THICK)
mesh_wall.apply_translation([0, 0, BASE_THICK])

slot_boxes = []
for angle_deg in [45, 135, 225, 315]:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    angle_norm = math.atan2(norm[1], norm[0])
    slot_z_bot = OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH
    slot_w = CLIP_ARM_WIDTH + 2 * CLIP_SLOT_CLEARANCE
    rot_mat = trimesh.transformations.rotation_matrix(angle_norm, [0, 0, 1])
    slot_box = trimesh.creation.box([OUTER_WALL_THICK * 4.0, slot_w, CLIP_GAP_DEPTH + 1.0])
    slot_box.apply_transform(rot_mat)
    slot_box.apply_translation([p[0] - norm[0]*OUTER_WALL_THICK*0.5, p[1] - norm[1]*OUTER_WALL_THICK*0.5, slot_z_bot + (CLIP_GAP_DEPTH + 1.0)/2])
    slot_boxes.append(slot_box)

all_slots = trimesh.util.concatenate(slot_boxes)
print("Mesh wall watertight:", mesh_wall.is_watertight)
print("All slots watertight:", all_slots.is_watertight)

try:
    diff = mesh_wall.difference(all_slots, engine='manifold')
    print("Difference with manifold succeeded! Is watertight:", diff.is_watertight)
except Exception as e:
    print("Manifold difference failed:", e)

try:
    diff_blender = mesh_wall.difference(all_slots, engine='blender')
    print("Difference with blender succeeded!")
except Exception as e:
    print("Blender difference failed:", e)

try:
    diff_scad = mesh_wall.difference(all_slots, engine='scad')
    print("Difference with scad succeeded!")
except Exception as e:
    print("Scad difference failed:", e)
