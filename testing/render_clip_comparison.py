"""
testing/render_clip_comparison.py
Renders side-by-side comparison of Top Clip (45.0°) with flat retention shelf
vs Bottom Clip (211.3°) with 45° support coming out of the stem.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_part as bp

part_flat, base_poly = bp.build_exact_3d_model()

fig = plt.figure(figsize=(16, 7), dpi=180)
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

def plot_clip(ax, p, title, facecolor, edgecolor):
    dists = np.linalg.norm(part_flat.vertices[:, :2] - p, axis=1)
    mask = dists < 5.0
    faces_mask = np.all(mask[part_flat.faces], axis=1)
    sub = trimesh.Trimesh(vertices=part_flat.vertices, faces=part_flat.faces[faces_mask])
    v = sub.vertices
    f = sub.faces
    col = Poly3DCollection(v[f], alpha=0.9, facecolor=facecolor, edgecolor=edgecolor, lw=0.35)
    ax.add_collection3d(col)
    ax.set_xlim(p[0] - 3.5, p[0] + 3.5)
    ax.set_ylim(p[1] - 3.5, p[1] + 3.5)
    ax.set_zlim(1.0, 7.5)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")

# 1. Top Clip (45.0°)
p45, _, _ = bp.find_boundary_point_and_normal(base_poly, 45.0)
plot_clip(ax1, p45, "Top Right Clip (45.0°)\nStandard 90° Horizontal Shelf at Z=4.97mm\n(Prints Upwards in 45° Tilted Orientation)", '#ffccbc', '#d84315')
ax1.view_init(elev=20, azim=45)

# 2. Bottom Clip (211.3°)
p211, _, _ = bp.find_boundary_point_and_normal(base_poly, 211.3)
plot_clip(ax2, p211, "Bottom Left Clip (211.3°)\nHardcoded 45° Support Coming Out of Stem\n(Slopes Upwards from Z=3.22mm to 4.97mm to Support Clip)", '#b2dfdb', '#004d40')
ax2.view_init(elev=20, azim=45)

plt.tight_layout()
out_png = 'testing/clip_support_comparison.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
