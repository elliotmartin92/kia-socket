"""
testing/inspect_cam_junction.py
Inspect the junction between the input cam tab and the cylindrical shaft barrel.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE, PIN_DIAMETER, HUB_DIAMETER

shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)

fig = plt.figure(figsize=(16, 8), dpi=180)

# Panel 1: Y-Z side profile of input cam vs axle circle
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_title("Input Cam 2D Profile relative to Shaft Center", fontsize=11, fontweight='bold')

r_hub = HUB_DIAMETER / 2.0
phi = np.linspace(0, 2*np.pi, 100)
ax1.plot(Y_AXLE + r_hub*np.cos(phi), Z_AXLE + r_hub*np.sin(phi), 'b-', lw=2, label=f'Hub Cylinder (Ø{HUB_DIAMETER:.2f}mm)')
ax1.plot(Y_AXLE, Z_AXLE, 'ro', markersize=6, label=f'Pivot Axis ({Y_AXLE:.2f}, {Z_AXLE:.2f})')

# Draw cam profile polygon
# Let's inspect the exact points
y_cam_tip = Y_AXLE - 4.50
z_cam_tip = Z_AXLE - 5.80
cam_pts = np.array([
    [Y_AXLE + 1.50, Z_AXLE + 1.50],
    [y_cam_tip, z_cam_tip + 2.40],
    [y_cam_tip, z_cam_tip],
    [y_cam_tip + 3.00, z_cam_tip],
    [Y_AXLE + 0.20, Z_AXLE - 2.80]
])
ax1.fill(cam_pts[:, 0], cam_pts[:, 1], color='#4caf50', alpha=0.5, label='Cam Polygon on main')
ax1.plot(cam_pts[:, 0], cam_pts[:, 1], 'g-', lw=1.5)

ax1.set_xlim(Y_AXLE - 6, Y_AXLE + 4)
ax1.set_ylim(Z_AXLE - 8, Z_AXLE + 4)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(loc='lower left')
ax1.set_xlabel('Y (mm)')
ax1.set_ylabel('Z (mm)')

# Panel 2: 3D Closeup of Cam Junction
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.set_title("3D Closeup of Shaft & Cam Tab", fontsize=11, fontweight='bold')

v = shaft_assembled.vertices
f = shaft_assembled.faces
col = Poly3DCollection(v[f], alpha=0.9, facecolor='#ff9800', edgecolor='#b71c1c', linewidth=0.15)
ax2.add_collection3d(col)

ax2.set_xlim(4, 11)
ax2.set_ylim(4, 13)
ax2.set_zlim(3, 15)
ax2.view_init(elev=20, azim=135)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')

plt.tight_layout()
out_png = 'testing/cam_junction_inspect.png'
plt.savefig(out_png, dpi=200)
print(f"Saved {out_png}")
