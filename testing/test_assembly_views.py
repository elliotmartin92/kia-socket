"""
testing/test_assembly_views.py
Tests camera angle and moderate elevation offsets to ensure parts are clearly inside the main body.
"""
import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import to_rgb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, build_slit_insert_mesh
from build_shaft import build_shaft_rocker_mesh
from testing.generate_print_assembly_guide import build_brass_contact_mesh, shade_faces, add_mesh_collection

part_mesh, _ = build_exact_3d_model()
shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)
brass_hot = build_brass_contact_mesh(is_hot=True)
brass_neutral = build_brass_contact_mesh(is_hot=False)

fig, axes = plt.subplots(1, 2, figsize=(20, 10), subplot_kw={'projection': '3d'}, facecolor='#090d16')

# Panel 1: Step 1 (Shaft hovering directly over towers inside body)
ax1 = axes[0]
ax1.set_facecolor('#111827')
ax1.set_title("Step 1: Shaft directly over towers (elev=55, azim=-65)", color='white', fontsize=14)
add_mesh_collection(ax1, part_mesh, base_color='#0284c7', alpha=0.75, azdeg=315, altdeg=45)

# Moderate elevation: +4.0mm
s_elev = shaft_assembled.copy()
s_elev.apply_translation([0, 0, 4.0])
add_mesh_collection(ax1, s_elev, base_color='#f59e0b', alpha=0.98, azdeg=315, altdeg=45)

ax1.quiver(4.65, 9.28, 17.5, 0, 0, -3.5, color='#ef4444', lw=4.0, arrow_length_ratio=0.35)
ax1.quiver(13.85, 9.28, 17.5, 0, 0, -3.5, color='#ef4444', lw=4.0, arrow_length_ratio=0.35)

ax1.set_xlim(-22, 22)
ax1.set_ylim(-22, 22)
ax1.set_zlim(-5, 22)
ax1.view_init(elev=55, azim=-65)
ax1.axis('off')

# Panel 2: Step 2 (Brass directly over brackets inside body)
ax2 = axes[1]
ax2.set_facecolor('#111827')
ax2.set_title("Step 2: Brass directly over brackets (elev=55, azim=-65)", color='white', fontsize=14)
add_mesh_collection(ax2, part_mesh, base_color='#0284c7', alpha=0.75, azdeg=315, altdeg=45)
add_mesh_collection(ax2, shaft_assembled, base_color='#f59e0b', alpha=0.98, azdeg=315, altdeg=45)

b_h = brass_hot.copy()
b_h.apply_translation([0, 0, 4.5])
add_mesh_collection(ax2, b_h, base_color='#eab308', alpha=0.98, azdeg=315, altdeg=45)

b_n = brass_neutral.copy()
b_n.apply_translation([0, 0, 4.5])
add_mesh_collection(ax2, b_n, base_color='#eab308', alpha=0.98, azdeg=315, altdeg=45)

ax2.quiver(6.28, 1.0, 18.0, 0, 0, -4.0, color='#facc15', lw=4.0, arrow_length_ratio=0.35)
ax2.quiver(-6.28, 1.0, 18.0, 0, 0, -4.0, color='#facc15', lw=4.0, arrow_length_ratio=0.35)

ax2.set_xlim(-22, 22)
ax2.set_ylim(-22, 22)
ax2.set_zlim(-5, 22)
ax2.view_init(elev=55, azim=-65)
ax2.axis('off')

plt.tight_layout()
plt.savefig('testing/test_moderate_elevation.png', dpi=150)
print('Saved test_moderate_elevation.png')
