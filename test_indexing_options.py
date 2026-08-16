"""
Visualize indexing options for separate 3D printable backside slit walls.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    get_exact_base_polygon, create_backside_slit_bosses_poly,
    BASE_THICK, SLIT_BOSS_HEIGHT, SLIT_W_X, SLIT_LEN_Y, OUTER_WALL_THICK
)

# Left slit: X in [-8.953, -7.853], Y in [-16.339, -13.339]
# Right slit: X in [7.853, 8.953], Y in [-16.339, -13.339]
# Slit boss outer wall: 1.20mm thick -> Left boss: X in [-10.153, -6.653], Y in [-17.539, -12.139]

# Option A: Monolithic Dual-Slit Insert with Plug Keys
# Base connecting flange plate: Y in [-17.539, -12.139], X in [-10.153, 10.153], thickness = 0.8mm
# Two protruding slit walls: protruding 2.47mm below the flange
# Two indexing alignment plugs: protruding 0.90mm into +Z (to insert into the 1.1x3.0mm slits)

# Option B: Two Individual Slit Inserts with Alignment Plugs
# Left Insert and Right Insert separately.

fig = plt.figure(figsize=(16, 8), dpi=160)

# 1. 2D Diagram of Main Baseplate Bottom and Insert Part
ax1 = fig.add_subplot(1, 2, 1)

# Slit through holes on main part
slit_left = box(-8.953, -16.339, -7.853, -13.339)
slit_right = box(7.853, -16.339, 8.953, -13.339)
boss_left = box(-10.153, -17.539, -6.653, -12.139)
boss_right = box(6.653, -17.539, 10.153, -12.139)

ax1.plot(*slit_left.exterior.xy, 'r-', linewidth=2, label='1.1x3.0mm Through Slits in Main Part')
ax1.plot(*slit_right.exterior.xy, 'r-', linewidth=2)
ax1.plot(*boss_left.exterior.xy, 'b--', linewidth=1.5, label='Slit Protruding Wall Footprint')
ax1.plot(*boss_right.exterior.xy, 'b--', linewidth=1.5)

# Optional connecting alignment bridge (Option 1)
bridge_box = box(-10.153, -15.5, 10.153, -14.0)
ax1.plot(*bridge_box.exterior.xy, 'g:', linewidth=1.5, label='Monolithic Alignment Bridge (Option 1)')

ax1.set_xlim(-13, 13)
ax1.set_ylim(-19, -10)
ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_title('2D Plan View: Slits & Indexing Geometry', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8.5)

# 2. 3D Exploded View of Main Part (Flat Bottom) and Separate Insert
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

# Main part base bottom at Z = 0
base_poly, _, _ = get_exact_base_polygon()
m_base = trimesh.creation.extrude_polygon(base_poly, height=1.0)
from build_part import extrude_shapely_geom

# Slit walls separate part (exploded down by 5mm)
m_bosses = extrude_shapely_geom(create_backside_slit_bosses_poly(), height=2.47)
m_bosses.apply_translation([0, 0, -2.47 - 5.0]) # Exploded down

# Add alignment plugs on the insert (protruding up into the slits)
plug_left = trimesh.creation.box([0.95, 2.85, 1.20])
plug_left.apply_translation([-8.403, -14.839, -5.0 + 0.60])
plug_right = trimesh.creation.box([0.95, 2.85, 1.20])
plug_right.apply_translation([8.403, -14.839, -5.0 + 0.60])

col_base = Poly3DCollection(m_base.vertices[m_base.faces], alpha=0.7, edgecolor='#333333', linewidths=0.2)
col_base.set_facecolor('#00bcd4')
ax2.add_collection3d(col_base)

col_bosses = Poly3DCollection(m_bosses.vertices[m_bosses.faces], alpha=0.9, edgecolor='#111111', linewidths=0.3)
col_bosses.set_facecolor('#e91e63')
ax2.add_collection3d(col_bosses)

col_plug1 = Poly3DCollection(plug_left.vertices[plug_left.faces], alpha=0.9, edgecolor='#111111', linewidths=0.3)
col_plug1.set_facecolor('#ff9800')
ax2.add_collection3d(col_plug1)

col_plug2 = Poly3DCollection(plug_right.vertices[plug_right.faces], alpha=0.9, edgecolor='#111111', linewidths=0.3)
col_plug2.set_facecolor('#ff9800')
ax2.add_collection3d(col_plug2)

ax2.set_xlim(-15, 15)
ax2.set_ylim(-20, 0)
ax2.set_zlim(-10, 5)
ax2.view_init(elev=25, azim=-60)
ax2.set_title('3D Exploded View: Flat Main Bed + Separate Indexed Inserts', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('separate_slit_indexing_preview.png', dpi=160)
print("Saved separate_slit_indexing_preview.png")
