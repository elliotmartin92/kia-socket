"""
testing/render_moon_and_ribs_3d.py
Renders high-res 3D views of the half moon, bracket seating ribs, and floor ribs from various angles.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import build_part as bp

full_part, base_poly = bp.build_exact_3d_model()

# Crop around Brackets 3 & 4: X in [0, 12], Y in [-8, 8], Z in [0, 12]
crop_box = trimesh.creation.box([12.0, 16.0, 14.0])
crop_box.apply_translation([6.0, 0.0, 7.0])

cropped = full_part.intersection(crop_box, engine='manifold')
print(f"Cropped model: {len(cropped.faces)} faces")

# Plot 3D views
fig = plt.figure(figsize=(18, 9), dpi=180)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.plot_trisurf(cropped.vertices[:, 0], cropped.vertices[:, 1], cropped.vertices[:, 2],
                 triangles=cropped.faces, color='#64b5f6', alpha=0.85, edgecolor='none')
ax1.view_init(elev=35, azim=-60)
ax1.set_title("3D View 1 (Looking from South-East / +X, -Y)", fontsize=11, fontweight='bold')
ax1.set_xlabel("X (mm)")
ax1.set_ylabel("Y (mm)")
ax1.set_zlabel("Z (mm)")

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.plot_trisurf(cropped.vertices[:, 0], cropped.vertices[:, 1], cropped.vertices[:, 2],
                 triangles=cropped.faces, color='#64b5f6', alpha=0.85, edgecolor='none')
ax2.view_init(elev=50, azim=-120)
ax2.set_title("3D View 2 (Looking from South-West / -X, -Y)", fontsize=11, fontweight='bold')
ax2.set_xlabel("X (mm)")
ax2.set_ylabel("Y (mm)")
ax2.set_zlabel("Z (mm)")

plt.tight_layout()
plt.savefig('testing/moon_and_ribs_3d.png')
print("Saved testing/moon_and_ribs_3d.png")
