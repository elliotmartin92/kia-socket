"""
Inspect and visualize making the snap clips ~0.5mm less prominent by cutting,
making the squared-off aspect more prominent, combined with the subtle top-down green crown.
Save plots in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

CLIP_HEIGHT = 6.77
CLIP_HOOK_HEIGHT = 1.80
stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
top_z = CLIP_HEIGHT                      # 6.77mm
H = CLIP_HOOK_HEIGHT                     # 1.80mm

# Current:
curr_depth = 2.10
curr_blunt = 0.35

# Proposed ~0.5mm less prominent:
# Cut depth: 2.10 - 0.50 = 1.60mm (or testing 1.60mm vs 1.65mm)
new_depth = 1.60
# When cutting 0.50mm off the ramp from (0, 6.77) to (2.10, 5.32):
# The ramp equation: Z(r) = 6.77 - (1.45 / 2.10) * r
# At r = 1.60mm: Z = 6.77 - 1.105 = 5.665mm
# New blunt height: 5.665 - 4.97 = 0.695mm (~0.70mm)
# The squared-off flat face is doubled from 0.35mm to 0.70mm!
new_blunt = 0.70

fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=200)

# Panel 1: Elevation Profile (R-Z)
ax1 = axes[0]
ax1.set_title("1. Elevation Profile: Current 2.10mm vs 1.60mm (-0.5mm Cut)", fontsize=11, fontweight='bold')

# Current profile
z_curr = [stem_h, stem_h, stem_h + curr_blunt, top_z]
r_curr = [0.0, curr_depth, curr_depth, 0.0]
ax1.plot(r_curr, z_curr, 'r--', lw=2.0, label=f'Current: 2.10mm Depth (0.35mm blunt face)')
ax1.fill(r_curr, z_curr, facecolor='red', alpha=0.10)

# New cut profile
z_new = [stem_h, stem_h, stem_h + new_blunt, top_z]
r_new = [0.0, new_depth, new_depth, 0.0]
ax1.plot(r_new, z_new, 'g-', lw=2.5, label=f'Proposed: 1.60mm Depth (0.70mm blunt face)')
ax1.fill(r_new, z_new, facecolor='#a5d6a7', alpha=0.4)

ax1.annotate(f'-0.50mm Less Prominent\n(Max Overhang = 1.60mm)',
             xy=(new_depth, stem_h + new_blunt/2.0), xytext=(0.5, 4.6),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=9, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round', fc='white', ec='#2e7d32'))

ax1.annotate(f'Squared-Off Face More Prominent!\nHeight: 0.35mm -> 0.70mm (+100%)',
             xy=(new_depth, stem_h + new_blunt), xytext=(0.3, 5.9),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=9, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round', fc='white', ec='#2e7d32'))

ax1.set_xlabel("Radial Protrusion beyond Outer Wall (mm)", fontsize=10, fontweight='bold')
ax1.set_ylabel("Elevation Z (mm)", fontsize=10, fontweight='bold')
ax1.set_xlim(-0.2, 2.5)
ax1.set_ylim(4.4, 7.1)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', fontsize=8.5)

# Panel 2: Top-Down Profile (XY) with Green Subtle Crown
ax2 = axes[1]
ax2.set_title("2. Top-Down Profile: Subtle Crown Arc at 1.60mm Depth", fontsize=11, fontweight='bold')

angle_deg = 45.0
center_rad = math.radians(angle_deg)
p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
r_est = np.linalg.norm(p)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
half_w = build_part.CLIP_ARM_WIDTH / 2.0

th_min = center_rad - d_theta / 2.0
th_max = center_rad + d_theta / 2.0
N = 64
theta_vals = np.linspace(th_min, th_max, N)

outer_pts = []
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
    outer_pts.append(po)
outer_pts = np.array(outer_pts)

# Current 2.10mm square
shelf_curr = []
for i, po in enumerate(outer_pts):
    n_dir = po / np.linalg.norm(po)
    shelf_curr.append(po + n_dir * curr_depth)
shelf_curr = np.array(shelf_curr)

# New 1.60mm with green subtle crown (0.20mm edge ease: 1.40mm at edges -> 1.60mm at center)
delta_d = 0.20
shelf_new = []
for i, th in enumerate(theta_vals):
    t = (th - center_rad) * r_est
    frac = abs(t / half_w)
    eff_d = new_depth - delta_d * (frac ** 2.0)
    po = outer_pts[i]
    n_dir = po / np.linalg.norm(po)
    shelf_new.append(po + n_dir * eff_d)
shelf_new = np.array(shelf_new)

ax2.plot(outer_pts[:,0], outer_pts[:,1], 'b-', lw=2.0, label='Outer Wall')
ax2.plot(shelf_curr[:,0], shelf_curr[:,1], 'r--', lw=1.5, alpha=0.5, label='Old 2.10mm Square')
ax2.plot(shelf_new[:,0], shelf_new[:,1], 'g-', lw=2.5, label='Proposed 1.60mm Subtle Crown')

poly_new = Polygon(np.vstack([outer_pts, shelf_new[::-1]]))
px, py = poly_new.exterior.xy
ax2.fill(px, py, facecolor='#a5d6a7', alpha=0.4)

center_p = shelf_new[N//2]
edge_p = shelf_new[0]
ax2.annotate(f"Center Depth: {new_depth:.2f}mm\n(-0.50mm less prominent)",
             xy=(center_p[0], center_p[1]), xytext=(center_p[0]+1.2, center_p[1]+1.8),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=8.5, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round', fc='white', ec='#2e7d32'))

ax2.annotate(f"Edge Depth: {new_depth - delta_d:.2f}mm\n(Gentle crown ease)",
             xy=(edge_p[0], edge_p[1]), xytext=(edge_p[0]-3.2, edge_p[1]+1.2),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=8.5, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round', fc='white', ec='#2e7d32'))

ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(11, 18)
ax2.set_ylim(12, 18)
ax2.legend(loc='lower left', fontsize=8.5)

# Panel 3: 3D Visualization of the new clip
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
ax3.set_title("3. 3D Render of Proposed Clip\n(1.60mm depth, 0.70mm blunt face, subtle crown)", fontsize=10, fontweight='bold', color='#2e7d32')

# Build 3D mesh
inner_overlap = outer_pts - (outer_pts / np.linalg.norm(outer_pts, axis=1, keepdims=True)) * 0.25
v0 = np.column_stack([inner_overlap, np.full(N, stem_h)])
v1 = np.column_stack([shelf_new, np.full(N, stem_h)])
v_face = np.column_stack([shelf_new, np.full(N, stem_h + new_blunt)])
v2 = np.column_stack([inner_overlap, np.full(N, top_z)])
hook_verts = np.vstack([v0, v1, v_face, v2])

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

m_3d = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
if m_3d.volume < 0:
    m_3d.faces = np.fliplr(m_3d.faces)

poly3d = Poly3DCollection(m_3d.vertices[m_3d.faces], facecolors='#66bb6a', edgecolors='black', linewidths=0.2, alpha=0.85)
ax3.add_collection3d(poly3d)
ax3.set_xlim(p[0] - 2, p[0] + 3)
ax3.set_ylim(p[1] - 2, p[1] + 3)
ax3.set_zlim(4.5, 7.2)
ax3.view_init(elev=50, azim=45)
ax3.set_xlabel('X')
ax3.set_ylabel('Y')
ax3.set_zlabel('Z')

plt.tight_layout()
out_fig = os.path.join(os.path.dirname(__file__), 'cut_clip_05mm_analysis.png')
plt.savefig(out_fig, dpi=200)
print(f"Saved {out_fig}")
