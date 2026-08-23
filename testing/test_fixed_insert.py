"""
Build and test the fixed 1-piece monolithic slit insert.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import extrude_shapely_geom, SLIT_BOSS_HEIGHT

def build_fixed_slit_insert_mesh(is_hollow=True, inner_hole_w=0.60, inner_hole_l=2.40):
    """Builds a 100% monolithic, contiguous 3D-printable slit insert part.
    - Outer body: 3.50mm x 5.40mm from Z = 0 to Z = 2.47mm
    - Continuous horizontal shoulder at Z = 2.47mm stepping inward
    - Raised indexing key: 0.95mm x 2.85mm from Z = 2.47mm to Z = 3.32mm (0.85mm key height)
    - Continuous through-hole of 0.60mm x 2.40mm from Z = 0 to Z = 3.32mm (or solid)
    """
    # 1. Lower Body: Outer 3.50 x 5.40mm, Inner 0.60 x 2.40mm (Z: 0 to 2.47mm)
    outer_body = box(-3.50/2, -5.40/2, 3.50/2, 5.40/2)
    inner_hole = box(-inner_hole_w/2, -inner_hole_l/2, inner_hole_w/2, inner_hole_l/2)
    
    if is_hollow:
        poly_body = outer_body.difference(inner_hole)
    else:
        poly_body = outer_body
    m_body = extrude_shapely_geom(poly_body, height=SLIT_BOSS_HEIGHT)
    
    # 2. Upper Key: Outer 0.95 x 2.85mm, Inner 0.60 x 2.40mm (Z: 2.47 to 3.32mm)
    outer_key = box(-0.95/2, -2.85/2, 0.95/2, 2.85/2)
    if is_hollow:
        poly_key = outer_key.difference(inner_hole)
    else:
        poly_key = outer_key
    m_key = extrude_shapely_geom(poly_key, height=0.85)
    m_key.apply_translation([0, 0, SLIT_BOSS_HEIGHT])
    
    # Concatenate and merge into a single watertight solid
    m_full = trimesh.util.concatenate([m_body, m_key])
    # Merge coplanar interface vertices
    m_full = trimesh.Trimesh(vertices=m_full.vertices, faces=m_full.faces, process=True)
    return m_full

insert = build_fixed_slit_insert_mesh()
print(f"Fixed Insert bounds: {insert.bounds}")
print(f"Is watertight: {insert.is_watertight}")
print(f"Volume: {insert.volume:.2f} mm^3")
print(f"Euler number: {insert.euler_number}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=160)

# 1. 3D Isometric View
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
col = Poly3DCollection(insert.vertices[insert.faces], alpha=0.9, edgecolor='#222222', linewidths=0.3)
col.set_facecolor('#00bcd4')
ax1.add_collection3d(col)
ax1.set_xlim(-3, 3)
ax1.set_ylim(-4, 4)
ax1.set_zlim(0, 4)
ax1.view_init(elev=30, azim=45)
ax1.set_title('Fixed 1-Piece Monolithic Slit Insert\n(Zero Gap, Solid Shoulder)', fontsize=11, fontweight='bold')
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)')

# 2. X-Z Cross Section
ax2 = fig.add_subplot(1, 2, 2)
# Draw single contiguous cross section
# Body wall: X in [-1.75, -0.30] and [0.30, 1.75], Z in [0, 2.47]
# Key wall: X in [-0.475, -0.30] and [0.30, 0.475], Z in [2.47, 3.32]
# Continuous hole in center: X in [-0.30, 0.30]
ax2.fill([-1.75, -1.75, -0.475, -0.475, -0.30, -0.30, -1.75],
         [0, 2.47, 2.47, 3.32, 3.32, 0, 0], color='#00bcd4', alpha=0.6, edgecolor='black', linewidth=1.5, label='Solid Left Wall')
ax2.fill([1.75, 1.75, 0.475, 0.475, 0.30, 0.30, 1.75],
         [0, 2.47, 2.47, 3.32, 3.32, 0, 0], color='#00bcd4', alpha=0.6, edgecolor='black', linewidth=1.5, label='Solid Right Wall')

# Draw dimension arrows and shoulder callout
ax2.annotate('Shoulder Seat (1.275mm wide)\nSits flush against main plate', xy=(-1.1, 2.47), xytext=(-2.3, 3.1),
             arrowprops=dict(arrowstyle='->', color='purple', lw=1.5), fontweight='bold', color='purple', fontsize=9.5)
ax2.annotate('0.95mm Indexing Key\n(Plugs into 1.1x3.0mm slit)', xy=(0.475, 2.9), xytext=(1.0, 3.2),
             arrowprops=dict(arrowstyle='->', color='green', lw=1.5), fontweight='bold', color='green', fontsize=9.5)

ax2.set_xlim(-2.5, 2.5)
ax2.set_ylim(-0.5, 4.0)
ax2.set_aspect('equal')
ax2.grid(True)
ax2.set_title('X-Z Cross Section: Monolithic Stepped Wall (Watertight 1-Piece)', fontsize=11, fontweight='bold')
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Z (mm)')
ax2.legend(loc='lower left', fontsize=8.5)

plt.tight_layout()
plt.savefig('fixed_slit_insert_preview.png', dpi=160)
print("Saved fixed_slit_insert_preview.png")
