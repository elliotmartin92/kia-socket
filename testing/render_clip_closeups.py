"""
Render high-resolution close-ups of the snap clip from multiple angles.
"""
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import build_exact_3d_model, find_boundary_point_and_normal, get_exact_base_polygon

mesh, base_poly = build_exact_3d_model()
p45, norm45, tang45 = find_boundary_point_and_normal(base_poly, 45)

fig = plt.figure(figsize=(20, 10), dpi=160)

views = [
    (1, "Side View of Clip at 45 deg", (0, 45)),
    (2, "Front View (from outside looking in)", (15, 225)),
    (3, "Bottom-Up View (looking at undercut shelf)", (-30, 225)),
    (4, "Top-Down Isometric", (45, 225))
]

for idx, title, (elev, azim) in views:
    ax = fig.add_subplot(2, 2, idx, projection='3d')
    # Filter vertices close to clip at 45 deg (around p45)
    dists = np.linalg.norm(mesh.vertices[:, :2] - p45[:2], axis=1)
    mask_faces = np.all(dists[mesh.faces] < 6.0, axis=1)
    clip_faces = mesh.faces[mask_faces]
    
    col = Poly3DCollection(mesh.vertices[clip_faces], alpha=0.85, edgecolor='#111111', linewidths=0.3)
    col.set_facecolor('#00bcd4')
    ax.add_collection3d(col)
    
    ax.set_xlim(p45[0] - 4, p45[0] + 4)
    ax.set_ylim(p45[1] - 4, p45[1] + 4)
    ax.set_zlim(0, 8)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

plt.tight_layout()
plt.savefig('clip_closeup_views.png', dpi=160)
print("Saved clip_closeup_views.png")
