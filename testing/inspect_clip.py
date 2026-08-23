"""
Detailed inspection of snap clip mesh geometry, face normals, and overlaps.
"""
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import LineString

from build_part import (
    OUTER_WALL_THICK, OUTER_WALL_HEIGHT,
    CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_ARM_WIDTH,
    CLIP_HOOK_DEPTH, find_boundary_point_and_normal,
    get_exact_base_polygon
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

angle_deg = 45
p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
center_rad = np.deg2rad(angle_deg)
r_est = np.linalg.norm(p)
d_theta = CLIP_ARM_WIDTH / r_est

N = 16
theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)

inner_coords = []
outer_coords = []
shelf_coords = []

for th in theta_vals:
    ray_dir = np.array([np.cos(th), np.sin(th)])
    ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
    
    inter_out = outer_body_poly.exterior.intersection(ray)
    if inter_out.geom_type == 'Point':
        po = np.array([inter_out.x, inter_out.y])
    elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
        po = np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
    else:
        po = ray_dir * r_est
        
    inter_in = inner_wall_poly.exterior.intersection(ray)
    if inter_in.geom_type == 'Point':
        pi = np.array([inter_in.x, inter_in.y])
    elif hasattr(inter_in, 'geoms') and len(inter_in.geoms) > 0:
        pi = np.array([inter_in.geoms[-1].x, inter_in.geoms[-1].y])
    else:
        pi = po - (po / np.linalg.norm(po)) * OUTER_WALL_THICK
        
    n_dir = po / np.linalg.norm(po)
    ps = po + n_dir * CLIP_HOOK_DEPTH
    
    inner_coords.append(pi)
    outer_coords.append(po)
    shelf_coords.append(ps)
    
inner_coords = np.array(inner_coords)
outer_coords = np.array(outer_coords)
shelf_coords = np.array(shelf_coords)

stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
z_bot = 0.0
z_top = CLIP_HEIGHT

v0 = np.column_stack([inner_coords, np.full(N, z_bot)])
v1 = np.column_stack([outer_coords, np.full(N, z_bot)])
v2 = np.column_stack([outer_coords, np.full(N, stem_h)])
v3 = np.column_stack([shelf_coords, np.full(N, stem_h)])
v4 = np.column_stack([inner_coords, np.full(N, z_top)])
verts = np.vstack([v0, v1, v2, v3, v4])

print(f"Checking shelf coordinates:")
print(f"Outer wall at stem_h (Z={stem_h:.2f}): radius = {np.linalg.norm(outer_coords[0]):.3f}")
print(f"Hook shelf at stem_h (Z={stem_h:.2f}): radius = {np.linalg.norm(shelf_coords[0]):.3f}")
print(f"Top apex at z_top (Z={z_top:.2f}): radius = {np.linalg.norm(inner_coords[0]):.3f}")

# Check the side cross section of the hook at theta_vals[0]
# Coordinates in (r, z):
r_in = np.linalg.norm(inner_coords[0])
r_out = np.linalg.norm(outer_coords[0])
r_shelf = np.linalg.norm(shelf_coords[0])

fig, ax = plt.subplots(figsize=(8, 8), dpi=160)
# Profile in (Radius, Z)
r_pts = [r_in, r_out, r_out, r_shelf, r_in, r_in]
z_pts = [0,    0,     stem_h, stem_h, z_top, 0]
ax.plot(r_pts, z_pts, 'b-o', linewidth=2, label='Clip Profile in (Radius, Z)')
ax.fill(r_pts, z_pts, color='#80deea', alpha=0.5)

# Outer wall profile for reference (R from r_in to r_out, Z from 0 to 6.77)
ax.plot([r_in, r_out, r_out, r_in, r_in], [0, 0, 6.77, 6.77, 0], 'r--', label='Normal Wall Profile (6.77mm)')

ax.set_xlabel('Radius r (mm)')
ax.set_ylabel('Height Z (mm)')
ax.set_title('Snap Clip Radial Profile vs Normal Wall', fontsize=12, fontweight='bold')
ax.grid(True)
ax.legend()
plt.savefig('clip_profile_rz.png', dpi=160)
print("Saved clip_profile_rz.png")
