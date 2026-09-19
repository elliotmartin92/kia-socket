import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
wall_2d = outer_body_poly.difference(inner_wall_poly)

mesh_wall = trimesh.creation.extrude_polygon(wall_2d, height=build_part.OUTER_WALL_HEIGHT - build_part.BASE_THICK)
mesh_wall.apply_translation([0, 0, build_part.BASE_THICK])

CLIP_GAP_DEPTH = 5.47  # slot reaches Z = 1.30mm
slot_z_bot = build_part.OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH  # 1.30mm
slot_t = build_part.CLIP_SLOT_CLEARANCE  # 0.35mm
r_root = 0.40  # 0.80mm diameter rounded stress-relief root
z_root_center = slot_z_bot + r_root  # 1.70mm

slot_cuts = []
for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    slot_d_theta = slot_t / r_est
    
    for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
        slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
        rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
        
        # 1. Vertical slot box above root cylinder
        box_h = (build_part.OUTER_WALL_HEIGHT + 1.0) - z_root_center
        s_box = trimesh.creation.box([build_part.OUTER_WALL_THICK * 4.0, slot_t, box_h])
        s_box.apply_transform(rot_mat)
        s_box.apply_translation([slot_p[0], slot_p[1], z_root_center + box_h / 2.0])
        
        # 2. Horizontal cylindrical stress-relief keyhole root (oriented radially along slot_p)
        # Cylinder axis along X, then rotated by th_slot
        cyl = trimesh.creation.cylinder(radius=r_root, height=build_part.OUTER_WALL_THICK * 4.0, sections=16)
        # trimesh cylinder axis is along Z. Rotate to X axis:
        rot_to_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
        cyl.apply_transform(rot_to_x)
        cyl.apply_transform(rot_mat)
        cyl.apply_translation([slot_p[0], slot_p[1], z_root_center])
        
        slot_cutter = trimesh.util.concatenate([s_box, cyl])
        slot_cuts.append(slot_cutter)

all_cuts = trimesh.util.concatenate(slot_cuts)
print(f"All cuts watertight: {all_cuts.is_watertight}")
slotted_wall = mesh_wall.difference(all_cuts, engine='manifold')
print(f"Slotted wall watertight: {slotted_wall.is_watertight}, volume: {slotted_wall.volume:.2f} mm³")
assert slotted_wall.is_watertight
