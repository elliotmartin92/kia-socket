import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

ins_r = bp.build_slit_insert_mesh(is_right=True)
cx_right = 8.453
cy = -13.589
z_insert = -bp.SLIT_BOSS_HEIGHT
ins_r_placed = ins_r.copy().apply_translation([cx_right, cy, z_insert])

# Rotate 45 deg
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
ins_tilted = ins_r_placed.copy().apply_transform(R)

# Part tilted
part_flat, _ = bp.build_exact_3d_model()
part_tilted = part_flat.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]

ins_tilted.apply_translation([0, 0, -z_min])

print(f"Insert bounds in tilted space:\n  X: [{ins_tilted.bounds[0,0]:.2f}, {ins_tilted.bounds[1,0]:.2f}]\n  Y: [{ins_tilted.bounds[0,1]:.2f}, {ins_tilted.bounds[1,1]:.2f}]\n  Z: [{ins_tilted.bounds[0,2]:.2f}, {ins_tilted.bounds[1,2]:.2f}]")

# Check face normals and angles with downward vertical [0, 0, -1]
# For 3D printing, an overhang has normal[:, 2] < 0.
# Overhang angle from horizontal: theta = arcsin(-normal[:, 2]) or arccos(normal[:, 2])
fn = ins_tilted.face_normals
overhang_faces = np.where(fn[:, 2] < -0.01)[0]
print(f"Number of overhang faces on tilted insert: {len(overhang_faces)} / {len(fn)}")

for f_idx in overhang_faces:
    norm = fn[f_idx]
    # angle from horizontal build plate (90 = vertical wall, 0 = horizontal ceiling)
    angle_from_horiz = np.degrees(np.arcsin(np.abs(norm[2])))
    # z height of face center
    fc = ins_tilted.triangles_center[f_idx]
    print(f"  Face {f_idx}: normal={norm}, angle_from_horiz={angle_from_horiz:.1f}°, center Z={fc[2]:.2f}, center Y={fc[1]:.2f}")
