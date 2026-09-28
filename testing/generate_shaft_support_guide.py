"""
testing/generate_shaft_support_guide.py
Generate a clear, high-resolution annotated visual guide showing the built-in breakaway
support system for the shaft rocker.
"""

import os, sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh, build_shaft_support_cradle_mesh

shaft_rocker = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
support_frame = build_shaft_support_cradle_mesh()

fig = plt.figure(figsize=(22, 10.5), dpi=200)

# Panel 1: 3D Isometric Overview
ax1 = fig.add_subplot(1, 3, 1, projection='3d')
v_r = shaft_rocker.vertices
f_r = shaft_rocker.faces
col_r = Poly3DCollection(v_r[f_r], alpha=0.92, edgecolor='#b71c1c', linewidths=0.15)
col_r.set_facecolor('#ff9800')
ax1.add_collection3d(col_r)

v_s = support_frame.vertices
f_s = support_frame.faces
col_s = Poly3DCollection(v_s[f_s], alpha=0.88, edgecolor='#004d40', linewidths=0.25)
col_s.set_facecolor('#00b4d8')
ax1.add_collection3d(col_s)

ax1.set_xlim(-8, 8)
ax1.set_ylim(-8, 8)
ax1.set_zlim(0, 21)
ax1.view_init(elev=25, azim=225)
ax1.set_title("1. 3D Print Layout with Built-In Supports\n(Print with Slicer Supports DISABLED)", fontsize=12, fontweight='bold', pad=10)
ax1.set_xlabel("X (mm)")
ax1.set_ylabel("Y (mm)")
ax1.set_zlabel("Z (mm)")

# Add 3D text annotations
ax1.text(0, -6.5, 18.0, "Plunger Arm\n(Self-Supporting)", color='#e65100', fontsize=8.5, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100'))
ax1.text(-2.5, 6.0, 10.0, "Cam Tab\n(Self-Supporting)", color='#e65100', fontsize=8.5, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100'))
ax1.text(-5.0, 1.0, 2.5, "Left Pin Saddle", color='#006064', fontsize=8, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#006064'))
ax1.text(5.0, 1.0, 2.5, "Right Pin Saddle", color='#006064', fontsize=8, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#006064'))
ax1.text(0, -3.8, 0.5, "Pry Tab (Snap-off)", color='#006064', fontsize=8, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#006064'))

# Panel 2: Front Closeup (X-Z) - Pin Saddles & 0.12mm Release Gap
ax2 = fig.add_subplot(1, 3, 2)
# 2D cross section along X-Z at Y = 1.05mm (pin centerline)
# Draw Left Pin
circle_l = plt.Circle((-4.75, 2.10), 1.40, color='#ff9800', ec='#b71c1c', lw=1.8, label='Left Axle Pin (Ø2.80mm)')
ax2.add_patch(circle_l)
# Draw Right Pin
circle_r = plt.Circle((4.75, 2.10), 1.40, color='#ff9800', ec='#b71c1c', lw=1.8, label='Right Axle Pin (Ø2.80mm)')
ax2.add_patch(circle_r)
# Draw Hub
rect_hub = plt.Rectangle((-3.75, 0.0), 7.50, 4.20, color='#ffa726', ec='#e65100', lw=1.5, alpha=0.5, label='Hub Barrel (Ø4.20mm)')
ax2.add_patch(rect_hub)

# Draw Support Saddles & Bed Frame
# Left Saddle
rect_sad_l = plt.Rectangle((-5.60, 0.0), 1.70, 0.58, color='#00b4d8', ec='#006064', lw=1.8, label='Support Saddles (Z=0.58mm)')
ax2.add_patch(rect_sad_l)
# Right Saddle
rect_sad_r = plt.Rectangle((3.90, 0.0), 1.70, 0.58, color='#00b4d8', ec='#006064', lw=1.8)
ax2.add_patch(rect_sad_r)
# Bed Frame extension
rect_base_l = plt.Rectangle((-6.40, 0.0), 0.80, 0.35, color='#48cae4', ec='#006064', lw=1.2)
ax2.add_patch(rect_base_l)
rect_base_r = plt.Rectangle((5.60, 0.0), 0.80, 0.35, color='#48cae4', ec='#006064', lw=1.2)
ax2.add_patch(rect_base_r)

# Print bed line
ax2.axhline(0.0, color='#37474f', lw=3.0, label='Print Bed (Z = 0.00mm)')

# Dimension callouts: 0.12mm release gap
ax2.annotate('0.12mm Vertical Release Micro-Gap\n(Z=0.58mm saddle to Z=0.70mm pin)\nZero Sag + Clean Breakaway!',
             xy=(-4.75, 0.64), xytext=(-6.2, 2.6),
             arrowprops=dict(facecolor='#006064', edgecolor='#004d40', width=1.8, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#006064', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#006064'))

ax2.annotate('0.12mm Gap',
             xy=(4.75, 0.64), xytext=(3.5, 2.6),
             arrowprops=dict(facecolor='#006064', edgecolor='#004d40', width=1.8, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#006064', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#006064'))

ax2.annotate('Hub Sits Directly on Print Bed\n(Z = 0.00mm, Zero Support Marks!)',
             xy=(0.0, 0.0), xytext=(-2.5, -0.65),
             arrowprops=dict(arrowstyle='->', color='#e65100', lw=1.5),
             fontsize=8.5, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100'))

ax2.set_xlim(-7.0, 7.0)
ax2.set_ylim(-1.0, 4.8)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_title("2. Axle Pin Support Saddles & Release Micro-Gap\n(Cross-Section at Y = 1.05mm)", fontsize=12, fontweight='bold', pad=10)
ax2.set_xlabel("X (mm)")
ax2.set_ylabel("Z (mm)")
ax2.legend(loc='upper right', fontsize=7.5)

# Panel 3: Bottom-Up View & Breakaway Guide
ax3 = fig.add_subplot(1, 3, 3)
# Frame outer box
from shapely.geometry import box
outer_box = box(-6.40, -2.60, 6.40, 3.80)
pry_tab = box(-2.00, -3.30, 2.00, -2.60)
inner_window = box(-3.85, -0.80, 3.85, 2.80)
frame_poly = outer_box.union(pry_tab).difference(inner_window)

# Plot frame
fx, fy = frame_poly.exterior.xy
ax3.fill(fx, fy, color='#00b4d8', alpha=0.85, ec='#004d40', lw=1.8, label='Sacrificial Support Frame (52.8mm²)')
for interior in frame_poly.interiors:
    ix, iy = interior.xy
    ax3.plot(ix, iy, color='#004d40', lw=1.5)

# Plot hub footprint
ax3.fill([-3.75, 3.75, 3.75, -3.75], [0.65, 0.65, 1.45, 1.45], color='#ff9800', alpha=0.9, ec='#b71c1c', lw=1.5, label='Hub Bed Contact Patch')
# Plot Plunger arm projection
ax3.plot([-2.2, 2.2, 0.0, -2.2], [-1.0, -1.0, -6.8, -1.0], color='#e65100', lw=2.0, linestyle='--', label='Plunger Projection')
# Plot Cam tab projection
ax3.plot([-3.75, -1.05, -1.05, -3.75, -3.75], [1.5, 1.5, 6.8, 6.8, 1.5], color='#ffa000', lw=2.0, linestyle=':', label='Cam Projection')

# Callouts
ax3.annotate('Rear Pull/Pry Tab\n(Slide fingernail & pull)', xy=(0.0, -2.95), xytext=(-4.5, -4.2),
             arrowprops=dict(facecolor='#006064', edgecolor='#004d40', width=1.8, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#006064', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#006064'))

ax3.annotate('Central Open Window\n(Hub sits on bed with zero weld)', xy=(0.0, 1.05), xytext=(-3.0, 4.6),
             arrowprops=dict(facecolor='#e65100', edgecolor='#b71c1c', width=1.8, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100'))

ax3.annotate('Left Pin Saddle Foot', xy=(-4.75, 1.05), xytext=(-6.8, 2.5),
             arrowprops=dict(arrowstyle='->', color='#006064', lw=1.5),
             fontsize=8, fontweight='bold', color='#006064')

ax3.annotate('Right Pin Saddle Foot', xy=(4.75, 1.05), xytext=(4.2, 2.5),
             arrowprops=dict(arrowstyle='->', color='#006064', lw=1.5),
             fontsize=8, fontweight='bold', color='#006064')

ax3.set_xlim(-7.5, 7.5)
ax3.set_ylim(-5.0, 5.8)
ax3.set_aspect('equal')
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.set_title("3. Bottom View (Bed Adhesion Footprint & Pry Tab)\nOne-Piece Snap-Off Removal", fontsize=12, fontweight='bold', pad=10)
ax3.set_xlabel("X (mm)")
ax3.set_ylabel("Y (mm)")
ax3.legend(loc='lower right', fontsize=7.5)

plt.tight_layout()
plt.savefig('testing/shaft_support_guide.png', dpi=200)
print("Saved testing/shaft_support_guide.png successfully!")
