"""
Tune and compare gentle continuous crown arc options for snap clips looking top-down.
Compare different crown radii and edge taper depths so user can choose the perfect balance.
Save plot in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon

import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

angle_deg = 45.0
center_rad = math.radians(angle_deg)
p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
r_est = np.linalg.norm(p)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
hook_depth = build_part.CLIP_HOOK_DEPTH
half_w = build_part.CLIP_ARM_WIDTH / 2.0

th_min = center_rad - d_theta / 2.0
th_max = center_rad + d_theta / 2.0

N = 80
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

# Current square profile
shelf_curr = []
for i, th in enumerate(theta_vals):
    po = outer_pts[i]
    n_dir = po / np.linalg.norm(po)
    shelf_curr.append(po + n_dir * hook_depth)
shelf_curr = np.array(shelf_curr)

# Function to generate crown with given edge drop delta_d
# At center: depth = hook_depth = 2.10mm
# At edges: depth = hook_depth - delta_d
def make_crown_profile(delta_d, power=2.0):
    shelf_pts = []
    for i, th in enumerate(theta_vals):
        t = (th - center_rad) * r_est
        frac = abs(t / half_w)
        eff_depth = hook_depth - delta_d * (frac ** power)
        po = outer_pts[i]
        n_dir = po / np.linalg.norm(po)
        shelf_pts.append(po + n_dir * eff_depth)
    return np.array(shelf_pts)

# Circular arc crown with a specific crown radius R_c
# Circle passing through (0, hook_depth) at center, and curving back symmetrically
def make_circular_crown_radius(R_crown):
    shelf_pts = []
    for i, th in enumerate(theta_vals):
        t = (th - center_rad) * r_est
        # sagitta s = R - sqrt(R^2 - t^2)
        val = max(0.0, R_crown**2 - t**2)
        sagitta = R_crown - np.sqrt(val)
        eff_depth = max(0.50, hook_depth - sagitta)
        po = outer_pts[i]
        n_dir = po / np.linalg.norm(po)
        shelf_pts.append(po + n_dir * eff_depth)
    return np.array(shelf_pts)

# Options to compare:
# Option 1: Very subtle crown (delta_d = 0.20mm, edge depth = 1.90mm, 90.5% retention at edges)
crown_subtle = make_crown_profile(delta_d=0.20)

# Option 2: Mild crown (delta_d = 0.35mm, edge depth = 1.75mm, 83.3% retention at edges)
crown_mild = make_crown_profile(delta_d=0.35)

# Option 3: Circular Crown (R = 7.5mm crown radius, sagitta = 0.30mm at edge)
crown_circ = make_circular_crown_radius(R_crown=7.50)

# Option 4: Gentle Flat-top Crown (flat center 2.0mm, gentle blend on sides with delta_d = 0.35mm)
def make_flattop_crown(flat_w=2.0, delta_d=0.35):
    shelf_pts = []
    half_flat = flat_w / 2.0
    for i, th in enumerate(theta_vals):
        t = abs((th - center_rad) * r_est)
        if t <= half_flat:
            eff_depth = hook_depth
        else:
            u = (t - half_flat) / (half_w - half_flat)
            # smooth cosine ease
            eff_depth = hook_depth - delta_d * 0.5 * (1.0 - np.cos(np.pi * u))
        po = outer_pts[i]
        n_dir = po / np.linalg.norm(po)
        shelf_pts.append(po + n_dir * eff_depth)
    return np.array(shelf_pts)

crown_flattop = make_flattop_crown(flat_w=2.0, delta_d=0.35)

fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=200)

configs = [
    ("Option 1: Subtle Crown (0.20mm Edge Ease)", crown_subtle, 0.20, axes[0, 0], '#2e7d32'),
    ("Option 2: Mild Crown (0.35mm Edge Ease)", crown_mild, 0.35, axes[0, 1], '#1565c0'),
    ("Option 3: True Circular Crown Arc (R = 7.5mm)", crown_circ, 0.30, axes[1, 0], '#e65100'),
    ("Option 4: Flat-Top Gentle Crown (2.0mm Flat Crest)", crown_flattop, 0.35, axes[1, 1], '#6a1b9a')
]

for title, s_pts, d_edge, ax, col in configs:
    ax.set_title(title, fontsize=11, fontweight='bold', color=col)
    
    # Outer wall
    ax.plot(outer_pts[:, 0], outer_pts[:, 1], 'b-', lw=2.0, label='Outer Wall')
    # Old square boundary for reference
    ax.plot(shelf_curr[:, 0], shelf_curr[:, 1], 'r--', lw=1.2, alpha=0.5, label='Current Square Edge')
    # New crown profile
    ax.plot(s_pts[:, 0], s_pts[:, 1], color=col, lw=2.5, label='Crowned Outer Edge')
    
    poly = Polygon(np.vstack([outer_pts, s_pts[::-1]]))
    px, py = poly.exterior.xy
    ax.fill(px, py, facecolor=col, alpha=0.25)
    
    # Annotations
    mid_idx = N // 2
    edge_idx = 0
    center_p = s_pts[mid_idx]
    edge_p = s_pts[edge_idx]
    
    ax.annotate(f"Center: Full {hook_depth:.2f}mm Depth\n(100% Full Retention Latch)",
                xy=(center_p[0], center_p[1]),
                xytext=(center_p[0] + 1.2, center_p[1] + 1.8),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=col),
                fontsize=8.5, fontweight='bold', color=col,
                bbox=dict(boxstyle='round', fc='white', ec=col))
                
    ax.annotate(f"Edge Depth: {hook_depth - d_edge:.2f}mm\n(-{d_edge:.2f}mm gentle ease)",
                xy=(edge_p[0], edge_p[1]),
                xytext=(edge_p[0] - 3.2, edge_p[1] + 1.2),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=col),
                fontsize=8.5, fontweight='bold', color=col,
                bbox=dict(boxstyle='round', fc='white', ec=col))

    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(10.5, 18.5)
    ax.set_ylim(11.5, 18.5)
    ax.legend(loc='lower left', fontsize=8)

plt.tight_layout()
out_file = os.path.join(os.path.dirname(__file__), 'gentle_crown_options_comparison.png')
plt.savefig(out_file, dpi=200)
print(f"Saved {out_file}")
