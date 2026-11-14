import numpy as np
import trimesh
import os, sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft
from test_candidate_b4_strut import build_strut_option_b, R, z_min, shaft_tilted
from test_robust_b4_strut import build_robust_strut

base_mesh, base_poly = build_part.build_exact_3d_model()
m_tilted = base_mesh.copy().apply_transform(R)
m_tilted.apply_translation([0, 0, -z_min])

full_lever = trimesh.util.concatenate(list(shaft_tilted.values()))

# Isolate Bracket 4
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

# Strut 1: Previous tiny strut (W=0.50mm, tines=0.18mm)
strut_tiny = build_strut_option_b()

# Strut 2: Robust printable strut (W=1.80mm, tines=0.55mm, trunk=1.20mm)
strut_robust = build_robust_strut(x_c=8.90, fork_w=1.80, tine_w=0.55)

fig = plt.figure(figsize=(18, 9), dpi=160)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

for ax, strut_to_show, title, color in [
    (ax1, strut_tiny, "Previous: Tiny 0.50mm Strut (0.18mm tines - Too Small to Print)", '#e91e63'),
    (ax2, strut_robust, "Updated: Robust 1.80mm Y-Strut (0.55mm tines, 1.20mm trunk)", '#4caf50')
]:
    # Bracket 4
    ax.add_collection3d(Poly3DCollection(b4_tilted.vertices[b4_tilted.faces], alpha=0.35, facecolor='#2196f3', edgecolor='#1565c0', lw=0.3))
    # Lever
    ax.add_collection3d(Poly3DCollection(full_lever.vertices[full_lever.faces], alpha=0.70, facecolor='#ff7043', edgecolor='#d84315', lw=0.3))
    # Strut under test
    ax.add_collection3d(Poly3DCollection(strut_to_show.vertices[strut_to_show.faces], alpha=0.95, facecolor=color, edgecolor='#880e4f' if color=='#e91e63' else '#1b5e20', lw=0.5))
    
    ax.set_xlim(6, 12)
    ax.set_ylim(-4, 4)
    ax.set_zlim(18, 28)
    ax.view_init(elev=20, azim=-65)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')

plt.suptitle("Lever Shaft Support Strut Comparison: Tiny (0.5mm) vs Robust (1.8mm)", fontsize=13, fontweight='bold')
plt.tight_layout()
out_png = 'testing/robust_vs_tiny_strut_comparison.png'
plt.savefig(out_png)
print(f"Saved {out_png}")
