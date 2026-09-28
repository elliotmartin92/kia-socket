"""
Generate 3D side-by-side comparison of current squared-off clip vs new rounded clip.
Saves render in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import LineString

import build_part
from testing.test_rounded_clip_mesh import build_rounded_hook_mesh

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

# Let's inspect the 45 degree clip
angle = 45.0
center_rad = math.radians(angle)
p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle)
r_est = np.linalg.norm(p)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
hook_depth = build_part.CLIP_HOOK_DEPTH

# 1. Old squared-off mesh
N = 16
theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
outer_coords = []
shelf_coords = []
inner_overlap_coords = []
for th in theta_vals:
    ray_dir = np.array([np.cos(th), np.sin(th)])
    ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
    inter_out = outer_body_poly.exterior.intersection(ray)
    if inter_out.geom_type == 'Point':
        po = np.array([inter_out.x, inter_out.y])
    elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
        po = np.array([inter_out.x, inter_out.y]) if hasattr(inter_out, 'x') else np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
    else:
        po = ray_dir * r_est
    n_dir = po / np.linalg.norm(po)
    ps = po + n_dir * hook_depth
    p_in = po - n_dir * 0.25
    outer_coords.append(po)
    shelf_coords.append(ps)
    inner_overlap_coords.append(p_in)

inner_overlap_coords = np.array(inner_overlap_coords)
shelf_coords = np.array(shelf_coords)
stem_h = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT

v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
v_face = np.column_stack([shelf_coords, np.full(N, stem_h + build_part.CLIP_BLUNT_HEIGHT)])
v2 = np.column_stack([inner_overlap_coords, np.full(N, build_part.CLIP_HEIGHT)])
hook_verts_old = np.vstack([v0, v1, v_face, v2])

hook_faces_old = []
for i in range(N - 1):
    hook_faces_old.append([i, N + i + 1, N + i])
    hook_faces_old.append([i, i + 1, N + i + 1])
    hook_faces_old.append([N + i, 2*N + i + 1, 2*N + i])
    hook_faces_old.append([N + i, N + i + 1, 2*N + i + 1])
    hook_faces_old.append([2*N + i, 3*N + i + 1, 3*N + i])
    hook_faces_old.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
    hook_faces_old.append([3*N + i, i + 1, i])
    hook_faces_old.append([3*N + i, 3*N + i + 1, i + 1])
hook_faces_old.append([0, 2*N, 3*N])
hook_faces_old.append([0, N, 2*N])
hook_faces_old.append([N - 1, 3*N - 1, 2*N - 1])
hook_faces_old.append([N - 1, 4*N - 1, 3*N - 1])

mesh_old = trimesh.Trimesh(vertices=hook_verts_old, faces=np.array(hook_faces_old), process=True)

# 2. New rounded mesh
mesh_new = build_rounded_hook_mesh(center_rad, r_est, d_theta, hook_depth)

# Render comparison
fig = plt.figure(figsize=(18, 8), dpi=200)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.set_title("Current Design: Squared-Off Triangle Hook\n(Steep ramp + 0.35mm blunt land: high insertion stress)", fontsize=11, fontweight='bold', color='#c62828')

# Plot old mesh
poly_old = Poly3DCollection(mesh_old.vertices[mesh_old.faces], facecolors='#ef5350', edgecolors='#b71c1c', linewidths=0.3, alpha=0.85)
ax1.add_collection3d(poly_old)
ax1.set_xlim(p[0] - 2, p[0] + 3)
ax1.set_ylim(p[1] - 2, p[1] + 3)
ax1.set_zlim(4.5, 7.2)
ax1.view_init(elev=25, azim=45)
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)')

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.set_title("Proposed Design: Rounded Convex Hook\n(Curved tangent to outer diameter: smooth insertion, identical retention)", fontsize=11, fontweight='bold', color='#2e7d32')

# Plot new mesh
poly_new = Poly3DCollection(mesh_new.vertices[mesh_new.faces], facecolors='#66bb6a', edgecolors='#1b5e20', linewidths=0.3, alpha=0.85)
ax2.add_collection3d(poly_new)
ax2.set_xlim(p[0] - 2, p[0] + 3)
ax2.set_ylim(p[1] - 2, p[1] + 3)
ax2.set_zlim(4.5, 7.2)
ax2.view_init(elev=25, azim=45)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')

plt.tight_layout()
out_render = os.path.join(os.path.dirname(__file__), 'rounded_clip_3d_comparison.png')
plt.savefig(out_render, dpi=200)
print(f"Saved {out_render}")
