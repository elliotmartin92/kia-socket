"""
testing/compare_clip_support_options.py
Renders the two interpretations of the 45-degree support for the bottom clips:
Option A: Hardcoded 45° self-supporting gusset directly on the bottom clip stem
Option B: Sacrificial 45° breakaway support strut with prying slot coming out of the stem
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_part as bp

base_poly, outer_body_poly, _ = bp.get_exact_base_polygon()
angle_deg = 211.3
center_rad = math.radians(angle_deg)
p, norm, tang = bp.find_boundary_point_and_normal(base_poly, angle_deg)
r_est = np.linalg.norm(p)
d_theta = bp.CLIP_ARM_WIDTH / r_est
hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, bp.CLIP_HOOK_DEPTH)
stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT  # 4.97mm

# Build Original Clip Hook
N = 32
theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
half_w = bp.CLIP_ARM_WIDTH / 2.0

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
    t = (th - center_rad) * r_est
    frac = abs(t / half_w)
    eff_depth = hook_depth - bp.CLIP_CROWN_EASE * (frac ** 2.0)
    
    ps = po + n_dir * eff_depth
    p_in = po - n_dir * 0.25
    
    outer_coords.append(po)
    shelf_coords.append(ps)
    inner_overlap_coords.append(p_in)
    
inner_overlap_coords = np.array(inner_overlap_coords)
shelf_coords = np.array(shelf_coords)
outer_coords = np.array(outer_coords)

# Original Hook Wedge
v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
v_face = np.column_stack([shelf_coords, np.full(N, stem_h + bp.CLIP_BLUNT_HEIGHT)])
v2 = np.column_stack([inner_overlap_coords, np.full(N, bp.CLIP_HEIGHT)])

hook_faces = []
for i in range(N - 1):
    hook_faces.append([i, N + i + 1, N + i])
    hook_faces.append([i, i + 1, N + i + 1])
    hook_faces.append([N + i, 2*N + i + 1, 2*N + i])
    hook_faces.append([N + i, N + i + 1, 2*N + i + 1])
    hook_faces.append([2*N + i, 3*N + i + 1, 3*N + i])
    hook_faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
    hook_faces.append([3*N + i, i + 1, i])
    hook_faces.append([3*N + i, 3*N + i + 1, i + 1])
hook_faces.append([0, 2*N, 3*N])
hook_faces.append([0, N, 2*N])
hook_faces.append([N - 1, 3*N - 1, 2*N - 1])
hook_faces.append([N - 1, 4*N - 1, 3*N - 1])
m_orig_hook = trimesh.Trimesh(vertices=np.vstack([v0, v1, v_face, v2]), faces=np.array(hook_faces), process=True)

# OPTION A: 45° Gusset on Stem under the Hook
# Starts at stem_h - hook_depth (3.22mm) on outer wall, slopes out at 45° to hook shelf (4.97mm)
z_stem_start = stem_h - hook_depth
v_stem_base = np.column_stack([inner_overlap_coords, np.full(N, z_stem_start)])

gusset_faces = []
# v_stem_base is 0..N-1, v0 is N..2N-1, v1 is 2N..3N-1
# Triangular prism under hook:
# Bottom 45° face: v_stem_base -> v1
# Inner face at wall: v_stem_base -> v0
# Top face at shelf: v0 -> v1 (already in hook)
for i in range(N - 1):
    # Slanted 45° support face from stem base to shelf:
    gusset_faces.append([i, 2*N + i + 1, 2*N + i])
    gusset_faces.append([i, i + 1, 2*N + i + 1])
    # Inner face at stem:
    gusset_faces.append([N + i, i + 1, i])
    gusset_faces.append([N + i, N + i + 1, i + 1])
    # Top shelf interface:
    gusset_faces.append([N + i, 2*N + i, 2*N + i + 1])
    gusset_faces.append([N + i, 2*N + i + 1, N + i + 1])
gusset_faces.append([0, N, 2*N])
gusset_faces.append([N - 1, 3*N - 1, 2*N - 1])
m_gusset = trimesh.Trimesh(vertices=np.vstack([v_stem_base, v0, v1]), faces=np.array(gusset_faces), process=True)
if m_gusset.volume < 0:
    m_gusset.faces = np.fliplr(m_gusset.faces)

# Plot comparison
fig = plt.figure(figsize=(16, 7), dpi=180)
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

def plot_mesh(ax, mesh, col_face, col_edge, title):
    v = mesh.vertices
    f = mesh.faces
    col = Poly3DCollection(v[f], alpha=0.9, facecolor=col_face, edgecolor=col_edge, lw=0.4)
    ax.add_collection3d(col)
    ax.set_xlim(p[0] - 3.5, p[0] + 3.5)
    ax.set_ylim(p[1] - 3.5, p[1] + 3.5)
    ax.set_zlim(2.5, 7.5)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.view_init(elev=20, azim=45)

plot_mesh(ax1, m_orig_hook, '#ffccbc', '#d84315', "Original Hook (Unsupported 90° Shelf at Z=4.97mm)")
combined_option_a = trimesh.util.concatenate([m_orig_hook, m_gusset])
plot_mesh(ax2, combined_option_a, '#b2dfdb', '#004d40', "45° Support Coming Out of Stem (Z=3.22mm to 4.97mm)")

plt.tight_layout()
out_png = 'testing/compare_clip_support_options.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
