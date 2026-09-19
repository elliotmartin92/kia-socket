import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import shapely.geometry as sg
from shapely.geometry import Point, LineString, Polygon
import matplotlib.pyplot as plt

import build_part
from build_shaft import X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER, Y_AXLE, Z_AXLE
from build_clamp import build_tower_clamp_mesh, build_unified_clamp_mesh

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
towers_poly = build_part.create_shaft_support_towers_poly()
towers_mesh = build_part.build_clean_shaft_towers_mesh()
clamp_r = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)

fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=200)

# Panel 1: Top-down 2D view around 45 deg clip and right tower
ax1 = axes[0, 0]
ax1.set_title("1. Top-Down View: 45° Clip vs Right Tower & Clamp", fontsize=11, fontweight='bold')
ox, oy = outer_body_poly.exterior.xy
ax1.plot(ox, oy, 'b-', label='Baseplate Outer Wall')
ix, iy = inner_wall_poly.exterior.xy
ax1.plot(ix, iy, 'b--', label='Baseplate Inner Wall')

for g in (towers_poly.geoms if hasattr(towers_poly, 'geoms') else [towers_poly]):
    tx, ty = g.exterior.xy
    ax1.fill(tx, ty, facecolor='#ffa726', alpha=0.5, edgecolor='#e65100', lw=1.5, label='Shaft Towers')

# 45 deg clip position
p45, n45, _ = build_part.find_boundary_point_and_normal(base_poly, 45.0)
center_rad = np.radians(45.0)
r_est = np.linalg.norm(p45)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
slot_t = build_part.CLIP_SLOT_CLEARANCE
slot_d_theta = slot_t / r_est

# Plot clip arm
th_range = np.linspace(center_rad - d_theta/2, center_rad + d_theta/2, 30)
clip_outer = [np.array([np.cos(th), np.sin(th)]) * r_est for th in th_range]
clip_hook = [p + (p/np.linalg.norm(p)) * build_part.CLIP_HOOK_DEPTH for p in clip_outer]
co = np.array(clip_outer)
ch = np.array(clip_hook)
ax1.plot(co[:,0], co[:,1], 'g-', lw=2.5, label='45° Clip Arm')
ax1.plot(ch[:,0], ch[:,1], 'r-', lw=2.5, label='45° Hook Shelf (2.49mm)')

# Plot right clamp footprint
cx, cy = clamp_r.bounds[:,0], clamp_r.bounds[:,1]
clamp_rect = plt.Rectangle((cx[0], cy[0]), cx[1]-cx[0], cy[1]-cy[0], facecolor='purple', alpha=0.25, edgecolor='purple', lw=1.5, label='Right Tower Clamp Footprint')
ax1.add_patch(clamp_rect)

ax1.set_xlim(8, 18)
ax1.set_ylim(8, 18)
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower left', fontsize=8)

# Panel 2: Clip Hook Profile (Current Knife Edge vs Faced-Off 0.1mm)
ax2 = axes[0, 1]
ax2.set_title("2. Clip Hook Cross-Section: Current vs Faced-Off (-0.10mm)", fontsize=11, fontweight='bold')
r_wall = 0.0
z_shelf = build_part.CLIP_HEIGHT - build_part.CLIP_HOOK_HEIGHT  # 4.97
z_top = build_part.CLIP_HEIGHT  # 6.77
r_hook_current = build_part.CLIP_HOOK_DEPTH  # 2.49
r_hook_faced = r_hook_current - 0.10  # 2.39

# Current knife edge profile: (0, 4.97) -> (2.49, 4.97) -> (0, 6.77)
ax2.plot([0, r_hook_current, 0], [z_shelf, z_shelf, z_top], 'r-', lw=2.0, label='Current Sharp Hook (2.49mm Apex)')
ax2.fill([0, r_hook_current, 0], [z_shelf, z_shelf, z_top], facecolor='red', alpha=0.15)

# Faced-off profile:
# Option A: Direct vertical face cut at r = 2.39mm
z_cut = z_shelf + 0.10 * (z_top - z_shelf) / r_hook_current
ax2.plot([0, r_hook_faced, r_hook_faced, 0], [z_shelf, z_shelf, z_cut, z_top], 'g-', lw=2.5, label=f'Faced-Off Hook (2.39mm Protrusion, Flat Tip)')
ax2.fill([0, r_hook_faced, r_hook_faced, 0], [z_shelf, z_shelf, z_cut, z_top], facecolor='green', alpha=0.2)

ax2.set_xlabel("Radial Protrusion from Outer Wall (mm)", fontsize=9, fontweight='bold')
ax2.set_ylabel("Elevation Z (mm)", fontsize=9, fontweight='bold')
ax2.set_xlim(-0.2, 2.8)
ax2.set_ylim(4.5, 7.2)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right', fontsize=9)

# Panel 3: Clamp Protrusion vs Baseplate Outer Wall
ax3 = axes[1, 0]
ax3.set_title("3. Right Tower Clamp Protrusion Beyond Baseplate (Mating Interference)", fontsize=11, fontweight='bold')
ax3.plot(ox, oy, 'b-', lw=2, label='Baseplate Perimeter')
v_clamp = clamp_r.vertices
ax3.scatter(v_clamp[:,0], v_clamp[:,1], c='purple', s=10, alpha=0.6, label='Right Clamp Vertices')
ax3.set_xlim(12, 18)
ax3.set_ylim(5, 15)
ax3.set_aspect('equal')
ax3.grid(True, alpha=0.3)
ax3.legend(loc='lower left', fontsize=9)

# Panel 4: Tower Cradle Snap Throat & Shaft Pin
ax4 = axes[1, 1]
ax4.set_title("4. Tower Cradle Snap Throat vs Shaft Rocker Pin", fontsize=11, fontweight='bold')
# Cradle circle
pin_c = plt.Circle((Y_AXLE, Z_AXLE), 2.80/2.0, facecolor='#90caf9', edgecolor='#1976d2', lw=2, label='Shaft Rocker Pin (Ø2.80mm)')
ax4.add_patch(pin_c)
ax4.axvline(Y_AXLE - build_part.TOWER_THROAT_W/2.0, color='red', linestyle='--', label=f'Throat Width ({build_part.TOWER_THROAT_W:.2f}mm)')
ax4.axvline(Y_AXLE + build_part.TOWER_THROAT_W/2.0, color='red', linestyle='--')
ax4.set_xlim(Y_AXLE - 3.0, Y_AXLE + 3.0)
ax4.set_ylim(Z_AXLE - 2.5, Z_AXLE + 3.5)
ax4.set_aspect('equal')
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper right', fontsize=9)

plt.tight_layout()
out_img = os.path.join(os.path.dirname(__file__), 'diagnostic_clip_and_mating_analysis.png')
plt.savefig(out_img)
print(f"Saved diagnostic plot: {out_img}")
