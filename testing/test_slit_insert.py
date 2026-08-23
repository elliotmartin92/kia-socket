"""
Test separate slit insert part with indexing registration key.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box, Polygon
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import extrude_shapely_geom

def create_slit_insert_mesh():
    """Builds a single separate 3D-printable backside slit wall insert with indexing key.
    - Flat print bed face at Z = 0
    - Wall body: 3.50mm x 5.40mm outer, 1.10mm x 3.00mm inner, height = 2.47mm (Z: 0 to 2.47mm)
    - Indexing registration key: 0.95mm x 2.85mm outer, 0.65mm x 2.55mm inner, height = 0.85mm (Z: 2.47 to 3.32mm)
    - Mating shoulder at Z = 2.47mm sits flush against main plate bottom.
    """
    # 1. Main Wall Body (Z: 0.0 to 2.47mm)
    outer_box = box(-3.50/2, -5.40/2, 3.50/2, 5.40/2)
    inner_box = box(-1.10/2, -3.00/2, 1.10/2, 3.00/2)
    body_poly = outer_box.difference(inner_box)
    m_body = extrude_shapely_geom(body_poly, height=2.47)
    
    # 2. Indexing Registration Key (Z: 2.47 to 3.32mm)
    key_outer = box(-0.95/2, -2.85/2, 0.95/2, 2.85/2)
    key_inner = box(-0.65/2, -2.55/2, 0.65/2, 2.55/2)
    key_poly = key_outer.difference(key_inner)
    m_key = extrude_shapely_geom(key_poly, height=0.85)
    m_key.apply_translation([0, 0, 2.47])
    
    m_insert = trimesh.util.concatenate([m_body, m_key])
    m_insert = trimesh.Trimesh(vertices=m_insert.vertices, faces=m_insert.faces, process=True)
    return m_insert

insert = create_slit_insert_mesh()
print(f"Insert bounds: {insert.bounds}")
print(f"Is watertight: {insert.is_watertight}")
print(f"Volume: {insert.volume:.2f} mm^3")

# Generate preview plot of the insert
fig = plt.figure(figsize=(12, 6), dpi=160)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
col1 = Poly3DCollection(insert.vertices[insert.faces], alpha=0.9, edgecolor='#222222', linewidths=0.3)
col1.set_facecolor('#e91e63')
ax1.add_collection3d(col1)
ax1.set_xlim(-3, 3)
ax1.set_ylim(-4, 4)
ax1.set_zlim(0, 4)
ax1.view_init(elev=25, azim=45)
ax1.set_title('Separate Slit Insert (Upright with Indexing Key)', fontsize=11, fontweight='bold')
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.set_zlabel('Z (mm)')

# Print orientation: Print upside down on flat collar face (Z=0 on bed) or upright
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
insert_pair = insert.copy()
insert_pair.apply_translation([-4, 0, 0])
insert_2 = insert.copy()
insert_2.apply_translation([4, 0, 0])
m_pair = trimesh.util.concatenate([insert_pair, insert_2])

col2 = Poly3DCollection(m_pair.vertices[m_pair.faces], alpha=0.9, edgecolor='#222222', linewidths=0.3)
col2.set_facecolor('#00bcd4')
ax2.add_collection3d(col2)
ax2.set_xlim(-8, 8)
ax2.set_ylim(-5, 5)
ax2.set_zlim(0, 4)
ax2.view_init(elev=30, azim=-60)
ax2.set_title('Pair of Inserts for 3D Print Build Plate', fontsize=11, fontweight='bold')
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')

plt.tight_layout()
plt.savefig('slit_insert_preview.png', dpi=160)
print("Saved slit_insert_preview.png")
