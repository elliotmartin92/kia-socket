import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from build_shaft import build_shaft_rocker_mesh as build_orig_shaft, Y_AXLE, Z_AXLE
from test_reinforced_shaft import build_heavy_duty_shaft_v2

orig_shaft = build_orig_shaft(in_assembly_coords=True)
new_shaft = build_heavy_duty_shaft_v2(in_assembly_coords=True)
part_mesh = trimesh.load('part.stl')

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=160)

# Panel 1: Top-Down X-Y comparison of Shafts & Towers & Through-Hole
ax = axes[0]
# Plot Through-hole
hole_rect = plt.Rectangle((7.608, 8.570), 5.352, 4.512, fill=True, color='#ffebee', ec='#c62828', lw=1.5, label='Through-Hole (5.35x4.51mm)')
ax.add_patch(hole_rect)

# Left & Right Towers
tower_l = plt.Rectangle((4.25, 6.0), 1.25, 4.0, fill=True, color='#fce4ec', ec='#ad1457', lw=1.5, label='Left Tower (4.25-5.50mm)')
tower_r = plt.Rectangle((13.36, 6.0), 1.25, 4.0, fill=True, color='#fce4ec', ec='#ad1457', lw=1.5, label='Right Tower (13.36-14.61mm)')
ax.add_patch(tower_l)
ax.add_patch(tower_r)

# Plot Original Shaft X-Y silhouette
v_orig = orig_shaft.vertices
ax.scatter(v_orig[:, 0], v_orig[:, 1], c='gray', s=1, alpha=0.3, label='Original Shaft (3.80mm Plunger, Ø2.80 Trunk)')

# Plot New Reinforced Shaft X-Y silhouette
v_new = new_shaft.vertices
ax.scatter(v_new[:, 0], v_new[:, 1], c='blue', s=2, alpha=0.6, label='Reinforced Shaft (4.60mm Plunger, Ø3.20 Trunk, Gusset)')

ax.set_xlim(2, 18)
ax.set_ylim(2, 14)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Top-Down View: Shaft Rocker in Assembly & Towers', fontsize=11, fontweight='bold')
ax.legend(loc='upper left', fontsize=8.5)

# Panel 2: Side Y-Z Cross Section Profile Comparison
ax = axes[1]
# Axle center
ax.plot(Y_AXLE, Z_AXLE, 'r+', markersize=12, markeredgewidth=2, label='Shaft Pivot Axis (Y=7.67, Z=12.59)')

# Original Plunger & Cam Y-Z silhouette
v_orig_yz = orig_shaft.vertices[(orig_shaft.vertices[:, 0] > 8.0) & (orig_shaft.vertices[:, 0] < 12.0)]
ax.scatter(v_orig_yz[:, 1], v_orig_yz[:, 2], c='gray', s=2, alpha=0.3, label='Original Profile (2.0mm root)')

# New Plunger & Cam Y-Z silhouette
v_new_yz = new_shaft.vertices[(new_shaft.vertices[:, 0] > 8.0) & (new_shaft.vertices[:, 0] < 12.0)]
ax.scatter(v_new_yz[:, 1], v_new_yz[:, 2], c='blue', s=3, alpha=0.6, label='Reinforced Profile (3.2mm root + Ø4.4mm boss)')

# Base floor reference (Z = 0 datum, thickness 1.0mm)
ax.axhspan(0, 1.0, color='silver', alpha=0.5, label='Base Floor (Z=0 to 1.0mm)')
ax.axhline(-6.50, color='green', linestyle='--', label='PCB Switch Contact (Z=-6.50mm)')

ax.set_xlim(2, 14)
ax.set_ylim(-7.5, 15.5)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Side Y-Z Section: Root Reinforcement & Plunger Reach', fontsize=11, fontweight='bold')
ax.legend(loc='lower left', fontsize=8.5)

plt.tight_layout()
plt.savefig('testing/shaft_reinforcement_comparison.png', dpi=160)
print("Saved testing/shaft_reinforcement_comparison.png")
