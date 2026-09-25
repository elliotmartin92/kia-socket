import os, sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT
from build_clamp import build_tower_clamp_mesh, build_unified_clamp_mesh

part = trimesh.load('part.stl')
c_left = build_tower_clamp_mesh('left', in_assembly_coords=True)
c_right = build_tower_clamp_mesh('right', in_assembly_coords=True)
c_bridge = build_unified_clamp_mesh(in_assembly_coords=True)

# Slice the part mesh at Z = 4.0mm to get the exact cross section of the walls
slice_part = part.section(plane_origin=[0, 0, 4.0], plane_normal=[0, 0, 1])
slice_2d_part, _ = slice_part.to_planar()

# Also slice at Z = 6.0mm (near top of outer wall)
slice_top = part.section(plane_origin=[0, 0, 6.0], plane_normal=[0, 0, 1])
slice_2d_top, _ = slice_top.to_planar()

# Also slice part at Z = 13.0mm (towers)
slice_towers = part.section(plane_origin=[0, 0, 13.0], plane_normal=[0, 0, 1])
slice_2d_towers, _ = slice_towers.to_planar()

fig, ax = plt.subplots(figsize=(14, 14), facecolor='#1a1a1a', dpi=180)
ax.set_facecolor('#222222')
ax.set_title('Top-Down (X-Y Plane): Part Walls vs Tower Clamps in Assembly', color='white', fontsize=14, weight='bold', pad=15)

# Plot Part walls at Z = 6.0mm
for poly in slice_2d_top.polygons_full:
    x, y = poly.exterior.xy
    ax.plot(x, y, color='#3498db', lw=2, label='Outer Wall @ Z=6.0mm' if 'Outer Wall @ Z=6.0mm' not in ax.get_legend_handles_labels()[1] else '')
    ax.fill(x, y, color='#3498db', alpha=0.15)
    for interior in poly.interiors:
        ix, iy = interior.xy
        ax.plot(ix, iy, color='#2980b9', lw=1.2, linestyle='--')

# Plot towers at Z = 13.0mm
for poly in slice_2d_towers.polygons_full:
    x, y = poly.exterior.xy
    ax.plot(x, y, color='#9b59b6', lw=1.5, label='Towers @ Z=13.0mm' if 'Towers @ Z=13.0mm' not in ax.get_legend_handles_labels()[1] else '')
    ax.fill(x, y, color='#9b59b6', alpha=0.3)

# Plot Left Clamp top-down 2D footprint (convex hull or projection)
c_left_xy = c_left.vertices[:, :2]
c_right_xy = c_right.vertices[:, :2]
c_bridge_xy = c_bridge.vertices[:, :2]

from scipy.spatial import ConvexHull
# Project clamp faces
for name, mesh, col in [('Left Clamp', c_left, '#e67e22'), ('Right Clamp', c_right, '#e74c3c'), ('Bridge Tie Bar', c_bridge, '#2ecc71')]:
    # Slice clamp at Z = 15.0mm (roof)
    sc = mesh.section(plane_origin=[0, 0, 15.0], plane_normal=[0, 0, 1])
    if sc:
        sc2d, _ = sc.to_planar()
        for p in sc2d.polygons_full:
            ax.plot(*p.exterior.xy, color=col, lw=2.5, label=f'{name} Roof @ Z=15mm')
            ax.fill(*p.exterior.xy, color=col, alpha=0.4)

ax.set_xlim(-22, 22)
ax.set_ylim(-20, 22)
ax.set_xlabel('X (mm)', color='white')
ax.set_ylabel('Y (mm)', color='white')
ax.tick_params(colors='white')
ax.grid(True, color='#444444', linestyle=':')
ax.legend(loc='lower left', fontsize=9, facecolor='#111111', labelcolor='white')

plt.tight_layout()
out_p = 'testing/clamp_vs_walls_topdown.png'
plt.savefig(out_p, dpi=180)
print(f'Saved {out_p}')
