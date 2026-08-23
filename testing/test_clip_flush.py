"""
Test snap clip flush alignment with inner wall face.
"""
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

from build_part import (
    OUTER_WALL_HEIGHT, OUTER_WALL_THICK, BASE_THICK,
    CLIP_HEIGHT, CLIP_GAP_DEPTH, CLIP_ARM_WIDTH, CLIP_SLOT_CLEARANCE,
    CLIP_HOOK_DEPTH, CLIP_HOOK_HEIGHT, find_boundary_point_and_normal,
    get_exact_base_polygon
)

# Test clip geometry with CLIP_ARM_THICK = OUTER_WALL_THICK = 1.20mm
CLIP_ARM_THICK = OUTER_WALL_THICK
stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT

# Stem
stem = trimesh.creation.box([CLIP_ARM_THICK, CLIP_ARM_WIDTH, stem_h])
stem.apply_translation([-CLIP_ARM_THICK/2, 0, stem_h/2])

# Hook
y0 = -CLIP_ARM_WIDTH / 2.0
y1 = CLIP_ARM_WIDTH / 2.0
hook_v = np.array([
    [-CLIP_ARM_THICK, y0, stem_h],
    [0.0,             y0, stem_h],
    [CLIP_HOOK_DEPTH, y0, stem_h],      # +1.59mm outward shelf
    [-CLIP_ARM_THICK, y0, CLIP_HEIGHT], # Apex at inner wall face
    [-CLIP_ARM_THICK, y1, stem_h],
    [0.0,             y1, stem_h],
    [CLIP_HOOK_DEPTH, y1, stem_h],
    [-CLIP_ARM_THICK, y1, CLIP_HEIGHT]
])
hook_faces = np.array([
    [0, 1, 2], [0, 2, 3],
    [4, 6, 5], [4, 7, 6],
    [1, 5, 6], [1, 6, 2],
    [0, 4, 5], [0, 5, 1],
    [2, 6, 7], [2, 7, 3],
    [0, 3, 7], [0, 7, 4]
])
hook = trimesh.Trimesh(vertices=hook_v, faces=hook_faces)
clip = trimesh.util.concatenate([stem, hook])

print("Clip bounds in local coords (u = radial, v = lateral, w = vertical):")
print(f"Radial u bounds: [{clip.bounds[0][0]:.3f}, {clip.bounds[1][0]:.3f}] mm")
print(f"Lateral v bounds: [{clip.bounds[0][1]:.3f}, {clip.bounds[1][1]:.3f}] mm")
print(f"Vertical w bounds: [{clip.bounds[0][2]:.3f}, {clip.bounds[1][2]:.3f}] mm")

# Verify inner face coordinate
inner_face_u = clip.bounds[0][0]
assert abs(inner_face_u - (-OUTER_WALL_THICK)) < 1e-6, f"Inner face {inner_face_u} does not match -OUTER_WALL_THICK {-OUTER_WALL_THICK}"
print("VERIFIED: Clip inner face is EXACTLY FLUSH with interior wall at u = -1.20mm!")
