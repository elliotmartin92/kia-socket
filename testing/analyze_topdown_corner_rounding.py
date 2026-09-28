"""
Explore and visualize top-down corner rounding options for snap clips:
Option 1: Filleted outer corners (R = 0.8mm - 1.2mm radius)
Option 2: Crowned circular arc in top-down (concentric / matching outer circle)
Option 3: Flat central retention plateau (e.g. 2.4mm wide) with tangent rounded corners
Save plot in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, box
import shapely.affinity as affinity

import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)

# Focus on the 45 degree clip
angle_deg = 45.0
center_rad = math.radians(angle_deg)
p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
r_est = np.linalg.norm(p)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
hook_depth = build_part.CLIP_HOOK_DEPTH
slot_t = build_part.CLIP_SLOT_CLEARANCE
slot_d_theta = slot_t / r_est

# Generate base clip polygon
th_min = center_rad - d_theta / 2.0
th_max = center_rad + d_theta / 2.0

N = 64
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

# Base square clip polygon
poly_square = Polygon(np.vstack([outer_pts, shelf_pts[::-1]]))

# Option 1: Fillet outer corners using shapely buffer tricks or parametric geometry
# In local clip coordinates (tangential t, radial n):
# t in [-W/2, W/2], n in [0, hook_depth]
# Fillet radius R_f = 0.80mm at outer corners (t = +/- W/2, n = hook_depth)
def make_filleted_shelf_pts(corner_r=0.80):
    new_shelf = []
    half_w = build_part.CLIP_ARM_WIDTH / 2.0
    for i, th in enumerate(theta_vals):
        # arc distance from center
        t = (th - center_rad) * r_est
        # if |t| > half_w - corner_r: round off radially
        if abs(t) > half_w - corner_r:
            dt = abs(t) - (half_w - corner_r)
            # circle equation: dn = corner_r - sqrt(corner_r^2 - dt^2)
            val = max(0.0, corner_r**2 - dt**2)
            delta_n = corner_r - np.sqrt(val)
            eff_depth = max(0.40, hook_depth - delta_n)
        else:
            eff_depth = hook_depth
        po = outer_pts[i]
        n_dir = po / np.linalg.norm(po)
        new_shelf.append(po + n_dir * eff_depth)
    return np.array(new_shelf)

shelf_fillet_08 = make_filleted_shelf_pts(corner_r=0.80)
shelf_fillet_12 = make_filleted_shelf_pts(corner_r=1.20)

# Option 2: Continuous parabolic / circular crown across entire width
# eff_depth(t) = hook_depth * (1 - 0.40 * (t / half_w)^2)
def make_crowned_shelf_pts(taper_frac=0.35):
    new_shelf = []
    half_w = build_part.CLIP_ARM_WIDTH / 2.0
    for i, th in enumerate(theta_vals):
        t = (th - center_rad) * r_est
        factor = 1.0 - taper_frac * (t / half_w)**2
        eff_depth = hook_depth * factor
        po = outer_pts[i]
        n_dir = po / np.linalg.norm(po)
        new_shelf.append(po + n_dir * eff_depth)
    return np.array(new_shelf)

shelf_crowned = make_crowned_shelf_pts(taper_frac=0.30)

fig, axes = plt.subplots(2, 2, figsize=(15, 14), dpi=200)

# Panel 1: Current vs Option 1 (R=0.8mm filleted corners)
ax1 = axes[0, 0]
ax1.set_title("Current Design: Sharp Square Corners (Top-Down View)", fontsize=11, fontweight='bold', color='#c62828')
ax1.plot(outer_pts[:,0], outer_pts[:,1], 'b-', lw=2.0, label='Outer Wall')
ax1.plot(shelf_pts[:,0], shelf_pts[:,1], 'r-', lw=2.5, label=f'Outer Edge (Depth = {hook_depth:.2f}mm)')
poly_curr = Polygon(np.vstack([outer_pts, shelf_pts[::-1]]))
cx, cy = poly_curr.exterior.xy
ax1.fill(cx, cy, facecolor='#ef5350', alpha=0.3)
# Mark sharp corners
ax1.plot([shelf_pts[0,0], shelf_pts[-1,0]], [shelf_pts[0,1], shelf_pts[-1,1]], 'ro', markersize=8)
ax1.annotate("Sharp 90° Corner\n(Bites into female bore!)", xy=(shelf_pts[0,0], shelf_pts[0,1]),
             xytext=(shelf_pts[0,0]-3, shelf_pts[0,1]+1.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='red'),
             fontsize=9, fontweight='bold', color='red', bbox=dict(boxstyle='round', fc='white', ec='red'))
ax1.annotate("Sharp 90° Corner\n(Bites into female bore!)", xy=(shelf_pts[-1,0], shelf_pts[-1,1]),
             xytext=(shelf_pts[-1,0]+1.5, shelf_pts[-1,1]-1.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='red'),
             fontsize=9, fontweight='bold', color='red', bbox=dict(boxstyle='round', fc='white', ec='red'))
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(10, 19)
ax1.set_ylim(11, 19)
ax1.legend(loc='lower left', fontsize=8.5)

# Panel 2: Option A - Moderate Corner Fillets (R = 0.80mm)
ax2 = axes[0, 1]
ax2.set_title("Option A: Moderate Corner Radii (R = 0.80mm Fillet)", fontsize=11, fontweight='bold', color='#2e7d32')
ax2.plot(outer_pts[:,0], outer_pts[:,1], 'b-', lw=2.0, label='Outer Wall')
ax2.plot(shelf_pts[:,0], shelf_pts[:,1], 'r--', lw=1.5, alpha=0.5, label='Old Square Boundary')
ax2.plot(shelf_fillet_08[:,0], shelf_fillet_08[:,1], 'g-', lw=2.5, label='R=0.80mm Rounded Corners')
poly_f08 = Polygon(np.vstack([outer_pts, shelf_fillet_08[::-1]]))
cx, cy = poly_f08.exterior.xy
ax2.fill(cx, cy, facecolor='#a5d6a7', alpha=0.4)
ax2.annotate("Smooth R=0.80mm Fillet\n(Slides freely into bore)", xy=(shelf_fillet_08[2,0], shelf_fillet_08[2,1]),
             xytext=(shelf_fillet_08[2,0]-3, shelf_fillet_08[2,1]+1.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=9, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round', fc='white', ec='#2e7d32'))
ax2.annotate("Central Retention Plateau (2.60mm wide)\n100% full 2.10mm depth!",
             xy=(shelf_fillet_08[N//2,0], shelf_fillet_08[N//2,1]),
             xytext=(shelf_fillet_08[N//2,0]+1, shelf_fillet_08[N//2,1]+2),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=9, fontweight='bold', color='#1b5e20', bbox=dict(boxstyle='round', fc='white', ec='#2e7d32'))
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(10, 19)
ax2.set_ylim(11, 19)
ax2.legend(loc='lower left', fontsize=8.5)

# Panel 3: Option B - Generous Corner Fillets (R = 1.20mm)
ax3 = axes[1, 0]
ax3.set_title("Option B: Generous Corner Radii (R = 1.20mm Fillet)", fontsize=11, fontweight='bold', color='#1565c0')
ax3.plot(outer_pts[:,0], outer_pts[:,1], 'b-', lw=2.0, label='Outer Wall')
ax3.plot(shelf_pts[:,0], shelf_pts[:,1], 'r--', lw=1.5, alpha=0.5, label='Old Square Boundary')
ax3.plot(shelf_fillet_12[:,0], shelf_fillet_12[:,1], 'm-', lw=2.5, label='R=1.20mm Rounded Corners')
poly_f12 = Polygon(np.vstack([outer_pts, shelf_fillet_12[::-1]]))
cx, cy = poly_f12.exterior.xy
ax3.fill(cx, cy, facecolor='#ce93d8', alpha=0.4)
ax3.annotate("R=1.20mm Bullet Nose\n(Vastly lower insertion force)", xy=(shelf_fillet_12[2,0], shelf_fillet_12[2,1]),
             xytext=(shelf_fillet_12[2,0]-3, shelf_fillet_12[2,1]+1.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='purple'),
             fontsize=9, fontweight='bold', color='purple', bbox=dict(boxstyle='round', fc='white', ec='purple'))
ax3.annotate("Central Retention Plateau (1.80mm wide)\nFull 2.10mm depth!",
             xy=(shelf_fillet_12[N//2,0], shelf_fillet_12[N//2,1]),
             xytext=(shelf_fillet_12[N//2,0]+1, shelf_fillet_12[N//2,1]+2),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='purple'),
             fontsize=9, fontweight='bold', color='purple', bbox=dict(boxstyle='round', fc='white', ec='purple'))
ax3.set_aspect('equal')
ax3.grid(True, alpha=0.3)
ax3.set_xlim(10, 19)
ax3.set_ylim(11, 19)
ax3.legend(loc='lower left', fontsize=8.5)

# Panel 4: Option C - Continuous Circular Crown
ax4 = axes[1, 1]
ax4.set_title("Option C: Continuous Crown Arc (Matching Outer Bore)", fontsize=11, fontweight='bold', color='#e65100')
ax4.plot(outer_pts[:,0], outer_pts[:,1], 'b-', lw=2.0, label='Outer Wall')
ax4.plot(shelf_pts[:,0], shelf_pts[:,1], 'r--', lw=1.5, alpha=0.5, label='Old Square Boundary')
ax4.plot(shelf_crowned[:,0], shelf_crowned[:,1], '#e65100', lw=2.5, label='Crowned Circular Arc')
poly_cr = Polygon(np.vstack([outer_pts, shelf_crowned[::-1]]))
cx, cy = poly_cr.exterior.xy
ax4.fill(cx, cy, facecolor='#ffcc80', alpha=0.4)
ax4.annotate("Continuous smooth circular arc\nMatching outer diameter profile", xy=(shelf_crowned[N//2,0], shelf_crowned[N//2,1]),
             xytext=(shelf_crowned[N//2,0]-2, shelf_crowned[N//2,1]+2),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#e65100'),
             fontsize=9, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round', fc='white', ec='#e65100'))
ax4.set_aspect('equal')
ax4.grid(True, alpha=0.3)
ax4.set_xlim(10, 19)
ax4.set_ylim(11, 19)
ax4.legend(loc='lower left', fontsize=8.5)

plt.tight_layout()
out_fig = os.path.join(os.path.dirname(__file__), 'topdown_corner_rounding_options.png')
plt.savefig(out_fig, dpi=200)
print(f"Saved {out_fig}")
