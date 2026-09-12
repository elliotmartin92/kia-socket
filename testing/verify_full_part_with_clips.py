"""
testing/verify_full_part_with_clips.py
Verify the full part generation with:
1. CLIP_HOOK_DEPTH = 2.49 mm (-0.10mm radial protrusion reduction)
2. Twin-prong breakaway fork supports (2 x 0.45 mm² = 0.90 mm² contact area)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_part

from test_twin_prong_support import build_clip_supports_twin_prong

# Generate full part with Twin-Prong support
build_part.CLIP_HOOK_DEPTH = 2.49

# Monkey-patch build_clip_supports_mesh to test
build_part.build_clip_supports_mesh = build_clip_supports_twin_prong
mesh_part_new, base_poly = build_part.build_exact_3d_model()
print(f"New part mesh watertight: {mesh_part_new.is_watertight}")
print(f"New part mesh volume: {mesh_part_new.volume:.2f} mm³")

# Side-by-side 3D comparison of Old vs New Support under Clip
fig = plt.figure(figsize=(14, 7), dpi=180)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

p45, _, _ = build_part.find_boundary_point_and_normal(base_poly, 45.0)

def plot_clip_region(ax, mesh, title, col_face, col_edge):
    dists = np.linalg.norm(mesh.vertices[:, :2] - p45, axis=1)
    mask = dists < 6.5
    faces_mask = np.all(mask[mesh.faces], axis=1)
    sub = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[faces_mask])
    v = sub.vertices
    f = sub.faces
    col = Poly3DCollection(v[f], alpha=0.92, facecolor=col_face, edgecolor=col_edge, lw=0.35)
    ax.add_collection3d(col)
    ax.set_xlim(p45[0] - 4, p45[0] + 4)
    ax.set_ylim(p45[1] - 4, p45[1] + 4)
    ax.set_zlim(0, 7.5)
    ax.set_xlabel("X (mm)", fontsize=8, fontweight='bold')
    ax.set_ylabel("Y (mm)", fontsize=8, fontweight='bold')
    ax.set_zlabel("Z (mm)", fontsize=8, fontweight='bold')
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.view_init(elev=22, azim=42)

# Reset to original build_clip_supports_mesh for old comparison
import importlib
importlib.reload(build_part)
build_part.CLIP_HOOK_DEPTH = 2.59
mesh_part_old, _ = build_part.build_exact_3d_model()

plot_clip_region(ax1, mesh_part_old,
                 "BEFORE: Center Chisel Support\n(Hook Protrusion = 2.59mm, Unsupported 1.2mm Edges Droop)",
                 '#ffccbc', '#d84315')

plot_clip_region(ax2, mesh_part_new,
                 "AFTER: Twin-Prong Breakaway Fork Support\n(Hook Protrusion = 2.49mm [-0.1mm], Edge Prongs + Prying Arch)",
                 '#b2dfdb', '#00695c')

plt.tight_layout()
out_comp = 'testing/clip_support_before_after_3d.png'
plt.savefig(out_comp, dpi=180)
print(f"Saved side-by-side comparison to {out_comp}")

