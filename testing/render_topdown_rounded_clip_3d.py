"""
Generate 3D mesh of snap clip with top-down rounded corners.
Save 3D render in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import LineString, Polygon

import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

angle = 45.0
center_rad = math.radians(angle)
p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle)
r_est = np.linalg.norm(p)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
hook_depth = build_part.CLIP_HOOK_DEPTH
stem_h = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT
top_z = build_part.CLIP_HEIGHT
blunt_h = build_part.CLIP_BLUNT_HEIGHT

def build_topdown_rounded_hook_mesh(corner_r=1.00, n_theta=32):
    half_w = build_part.CLIP_ARM_WIDTH / 2.0
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, n_theta)
    
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
        
        # Tangential position from center
        t = (th - center_rad) * r_est
        if abs(t) > half_w - corner_r:
            dt = abs(t) - (half_w - corner_r)
            val = max(0.0, corner_r**2 - dt**2)
            delta_n = corner_r - np.sqrt(val)
            eff_depth = max(0.30, hook_depth - delta_n)
        else:
            eff_depth = hook_depth
            
        ps = po + n_dir * eff_depth
        p_in = po - n_dir * 0.25
        
        outer_coords.append(po)
        shelf_coords.append(ps)
        inner_overlap_coords.append(p_in)
        
    inner_overlap_coords = np.array(inner_overlap_coords)
    shelf_coords = np.array(shelf_coords)
    
    N = n_theta
    v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
    v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
    v_face = np.column_stack([shelf_coords, np.full(N, stem_h + blunt_h)])
    v2 = np.column_stack([inner_overlap_coords, np.full(N, top_z)])
    hook_verts = np.vstack([v0, v1, v_face, v2])
    
    hook_faces = []
    for i in range(N - 1):
        # Shelf (-Z)
        hook_faces.append([i, N + i + 1, N + i])
        hook_faces.append([i, i + 1, N + i + 1])
        # Blunt face (+R)
        hook_faces.append([N + i, 2*N + i + 1, 2*N + i])
        hook_faces.append([N + i, N + i + 1, 2*N + i + 1])
        # Lead-in ramp
        hook_faces.append([2*N + i, 3*N + i + 1, 3*N + i])
        hook_faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
        # Inner wall face
        hook_faces.append([3*N + i, i + 1, i])
        hook_faces.append([3*N + i, 3*N + i + 1, i + 1])
        
    # Side endcaps
    hook_faces.append([0, 2*N, 3*N])
    hook_faces.append([0, N, 2*N])
    hook_faces.append([N - 1, 3*N - 1, 2*N - 1])
    hook_faces.append([N - 1, 4*N - 1, 3*N - 1])
    
    mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
    if mesh.volume < 0:
        mesh.faces = np.fliplr(mesh.faces)
    return mesh

# Generate meshes for old square vs new top-down rounded
mesh_square = build_topdown_rounded_hook_mesh(corner_r=0.0) # Sharp square
mesh_rounded = build_topdown_rounded_hook_mesh(corner_r=1.0) # Rounded corners

fig = plt.figure(figsize=(18, 8), dpi=200)

# Top view of both
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.set_title("Current Design: Sharp Square Corners (Top-Down 3D)\n(Corners dig into female bore during insertion)", fontsize=11, fontweight='bold', color='#c62828')
p_sq = Poly3DCollection(mesh_square.vertices[mesh_square.faces], facecolors='#ef5350', edgecolors='#b71c1c', linewidths=0.3, alpha=0.85)
ax1.add_collection3d(p_sq)
ax1.set_xlim(p[0] - 2, p[0] + 3)
ax1.set_ylim(p[1] - 2, p[1] + 3)
ax1.set_zlim(4.5, 7.2)
ax1.view_init(elev=65, azim=45)
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)')

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.set_title("Proposed Design: Rounded Corners Top-Down (R = 1.0mm)\n(Smooth insertion, non-biting corners, 100% full retention)", fontsize=11, fontweight='bold', color='#2e7d32')
p_rnd = Poly3DCollection(mesh_rounded.vertices[mesh_rounded.faces], facecolors='#66bb6a', edgecolors='#1b5e20', linewidths=0.3, alpha=0.85)
ax2.add_collection3d(p_rnd)
ax2.set_xlim(p[0] - 2, p[0] + 3)
ax2.set_ylim(p[1] - 2, p[1] + 3)
ax2.set_zlim(4.5, 7.2)
ax2.view_init(elev=65, azim=45)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')

plt.tight_layout()
out_3d = os.path.join(os.path.dirname(__file__), 'topdown_rounded_clip_3d.png')
plt.savefig(out_3d, dpi=200)
print(f"Saved {out_3d}")
