"""
Inspect the insert and its surrounding walls in the assembly.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    build_exact_3d_model, build_slit_insert_mesh, build_indexed_assembly_mesh,
    get_exact_base_polygon, OUTER_WALL_THICK, SLIT_BOSS_HEIGHT
)

part_mesh, base_poly = build_exact_3d_model()
insert_mesh = build_slit_insert_mesh()
assembly_mesh = build_indexed_assembly_mesh(part_mesh, insert_mesh)

fig = plt.figure(figsize=(18, 12), dpi=160)

# 1. 2D Bottom Plan View of Slit Area (X in [-15, 15], Y in [-20, -10])
ax1 = fig.add_subplot(2, 2, 1)
# Base polygon exterior & interior
if base_poly.geom_type == 'Polygon':
    ax1.plot(*base_poly.exterior.xy, 'k-', linewidth=2, label='Outer Perimeter Wall Base')
    for interior in base_poly.interiors:
        ax1.plot(*interior.xy, 'r-', linewidth=1.5, label='Through-Slit Hole' if interior.bounds[0] < 0 else "")

# Left & Right insert outer footprint in assembly
ins_left_box = box(-8.403 - 3.5/2, -14.839 - 5.4/2, -8.403 + 3.5/2, -14.839 + 5.4/2)
ins_right_box = box(8.403 - 3.5/2, -14.839 - 5.4/2, 8.403 + 3.5/2, -14.839 + 5.4/2)
ax1.plot(*ins_left_box.exterior.xy, 'b--', linewidth=2, label='Insert Outer Wall Footprint')
ax1.plot(*ins_right_box.exterior.xy, 'b--', linewidth=2)

ax1.set_xlim(-14, 14)
ax1.set_ylim(-20, -9)
ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_title('2D Plan View of Slit Inserts vs Perimeter Walls', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8.5)

# 2. 3D Close-up from Bottom / Underside
ax2 = fig.add_subplot(2, 2, 2, projection='3d')
# Crop assembly around left slit
col_part = Poly3DCollection(part_mesh.vertices[part_mesh.faces], alpha=0.6, edgecolor='#555555', linewidths=0.2)
col_part.set_facecolor('#4A90E2')
ax2.add_collection3d(col_part)

# Left insert
ins_left = insert_mesh.copy()
ins_left.apply_translation([-8.403, -14.839, -SLIT_BOSS_HEIGHT])
col_ins = Poly3DCollection(ins_left.vertices[ins_left.faces], alpha=0.95, edgecolor='#111111', linewidths=0.3)
col_ins.set_facecolor('#e91e63')
ax2.add_collection3d(col_ins)

ax2.set_xlim(-13, -4)
ax2.set_ylim(-19, -10)
ax2.set_zlim(-4, 3)
ax2.view_init(elev=-50, azim=220)
ax2.set_title('3D Underside View of Left Insert Mated into Base', fontsize=12, fontweight='bold')

# 3. Y-Z Cross Section at X = -8.403mm (through center of left slit)
ax3 = fig.add_subplot(2, 2, 3)
# Slit is at Y in [-16.339, -13.339], floor at Z in [0, 1.0]
# Perimeter bottom tab is at Y in [-18.539, -17.339], wall Z in [1.0, 6.77]
# Insert body is at Y in [-17.539, -12.139], Z in [-2.47, 0.0]
# Insert key is at Y in [-16.264, -13.414], Z in [0.0, 0.85]
floor_rect = plt.Rectangle((-18.539, 0), 18.539 - 5.0, 1.0, facecolor='#4A90E2', alpha=0.5, edgecolor='black', label='Floor (Z=0 to 1mm)')
wall_rect = plt.Rectangle((-18.539, 1.0), 1.20, 5.77, facecolor='#1f77b4', alpha=0.7, edgecolor='black', label='Outer Wall (1.2mm thick)')
ins_body_rect = plt.Rectangle((-17.539, -2.47), 5.40, 2.47, facecolor='#e91e63', alpha=0.6, edgecolor='black', label='Insert Body (Z=-2.47 to 0)')
ins_key_rect = plt.Rectangle((-16.264, 0), 2.85, 0.85, facecolor='#ff9800', alpha=0.8, edgecolor='black', label='Insert Key in Slit (Z=0 to 0.85)')

ax3.add_patch(floor_rect)
ax3.add_patch(wall_rect)
ax3.add_patch(ins_body_rect)
ax3.add_patch(ins_key_rect)

# Add dimension annotations
ax3.annotate('Bottom Wall (Y=-18.54 to -17.34)', xy=(-17.94, 2.0), xytext=(-20.5, 4.0),
             arrowprops=dict(arrowstyle='->', lw=1.5), fontsize=9)
ax3.annotate('Gap to Wall:\n1.00mm', xy=(-17.44, -1.0), xytext=(-20.0, -1.0),
             arrowprops=dict(arrowstyle='<->', color='red', lw=1.5), fontsize=9, fontweight='bold', color='red')

ax3.set_xlim(-22, -9)
ax3.set_ylim(-3.5, 7.5)
ax3.set_aspect('equal')
ax3.grid(True)
ax3.set_xlabel('Y (mm)')
ax3.set_ylabel('Z (mm)')
ax3.set_title('Cross-Section through Slit: Notice the 1.00mm Gap to Bottom Wall', fontsize=11, fontweight='bold')
ax3.legend(loc='upper right', fontsize=8)

# 4. 3D Top-Side view through the floor
ax4 = fig.add_subplot(2, 2, 4, projection='3d')
col_part4 = Poly3DCollection(part_mesh.vertices[part_mesh.faces], alpha=0.6, edgecolor='#555555', linewidths=0.2)
col_part4.set_facecolor('#4A90E2')
col_ins4 = Poly3DCollection(ins_left.vertices[ins_left.faces], alpha=0.95, edgecolor='#111111', linewidths=0.3)
col_ins4.set_facecolor('#e91e63')
ax4.add_collection3d(col_part4)
ax4.add_collection3d(col_ins4)
ax4.set_xlim(-13, -4)
ax4.set_ylim(-19, -10)
ax4.set_zlim(-4, 4)
ax4.view_init(elev=35, azim=45)
ax4.set_title('3D Top-Side View: Key Protruding into Slit', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('inspect_insert_gap.png', dpi=160)
print("Saved inspect_insert_gap.png")
