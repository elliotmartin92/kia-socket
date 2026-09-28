"""
testing/plot_lever_profiles_with_sticks.py
Plot the exact 2D profiles of the Cam and Plunger in printable orientation (Y-Z),
highlight overhangs, and propose candidate support stick pillars rising from the bed.
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

parts = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False, return_subparts=True)
cam = parts['cam']
plunger = parts['plunger']
hub = parts['hub']

# Get 2D polygons in Y-Z
# Cam vertices at X_min
v_c = cam.vertices[np.isclose(cam.vertices[:, 0], cam.vertices[:, 0].min(), atol=1e-3)]
c_cam = np.mean(v_c[:, 1:], axis=0)
angles = np.arctan2(v_c[:, 2] - c_cam[1], v_c[:, 1] - c_cam[0])
v_c_sorted = v_c[np.argsort(angles)]
poly_cam_yz = Polygon(v_c_sorted[:, 1:])

# Plunger vertices at X_min
v_p = plunger.vertices[np.isclose(plunger.vertices[:, 0], plunger.vertices[:, 0].min(), atol=1e-3)]
c_p = np.mean(v_p[:, 1:], axis=0)
angles_p = np.arctan2(v_p[:, 2] - c_p[1], v_p[:, 1] - c_p[0])
v_p_sorted = v_p[np.argsort(angles_p)]
poly_plunger_yz = Polygon(v_p_sorted[:, 1:])

fig, ax = plt.subplots(figsize=(14, 12))

# Plot ground bed at Z = 0
ax.axhline(0, color='black', linewidth=2, label='Print Bed (Z = 0.00 mm)')

# Plot existing cradle baseplate
ax.fill_between([-2.60, 3.80], 0, 0.35, color='gray', alpha=0.4, label='v9.4 Base Cradle Brim (Z <= 0.35mm)')

# Plot Cam polygon
cam_x, cam_y = poly_cam_yz.exterior.xy
ax.fill(cam_x, cam_y, alpha=0.3, color='orange', label='Cam Tab Profile')
ax.plot(cam_x, cam_y, color='darkorange', linewidth=2)

# Plot Plunger polygon
p_x, p_y = poly_plunger_yz.exterior.xy
ax.fill(p_x, p_y, alpha=0.3, color='blue', label='Plunger Arm Profile')
ax.plot(p_x, p_y, color='darkblue', linewidth=2)

# Hub circle
circle = plt.Circle((1.05, 2.10), 2.10, color='gray', alpha=0.2, label='Hub Barrel (Ø4.20mm)')
ax.add_patch(circle)

# Label key overhang features
# 1. Cam tip / knee overhang:
# Underside runs from (4.32, 5.92) to (6.81, 9.50)
ax.plot([4.32, 6.81], [5.92, 9.50], color='red', linewidth=4, label='Steep Overhangs (>45°)')
ax.annotate('Cam Ramp Knee Overhang\n(Z = 5.92 to 9.50 mm)\nCantilevered in mid-air',
            xy=(5.5, 7.7), xytext=(7.5, 6.0),
            arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8),
            fontweight='bold', color='red')

# 2. Plunger tip nose:
# Curves down to Z = 18.54 mm at Y = -6.76 mm
ax.plot([-6.76, -6.81], [18.54, 18.93], color='red', linewidth=4)
ax.annotate('Plunger Tip Nose Hook\n(Z = 18.54 mm, Y = -6.76 mm)\nDownward pointing tip',
            xy=(-6.76, 18.54), xytext=(-9.5, 17.0),
            arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8),
            fontweight='bold', color='red')

# 3. Plunger mid-arm underside (Y in [-4.0, -1.0], Z in [2.0, 8.0])
ax.annotate('Plunger Arm Mid-span\n(Z ~ 8.0 to 12.0 mm)\nSlender arm sway/deflection',
            xy=(-3.8, 10.0), xytext=(-8.0, 10.5),
            arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8),
            fontweight='bold', color='blue')

# Propose Support Stick 1: Cam Tab Support Post
# Centered at Y = 5.80 mm, rising from Z = 0 to Z = 8.00 mm (under the cam ramp)
stick1_y = 5.80
stick1_top_z = 7.70  # Underside of cam at Y=5.80 is ~ 7.85 mm -> 0.15mm gap!
ax.fill_between([stick1_y - 0.75, stick1_y + 0.75], 0, stick1_top_z, color='green', alpha=0.5, label='Candidate Support Sticks')
ax.plot([stick1_y - 0.75, stick1_y + 0.75, stick1_y + 0.75, stick1_y - 0.75, stick1_y - 0.75],
        [0, 0, stick1_top_z, stick1_top_z, 0], color='darkgreen', linewidth=2)
ax.annotate(f'Stick #1: Cam Support Pillar\n(Y = {stick1_y} mm, Top Z = {stick1_top_z} mm)\n0.15mm release gap',
            xy=(stick1_y, stick1_top_z), xytext=(7.0, 11.0),
            arrowprops=dict(facecolor='darkgreen', shrink=0.05, width=2, headwidth=8),
            fontweight='bold', color='darkgreen')

# Propose Support Stick 2: Plunger Tip / Mid-span Support Post
# Under the plunger arm:
# Option A: Under the tip hook at Y = -6.50 mm, rising to Z = 18.35 mm (0.15mm gap below 18.54mm)
stick2_y = -6.50
stick2_top_z = 18.35
ax.fill_between([stick2_y - 0.75, stick2_y + 0.75], 0, stick2_top_z, color='green', alpha=0.5)
ax.plot([stick2_y - 0.75, stick2_y + 0.75, stick2_y + 0.75, stick2_y - 0.75, stick2_y - 0.75],
        [0, 0, stick2_top_z, stick2_top_z, 0], color='darkgreen', linewidth=2)
ax.annotate(f'Stick #2: Plunger Tip Pillar\n(Y = {stick2_y} mm, Top Z = {stick2_top_z} mm)\n0.15mm release gap below tip',
            xy=(stick2_y, stick2_top_z), xytext=(-9.5, 14.0),
            arrowprops=dict(facecolor='darkgreen', shrink=0.05, width=2, headwidth=8),
            fontweight='bold', color='darkgreen')

# Propose Support Stick 3: Plunger Mid-span brace (optional stabilizer at Y = -3.80 mm, rising to Z = 9.80 mm)
stick3_y = -3.80
stick3_top_z = 9.80
ax.fill_between([stick3_y - 0.60, stick3_y + 0.60], 0, stick3_top_z, color='limegreen', alpha=0.3)
ax.plot([stick3_y - 0.60, stick3_y + 0.60, stick3_y + 0.60, stick3_y - 0.60, stick3_y - 0.60],
        [0, 0, stick3_top_z, stick3_top_z, 0], color='forestgreen', linewidth=1.5, linestyle='--')
ax.annotate(f'Stick #3 (Stabilizer): Plunger Mid-Span Pillar\n(Y = {stick3_y} mm, Top Z = {stick3_top_z} mm)\nPrevents tall arm wobble',
            xy=(stick3_y, stick3_top_z), xytext=(-8.0, 8.0),
            arrowprops=dict(facecolor='forestgreen', shrink=0.05, width=1.5, headwidth=6),
            fontweight='bold', color='forestgreen')

ax.set_xlabel('Y (mm) [Print Bed Axis]')
ax.set_ylabel('Z (mm) [Height Above Bed]')
ax.set_title('Shaft Rocker Overhang Analysis & Proposed Sacrificial Support Sticks', fontsize=14, fontweight='bold')
ax.grid(True, linestyle=':')
ax.set_xlim(-12, 12)
ax.set_ylim(-1, 22)
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig('testing/shaft_support_sticks_diagram.png', dpi=150)
print("Saved testing/shaft_support_sticks_diagram.png")
