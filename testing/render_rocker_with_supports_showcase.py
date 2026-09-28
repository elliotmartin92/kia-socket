"""
testing/render_rocker_with_supports_showcase.py
Generates a multi-panel, high-resolution rendering showing the 3D model of the thinned rocker
with its built-in sacrificial breakaway base cradle (dual axle saddles + bed brim).
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh, build_shaft_support_cradle_mesh

# 1. Load meshes in printable orientation
rocker_mesh = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
cradle_mesh = build_shaft_support_cradle_mesh()

# Set up figure: 3 panels
fig = plt.figure(figsize=(28, 10), dpi=200)

# ==============================================================================
# PANEL 1: 3D ISOMETRIC SHOWCASE (Matching Slicer View)
# ==============================================================================
ax1 = fig.add_subplot(1, 3, 1, projection='3d')

# Shaded Rocker (Warm Amber / Gold)
v_r = rocker_mesh.vertices
f_r = rocker_mesh.faces
normals_r = rocker_mesh.face_normals
light_dir = np.array([0.4, 0.4, 0.8])
light_dir = light_dir / np.linalg.norm(light_dir)
intensities_r = 0.4 + 0.6 * np.clip(np.dot(normals_r, light_dir), 0.1, 1.0)
colors_r = np.array([[0.95 * i, 0.55 * i, 0.15 * i, 0.88] for i in intensities_r])

mesh_r_poly = Poly3DCollection(v_r[f_r], facecolors=colors_r, edgecolors='#b25900', linewidths=0.15)
ax1.add_collection3d(mesh_r_poly)

# Shaded Cradle (Emerald / Forest Green)
v_c = cradle_mesh.vertices
f_c = cradle_mesh.faces
normals_c = cradle_mesh.face_normals
intensities_c = 0.4 + 0.6 * np.clip(np.dot(normals_c, light_dir), 0.1, 1.0)
colors_c = np.array([[0.15 * i, 0.75 * i, 0.35 * i, 0.90] for i in intensities_c])

mesh_c_poly = Poly3DCollection(v_c[f_c], facecolors=colors_c, edgecolors='#0e4d1f', linewidths=0.25)
ax1.add_collection3d(mesh_c_poly)

# Print bed grid visualization
bed_xs = np.linspace(-10, 10, 9)
bed_ys = np.linspace(-10, 10, 9)
for bx in bed_xs:
    ax1.plot([bx, bx], [-10, 10], [0, 0], color='#bdbdbd', linestyle=':', linewidth=0.6)
for by in bed_ys:
    ax1.plot([-10, 10], [by, by], [0, 0], color='#bdbdbd', linestyle=':', linewidth=0.6)

def add_3d_callout(ax, pt_model, pt_text, text, color='#004d40', bgcolor='#e0f2f1', fontsize=8.0):
    ax.plot([pt_model[0], pt_text[0]], [pt_model[1], pt_text[1]], [pt_model[2], pt_text[2]],
            color=color, linestyle='-', linewidth=1.2, alpha=0.9)
    ax.scatter([pt_model[0]], [pt_model[1]], [pt_model[2]], color=color, s=20, depthshade=False)
    ax.text(pt_text[0], pt_text[1], pt_text[2], text, color=color, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', bbox=dict(boxstyle='round,pad=0.25', fc=bgcolor, ec=color, alpha=0.95, lw=1.2))

# 3D Annotations
add_3d_callout(ax1, [-4.75, 1.05, 0.58], [-9.5, 1.05, 4.0],
               "Left Pin Saddle\n(0.12mm Gap under Ø2.8mm Pin)", color='#006064', bgcolor='#e0f7fa')
add_3d_callout(ax1, [4.75, 1.05, 0.58], [9.5, 1.05, 4.0],
               "Right Pin Saddle\n(0.12mm Gap under Ø2.8mm Pin)", color='#006064', bgcolor='#e0f7fa')
add_3d_callout(ax1, [0.0, -3.00, 0.35], [0.0, -8.5, 2.5],
               "Rear Pry Notch & Brim\n(One-piece snap removal)", color='#bf360c', bgcolor='#fbe9e7')
add_3d_callout(ax1, [-2.2, 5.5, 10.0], [-7.5, 8.5, 14.0],
               "Thinned Cam Tab (1.90mm)\n+0.60mm to Bracket 4", color='#1b5e20', bgcolor='#e8f5e9')
add_3d_callout(ax1, [1.5, -5.5, 15.0], [7.0, -7.0, 16.0],
               "Thinned Plunger (3.60mm)\n+0.48mm to Bracket 4", color='#e65100', bgcolor='#fff3e0')

ax1.set_xlim(-10, 10)
ax1.set_ylim(-10, 10)
ax1.set_zlim(0, 22)
ax1.view_init(elev=24, azim=-55)
ax1.set_xlabel('X (mm)', fontsize=9)
ax1.set_ylabel('Y (mm)', fontsize=9)
ax1.set_zlabel('Z (mm)', fontsize=9)
ax1.set_title('1. 3D Isometric View (As Sliced on Build Plate)\nOrange: Thinned Rocker Body | Green: Built-In Breakaway Base Cradle',
              fontsize=12, fontweight='bold', pad=10)

# ==============================================================================
# PANEL 2: SIDE VIEW (Y-Z PLANE) WITH RELEASE MICRO-GAPS
# ==============================================================================
ax2 = fig.add_subplot(1, 3, 2)

# Ground line
ax2.axhline(0, color='black', linewidth=2.5, label='Print Bed (Z = 0.00mm)')

# Plot wireframes / silhouettes of rocker
for f in rocker_mesh.faces[::2]:
    v = rocker_mesh.vertices[f]
    ax2.plot(v[[0,1,2,0], 1], v[[0,1,2,0], 2], color='#e65100', alpha=0.35, linewidth=0.5)

# Plot cradle wireframes
for f in cradle_mesh.faces[::2]:
    v = cradle_mesh.vertices[f]
    ax2.plot(v[[0,1,2,0], 1], v[[0,1,2,0], 2], color='#2e7d32', alpha=0.75, linewidth=0.7)

# Side view callouts
ax2.annotate('Axle Pin Saddles\n(Z = 0.58mm)\nRelease Gap: 0.12mm under Ø2.8mm Pin',
             xy=(1.05, 0.58), xytext=(3.5, 4.5),
             arrowprops=dict(facecolor='#006064', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#006064',
             bbox=dict(boxstyle='round,pad=0.25', fc='#e0f7fa', ec='#006064'))

ax2.annotate('Central Hub Sits on Bed\n(Z = 0.00mm Direct Contact Window)',
             xy=(1.05, 0.00), xytext=(-2.5, -2.5),
             arrowprops=dict(facecolor='#e65100', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#e65100',
             bbox=dict(boxstyle='round,pad=0.25', fc='#fff3e0', ec='#e65100'))

ax2.annotate('Rear Pry Tab\n(Y = -3.0mm, Z = 0.35mm)\nLeverage point for clean peel',
             xy=(-3.00, 0.35), xytext=(-8.5, 2.0),
             arrowprops=dict(facecolor='#bf360c', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#bf360c',
             bbox=dict(boxstyle='round,pad=0.25', fc='#fbe9e7', ec='#bf360c'))

ax2.annotate('Overhang Angles (~55°-70°)\nSelf-Supporting without Sticks',
             xy=(5.60, 8.0), xytext=(4.0, 12.0),
             arrowprops=dict(facecolor='#1b5e20', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#1b5e20',
             bbox=dict(boxstyle='round,pad=0.25', fc='#e8f5e9', ec='#1b5e20'))

ax2.set_xlim(-10, 10)
ax2.set_ylim(-3, 22)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_title('2. Side Elevation View (Y vs Z)\nShowing Dual Pin Saddles & 0.12mm Release Gap',
              fontsize=12, fontweight='bold', pad=10)
ax2.set_xlabel('Y (mm) [Print Bed Longitudinal Axis]', fontsize=9)
ax2.set_ylabel('Z (mm) [Elevation Above Build Plate]', fontsize=9)

# ==============================================================================
# PANEL 3: FRONT VIEW (X-Z PLANE) WITH THINNED ROCKER & CLEARANCE
# ==============================================================================
ax3 = fig.add_subplot(1, 3, 3)

ax3.axhline(0, color='black', linewidth=2.5, label='Print Bed (Z = 0.00mm)')

for f in rocker_mesh.faces[::2]:
    v = rocker_mesh.vertices[f]
    ax3.plot(v[[0,1,2,0], 0], v[[0,1,2,0], 2], color='#e65100', alpha=0.35, linewidth=0.5)

for f in cradle_mesh.faces[::2]:
    v = cradle_mesh.vertices[f]
    ax3.plot(v[[0,1,2,0], 0], v[[0,1,2,0], 2], color='#2e7d32', alpha=0.75, linewidth=0.7)

ax3.annotate('Left Cantilever Pin (Ø2.8mm)\nSits on Left Saddle',
             xy=(-4.75, 0.70), xytext=(-9.5, 4.0),
             arrowprops=dict(facecolor='#006064', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#006064',
             bbox=dict(boxstyle='round,pad=0.25', fc='#e0f7fa', ec='#006064'))

ax3.annotate('Right Cantilever Pin (Ø2.8mm)\nSits on Right Saddle',
             xy=(4.75, 0.70), xytext=(5.5, 4.0),
             arrowprops=dict(facecolor='#006064', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#006064',
             bbox=dict(boxstyle='round,pad=0.25', fc='#e0f7fa', ec='#006064'))

ax3.annotate('Thinned Cam Tab (Width 1.90mm)\nX: 5.50 -> 7.40mm\n+0.60mm Clearance to Bracket 4',
             xy=(-2.40, 7.61), xytext=(-9.5, 10.0),
             arrowprops=dict(facecolor='#1b5e20', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#1b5e20',
             bbox=dict(boxstyle='round,pad=0.25', fc='#e8f5e9', ec='#1b5e20'))

ax3.annotate('Thinned Plunger (Width 3.60mm)\nX: 8.48 -> 12.08mm\n+0.48mm Clearance to Bracket 4',
             xy=(1.03, 14.0), xytext=(3.5, 15.0),
             arrowprops=dict(facecolor='#e65100', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#e65100',
             bbox=dict(boxstyle='round,pad=0.25', fc='#fff3e0', ec='#e65100'))

ax3.annotate('Broad 12.80mm Base Brim\nPrevents Bed Detachment',
             xy=(0.0, 0.35), xytext=(-6.0, -2.5),
             arrowprops=dict(facecolor='#2e7d32', shrink=0.06, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#2e7d32',
             bbox=dict(boxstyle='round,pad=0.25', fc='#e8f5e9', ec='#2e7d32'))

ax3.set_xlim(-10, 10)
ax3.set_ylim(-3, 22)
ax3.set_aspect('equal')
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.set_title('3. Front Elevation View (X vs Z)\nShowing Thinned Cam/Plunger & Dual Pin Support Saddles',
              fontsize=12, fontweight='bold', pad=10)
ax3.set_xlabel('X (mm) [Axle Transverse Axis]', fontsize=9)
ax3.set_ylabel('Z (mm) [Elevation Above Build Plate]', fontsize=9)

plt.tight_layout()
output_path = 'testing/rocker_with_supports_showcase.png'
plt.savefig(output_path, dpi=200)
print(f"Saved {output_path} successfully!")
