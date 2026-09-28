"""
testing/render_shaft_printable.py
Render 4-panel multi-angle view of the printable shaft rocker to visualize its orientation,
contact with Z=0, and overhangs.
"""

import os, sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

shaft_print = build_shaft_rocker_mesh(in_assembly_coords=False)

fig = plt.figure(figsize=(20, 15), dpi=150)

v = shaft_print.vertices
f = shaft_print.faces
normals = shaft_print.face_normals

# Identify face colors:
# Bed contact: green
# Overhang (< 45 deg to horizontal): red
# Other: light blue
face_colors = []
for i, face in enumerate(f):
    z_min = np.min(v[face, 2])
    n_z = normals[i, 2]
    if np.all(v[face, 2] < 0.08) and n_z < -0.7:
        face_colors.append('#2ecc71') # Green (bed contact)
    elif z_min > 0.15 and n_z < -0.707:
        face_colors.append('#e74c3c') # Red (unsupported overhang)
    else:
        face_colors.append('#3498db') # Blue (self-supporting)

face_colors = np.array(face_colors)

views = [
    ('Isometric (Elev 25, Azim 225)', 25, 225, 1),
    ('Front View (X-Z, Elev 0, Azim 270)', 0, 270, 2),
    ('Side View (Y-Z, Elev 0, Azim 180)', 0, 180, 3),
    ('Bottom-Up View (Elev -45, Azim 225)', -45, 225, 4)
]

for title, elev, azim, idx in views:
    ax = fig.add_subplot(2, 2, idx, projection='3d')
    mesh_col = Poly3DCollection(v[f], alpha=0.85, edgecolor='#2c3e50', linewidths=0.1)
    mesh_col.set_facecolor(face_colors)
    ax.add_collection3d(mesh_col)
    
    ax.set_xlim(-8, 8)
    ax.set_ylim(-8, 8)
    ax.set_zlim(0, 21)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')

plt.suptitle("Printable Shaft Rocker Overhang Analysis\nGreen = Bed Contact (Z=0) | Red = Overhangs Needing Support | Blue = Self-Supporting",
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('testing/shaft_printable_overhangs.png', dpi=150)
print("Saved testing/shaft_printable_overhangs.png successfully!")
