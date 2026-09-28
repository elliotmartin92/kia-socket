"""
testing/render_overhang_3d.py
Render 3D isometric and orthographic views of the lever in printable orientation,
highlighting all overhangs / downward-facing faces in bright red with Z heights labeled.
"""

import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

mesh = trimesh.load('shaft_rocker_clean.stl')

# Filter faces
normals = mesh.face_normals
centers = mesh.triangles_center
areas = mesh.area_faces

# Thresholds for overhangs:
# normal_z < -0.2 (downward facing > 11.5° from vertical)
# normal_z < -0.5 (overhang > 30° from vertical / 60° from horizontal)
is_downward = normals[:, 2] < -0.2
is_steep = normals[:, 2] < -0.5

print(f"Total faces: {len(mesh.faces)}")
print(f"Downward faces (n_z < -0.2): {np.sum(is_downward)}")
print(f"Steep overhang faces (n_z < -0.5): {np.sum(is_steep)}")

fig = plt.figure(figsize=(18, 6))

views = [
    ('Side View (Y-Z)', (0, 0), (1, 2), 'Y (mm)', 'Z (mm)'),
    ('3D Perspective View', None, None, None, None),
    ('Front View (X-Z)', (0, 90), (0, 2), 'X (mm)', 'Z (mm)')
]

# 1. Side View 2D projection
ax1 = fig.add_subplot(1, 3, 1)
# Plot all triangles projected to Y-Z
for i, f in enumerate(mesh.faces):
    v = mesh.vertices[f]
    pts = v[:, [1, 2]]
    nz = normals[i, 2]
    if nz < -0.5:
        color = 'red'
        alpha = 0.8
        zorder = 5
    elif nz < -0.2:
        color = 'orange'
        alpha = 0.6
        zorder = 4
    else:
        color = 'lightgray'
        alpha = 0.3
        zorder = 1
    poly = plt.Polygon(pts, facecolor=color, edgecolor='none', alpha=alpha, zorder=zorder)
    ax1.add_patch(poly)

ax1.set_xlim(mesh.bounds[0, 1] - 2, mesh.bounds[1, 1] + 2)
ax1.set_ylim(-1, mesh.bounds[1, 2] + 2)
ax1.set_xlabel('Y (mm)')
ax1.set_ylabel('Z (mm)')
ax1.set_title('Side View (Y vs Z)\nRed = Steep Overhang (n_z < -0.5)\nOrange = Downward (n_z < -0.2)')
ax1.grid(True)
ax1.set_aspect('equal')

# 2. 3D Perspective View
ax2 = fig.add_subplot(1, 3, 2, projection='3d')
# Subsample faces for fast 3d rendering
triangles = []
face_colors = []
for i, f in enumerate(mesh.faces):
    v = mesh.vertices[f]
    nz = normals[i, 2]
    if nz < -0.5:
        face_colors.append((1.0, 0.0, 0.0, 0.9)) # Red
        triangles.append(v)
    elif nz < -0.2:
        face_colors.append((1.0, 0.6, 0.0, 0.7)) # Orange
        triangles.append(v)
    elif i % 2 == 0: # Subsample other faces
        face_colors.append((0.8, 0.8, 0.8, 0.2)) # Light gray
        triangles.append(v)

coll = Poly3DCollection(triangles, facecolors=face_colors, edgecolors='none')
ax2.add_collection3d(coll)
ax2.set_xlim(mesh.bounds[0, 0] - 2, mesh.bounds[1, 0] + 2)
ax2.set_ylim(mesh.bounds[0, 1] - 2, mesh.bounds[1, 1] + 2)
ax2.set_zlim(0, mesh.bounds[1, 2] + 2)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
ax2.view_init(elev=25, azim=-45)
ax2.set_title('3D Perspective View')

# 3. Front View (X-Z)
ax3 = fig.add_subplot(1, 3, 3)
for i, f in enumerate(mesh.faces):
    v = mesh.vertices[f]
    pts = v[:, [0, 2]]
    nz = normals[i, 2]
    if nz < -0.5:
        color = 'red'
        alpha = 0.8
        zorder = 5
    elif nz < -0.2:
        color = 'orange'
        alpha = 0.6
        zorder = 4
    else:
        color = 'lightgray'
        alpha = 0.3
        zorder = 1
    poly = plt.Polygon(pts, facecolor=color, edgecolor='none', alpha=alpha, zorder=zorder)
    ax3.add_patch(poly)

ax3.set_xlim(mesh.bounds[0, 0] - 2, mesh.bounds[1, 0] + 2)
ax3.set_ylim(-1, mesh.bounds[1, 2] + 2)
ax3.set_xlabel('X (mm)')
ax3.set_ylabel('Z (mm)')
ax3.set_title('Front View (X vs Z)')
ax3.grid(True)
ax3.set_aspect('equal')

plt.tight_layout()
plt.savefig('testing/lever_overhangs_3d.png', dpi=150)
print("Saved testing/lever_overhangs_3d.png")
