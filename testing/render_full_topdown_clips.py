"""
Render full part top-down view showing all 4 clips in context.
Save plot in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon
import shapely.affinity as affinity

import build_part

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)

fig, ax = plt.subplots(figsize=(12, 12), dpi=200)
ax.set_title("Full Baseplate Top-Down View: 4 Perimeter Clips", fontsize=14, fontweight='bold')

# Plot baseplate
bx, by = base_poly.exterior.xy
ax.plot(bx, by, 'k-', lw=1.5, label='Baseplate Perimeter')
ox, oy = outer_body_poly.exterior.xy
ax.plot(ox, oy, 'b-', lw=1.5, label='Outer Wall')
ix, iy = inner_wall_poly.exterior.xy
ax.plot(ix, iy, 'b--', lw=1.0, label='Inner Wall')

# Plot each clip
for angle_deg in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle_deg)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    hook_depth = build_part.CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, build_part.CLIP_HOOK_DEPTH)
    
    # Clip arm boundaries
    th_min = center_rad - d_theta / 2.0
    th_max = center_rad + d_theta / 2.0
    
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
    
    hook_poly_topdown = np.vstack([outer_pts, shelf_pts[::-1]])
    ax.fill(hook_poly_topdown[:, 0], hook_poly_topdown[:, 1], facecolor='#ef5350', alpha=0.6, edgecolor='red', lw=2)
    
    # Annotate clip
    mid_p = shelf_pts[len(shelf_pts)//2]
    ax.annotate(f"Clip {angle_deg}°\n(Sharp square corners in top-down!)",
                xy=(mid_p[0], mid_p[1]),
                xytext=(mid_p[0] * 1.25, mid_p[1] * 1.25),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='red'),
                fontsize=9, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', fc='#ffebee', ec='red'))

ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.set_xlim(-26, 26)
ax.set_ylim(-26, 26)
ax.legend(loc='lower right')

plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'full_baseplate_clips_topdown.png')
plt.savefig(out_path, dpi=200)
print(f"Saved {out_path}")
