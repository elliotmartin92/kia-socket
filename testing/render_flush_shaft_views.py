"""
testing/render_flush_shaft_views.py
Render 4 high-resolution 3D views of the shaft with flush-top input cam.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from testing.test_flush_cam_full_shaft import build_shaft_rocker_mesh_flush

mesh = build_shaft_rocker_mesh_flush(in_assembly_coords=True)

fig = plt.figure(figsize=(16, 12), facecolor='#1e1e1e')
v = mesh.vertices
f = mesh.faces

# 1. Top View (showing continuous top plane)
ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#252526')
ax1.set_title("1. Top View: 100% Flush Top Plane", color='white', fontsize=12, weight='bold')
col1 = Poly3DCollection(v[f], alpha=0.95, facecolor='#00d2ff', edgecolor='#005577', linewidth=0.2)
ax1.add_collection3d(col1)
ax1.set_xlim(2, 16); ax1.set_ylim(2, 14); ax1.set_zlim(-7, 16)
ax1.view_init(elev=80, azim=-90)
ax1.tick_params(colors='white')
ax1.set_xlabel('X (mm)', color='white')
ax1.set_ylabel('Y (mm)', color='white')

# 2. Side Profile (showing top tangent alignment)
ax2 = fig.add_subplot(2, 2, 2, projection='3d', facecolor='#252526')
ax2.set_title("2. Side Profile: Tangent to Shaft Apex (Z=14.69mm)", color='white', fontsize=12, weight='bold')
col2 = Poly3DCollection(v[f], alpha=0.95, facecolor='#2ecc71', edgecolor='#155724', linewidth=0.2)
ax2.add_collection3d(col2)
ax2.set_xlim(2, 16); ax2.set_ylim(2, 14); ax2.set_zlim(-7, 16)
ax2.view_init(elev=0, azim=0)
ax2.tick_params(colors='white')
ax2.set_ylabel('Y (mm)', color='white')
ax2.set_zlabel('Z (mm)', color='white')

# 3. 3D Isometric View
ax3 = fig.add_subplot(2, 2, 3, projection='3d', facecolor='#252526')
ax3.set_title("3. 3D Isometric View (Front-Top)", color='white', fontsize=12, weight='bold')
col3 = Poly3DCollection(v[f], alpha=0.95, facecolor='#f39c12', edgecolor='#b9770e', linewidth=0.2)
ax3.add_collection3d(col3)
ax3.set_xlim(2, 16); ax3.set_ylim(2, 14); ax3.set_zlim(-7, 16)
ax3.view_init(elev=35, azim=-45)
ax3.tick_params(colors='white')
ax3.set_xlabel('X (mm)', color='white')
ax3.set_ylabel('Y (mm)', color='white')
ax3.set_zlabel('Z (mm)', color='white')

# 4. Underside View
ax4 = fig.add_subplot(2, 2, 4, projection='3d', facecolor='#252526')
ax4.set_title("4. Underside 3D View (Direct Hub Fusion)", color='white', fontsize=12, weight='bold')
col4 = Poly3DCollection(v[f], alpha=0.95, facecolor='#e74c3c', edgecolor='#78281f', linewidth=0.2)
ax4.add_collection3d(col4)
ax4.set_xlim(2, 16); ax4.set_ylim(2, 14); ax4.set_zlim(-7, 16)
ax4.view_init(elev=-40, azim=-60)
ax4.tick_params(colors='white')
ax4.set_xlabel('X (mm)', color='white')
ax4.set_ylabel('Y (mm)', color='white')
ax4.set_zlabel('Z (mm)', color='white')

plt.tight_layout()
out_png = "testing/flush_shaft_closeup.png"
plt.savefig(out_png, dpi=200)
print(f"Saved {out_png}")
