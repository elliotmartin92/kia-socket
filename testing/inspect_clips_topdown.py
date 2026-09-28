"""
Inspect clips looking top-down in the XY plane.
Save plot in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon

import build_part

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)

# Let's inspect the 4 clips in top-down view
fig, axes = plt.subplots(2, 2, figsize=(14, 14), dpi=200)

for idx, angle_deg in enumerate(build_part.CLIP_ANGLES):
    ax = axes[idx // 2, idx % 2]
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    slot_t = build_part.CLIP_SLOT_CLEARANCE
    slot_d_theta = slot_t / r_est
    hook_depth = build_part.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, build_part.CLIP_HOOK_DEPTH)
    
    # Outer body poly
    ox, oy = outer_body_poly.exterior.xy
    ax.plot(ox, oy, 'b-', lw=1.5, label='Outer Wall')
    ix, iy = inner_wall_poly.exterior.xy
    ax.plot(ix, iy, 'b--', lw=1.0, label='Inner Wall')
    
    # Clip arm boundaries
    th_min = center_rad - d_theta / 2.0
    th_max = center_rad + d_theta / 2.0
    
    # Hook shelf outline
    N = 32
    theta_vals = np.linspace(th_min, th_max, N)
    outer_pts = []
    shelf_pts = []
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
        outer_pts.append(po)
        shelf_pts.append(ps)
        
    outer_pts = np.array(outer_pts)
    shelf_pts = np.array(shelf_pts)
    
    # The current hook shelf polygon in top-down view:
    # outer_pts along the wall, shelf_pts along the outer hook boundary, closed by the two straight ends
    hook_poly_topdown = np.vstack([outer_pts, shelf_pts[::-1]])
    ax.fill(hook_poly_topdown[:, 0], hook_poly_topdown[:, 1], facecolor='#ef5350', alpha=0.4, edgecolor='red', lw=2, label=f'Current Hook (Depth={hook_depth}mm)')
    
    # Plot slot cuts
    for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
        sp1 = np.array([np.cos(th_slot), np.sin(th_slot)]) * (r_est - 2.5)
        sp2 = np.array([np.cos(th_slot), np.sin(th_slot)]) * (r_est + hook_depth + 1.0)
        ax.plot([sp1[0], sp2[0]], [sp1[1], sp2[1]], 'k--', lw=1.5, label='Flex Slot Cut')
        
    ax.set_title(f'Clip at {angle_deg}° (Top-Down View)', fontsize=11, fontweight='bold')
    ax.set_xlim(p[0] - 6, p[0] + 6)
    ax.set_ylim(p[1] - 6, p[1] + 6)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    if idx == 0:
        ax.legend(loc='lower left', fontsize=8)

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'topdown_clip_inspection.png')
plt.savefig(out_path, dpi=200)
print(f"Saved {out_path}")
