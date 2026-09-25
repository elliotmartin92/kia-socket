import sys, os
sys.path.insert(0, '.')
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from build_part import get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT
import build_clamp

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

clamp_bridge = build_clamp.build_unified_clamp_mesh(in_assembly_coords=True)
clamp_r = build_clamp.build_tower_clamp_mesh('right', in_assembly_coords=True)
clamp_l = build_clamp.build_tower_clamp_mesh('left', in_assembly_coords=True)

# Also load part.stl
part = trimesh.load('part.stl')

fig, axes = plt.subplots(1, 2, figsize=(18, 9), facecolor='#111111')

for ax in axes:
    ax.set_facecolor('#1a1a1a')
    ax.tick_params(colors='white')
    ax.grid(True, color='#333333', linestyle=':')

# Left plot: Full baseplate top-down view
ax1, ax2 = axes

# Plot wall exterior and interior
ox, oy = outer_body_poly.exterior.xy
ix, iy = inner_poly.exterior.xy

for ax in [ax1, ax2]:
    ax.plot(ox, oy, color='#00d2d3', lw=2.0, label='Outer Wall Exterior Face')
    ax.plot(ix, iy, color='#54a0ff', lw=1.5, linestyle='--', label='Outer Wall Interior Face')

# Plot clamp top-down projection
# Project clamp 3D faces to 2D
v_b = clamp_bridge.vertices
f_b = clamp_bridge.faces

# Color code clamp vertices/faces:
# Inside inner wall (cavity): Green
# Between inner & outer wall (encroaching into wall thickness): Orange
# Outside outer wall (sticking out past baseplate!): Red

for name, mesh, c_base in [('Bridge Tie Bar', clamp_bridge, '#ff9f43')]:
    for f in mesh.faces:
        pts = mesh.vertices[f, :2]
        # centroid of face
        c = pts.mean(axis=0)
        p = Point(c[0], c[1])
        if not outer_body_poly.contains(p):
            col = '#ff4757' # Red: outside outer wall!
        elif not inner_poly.contains(p):
            col = '#ffa502' # Orange: inside wall rim!
        else:
            col = '#2ed573' # Green: completely inside housing interior!
        poly_patch = plt.Polygon(pts, facecolor=col, edgecolor='none', alpha=0.6)
        ax1.add_patch(poly_patch)
        poly_patch2 = plt.Polygon(pts, facecolor=col, edgecolor='none', alpha=0.6)
        ax2.add_patch(poly_patch2)

ax1.set_xlim(-22, 22)
ax1.set_ylim(-20, 22)
ax1.set_aspect('equal')
ax1.set_title('Full Baseplate Top-Down: Wall vs Clamp Encroachment', color='white', fontsize=13, weight='bold')
ax1.legend(loc='lower left', facecolor='#222222', labelcolor='white')

# Right plot: Zoomed into Right Tower and Clamp
ax2.set_xlim(11, 18)
ax2.set_ylim(4, 15)
ax2.set_aspect('equal')
ax2.set_title('Zoomed View: Right Tower Clamp vs Wall Faces', color='white', fontsize=13, weight='bold')

# Add legend patches
import matplotlib.patches as mpatches
green_patch = mpatches.Patch(color='#2ed573', label='Clamp Inside Interior Cavity')
orange_patch = mpatches.Patch(color='#ffa502', label='Clamp Encroaching into Wall Rim')
red_patch = mpatches.Patch(color='#ff4757', label='Clamp Protruding OUTSIDE Outer Wall!')
handles, labels = ax2.get_legend_handles_labels()
handles.extend([green_patch, orange_patch, red_patch])
ax2.legend(handles=handles, loc='upper left', facecolor='#222222', labelcolor='white', fontsize=9)

out_path = 'testing/render_topdown_assembly_wall_check.png'
plt.tight_layout()
plt.savefig(out_path, dpi=200)
print(f"Saved {out_path}")
