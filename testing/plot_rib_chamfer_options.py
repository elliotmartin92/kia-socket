"""
testing/plot_rib_chamfer_options.py
Visualizes candidate chamfered ramp designs connecting the ribs and half moon:
- Profile in (Y, Z) along the centerline X = 6.279mm
- Profile in (X, Z) across the channel
- Clearance to the brass insert resting on top of the rib (Z = 2.15mm)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box

import build_part as bp

z_floor = 1.00
z_rib = 2.15
h_rib = 1.15

# Seating Rib 4: Y in [-4.95, -4.35]
# Half Moon: Y in [-4.30, -3.00], Z in [1.00, 10.50]
# Rib 3: Y in [-1.65, -1.05]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), dpi=180)

# -------------------------------------------------------------
# Panel 1: Centerline Longitudinal Cross-Section (Y-Z Plane at X = 6.28mm)
# -------------------------------------------------------------
# Draw Baseplate Floor (Z = 0 to 1.0mm)
ax1.fill([-7.5, 2.0, 2.0, -7.5], [0, 0, 1.0, 1.0], color='#b0bec5', alpha=0.7, label='Baseplate Floor (Z=0 to 1.0mm)')

# Draw Rib 4 (Y in [-4.95, -4.35], Z in [1.0, 2.15])
ax1.fill([-4.95, -4.35, -4.35, -4.95], [1.0, 1.0, 2.15, 2.15], color='#ffb74d', alpha=0.9, label='Rib 4 (Z=1.0 to 2.15mm)')
ax1.plot([-4.95, -4.35, -4.35, -4.95, -4.95], [1.0, 1.0, 2.15, 2.15, 1.0], color='#e65100', lw=2)

# Draw Rib 3 (Y in [-1.65, -1.05], Z in [1.0, 2.15])
ax1.fill([-1.65, -1.05, -1.05, -1.65], [1.0, 1.0, 2.15, 2.15], color='#ffb74d', alpha=0.9, label='Rib 3 (Z=1.0 to 2.15mm)')
ax1.plot([-1.65, -1.05, -1.05, -1.65, -1.65], [1.0, 1.0, 2.15, 2.15, 1.0], color='#e65100', lw=2)

# Draw Half Moon (Y in [-4.30, -3.00], Z in [1.0, 10.50])
ax1.fill([-4.30, -3.00, -3.00, -3.25, -4.30], [1.0, 1.0, 8.5, 10.5, 10.5], color='#90caf9', alpha=0.7, label='Half Moon (Z=1.0 to 10.5mm)')
ax1.plot([-4.30, -4.30, -3.25, -3.00, -3.00, -4.30], [1.0, 10.5, 10.5, 8.5, 1.0, 1.0], color='#1565c0', lw=2.5)

# Proposed Chamfered Ramp Option A:
# Ramp 1: From bottom of Rib 4 (Y = -4.95) up to Rib 4 top (Y = -4.35, Z = 2.15),
# and from Rib 4 top into the Half Moon back wall (Y = -4.30, Z = 3.50mm)!
# Ramp 2: On the front face, from Half Moon front base (Y = -3.00, Z = 2.15) ramping down to floor or Rib 3!
ramp_pts_back = [(-5.50, 1.0), (-4.95, 1.0), (-4.35, 2.15), (-4.30, 3.50), (-4.30, 2.15), (-4.35, 2.15), (-4.35, 1.0)]
ax1.fill([-5.50, -4.95, -4.35, -4.30, -4.30], [1.0, 1.0, 2.15, 3.50, 1.0], color='#4caf50', alpha=0.4, label='Option A: Rear Chamfered Ramp (45° Gusset)')
ax1.plot([-5.50, -4.30], [1.0, 3.50], color='#2e7d32', lw=3, linestyle='--', label='Smooth 45° Stress-Relief Chamfer')

# Draw Brass Insert (sitting ON TOP of Rib 4 at Z = 2.15mm, thickness 0.50mm)
ax1.fill([-5.20, -4.40, -4.40, -5.20], [2.15, 2.15, 2.65, 2.65], color='#ffd54f', alpha=0.9, edgecolor='#f57f17', lw=2, label='Brass Insert U-Bridge (Z=2.15 to 2.65mm)')

ax1.set_xlim(-7.5, 0.5)
ax1.set_ylim(-0.5, 12.0)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_xlabel('Y (mm)')
ax1.set_ylabel('Z (mm)')
ax1.set_title('Option A: Rear Chamfered Buttress (From Rib 4 up to Half Moon)', fontsize=11, fontweight='bold')
ax1.legend(loc='upper left', fontsize=8)

# -------------------------------------------------------------
# Panel 2: Ramp From One Rib to the Next (Rib 4 to Rib 3 under Half Moon)
# -------------------------------------------------------------
# What if the floor between Rib 4 and Rib 3 is raised / chamfered to Z = 2.15mm?
ax2.fill([-7.5, 2.0, 2.0, -7.5], [0, 0, 1.0, 1.0], color='#b0bec5', alpha=0.7)
ax2.fill([-4.95, -4.35, -4.35, -4.95], [1.0, 1.0, 2.15, 2.15], color='#ffb74d', alpha=0.9)
ax2.fill([-1.65, -1.05, -1.05, -1.65], [1.0, 1.0, 2.15, 2.15], color='#ffb74d', alpha=0.9)

# Raised floor / chamfered ramp from Rib 4 (Y=-4.35) to Rib 3 (Y=-1.65):
# Elevates the floor between Rib 4 and Rib 3 up to Z = 2.15mm!
# The half moon now stands on a solid Z = 2.15mm foundation!
# And lead-in chamfers at the ends (45 deg)
ax2.fill([-5.50, -4.95, -1.05, -0.50, -0.50, -5.50], [1.0, 2.15, 2.15, 1.0, 1.0, 1.0],
         color='#ab47bc', alpha=0.4, label='Option B: Solid Raised Bed between Rib 4 & Rib 3 (Z=2.15mm)')
ax2.plot([-5.50, -4.95, -1.05, -0.50], [1.0, 2.15, 2.15, 1.0], color='#6a1b9a', lw=3, label='Chamfered Ramps (45° at Rib Ends)')

# Draw Half Moon on top of this raised bed
ax2.fill([-4.30, -3.00, -3.00, -3.25, -4.30], [2.15, 2.15, 8.5, 10.5, 10.5], color='#90caf9', alpha=0.7, label='Half Moon (Starts at Z=2.15mm)')
ax2.plot([-4.30, -4.30, -3.25, -3.00, -3.00, -4.30], [2.15, 10.5, 10.5, 8.5, 2.15, 2.15], color='#1565c0', lw=2.5)

# Draw Brass Insert resting on Z=2.15mm
ax2.fill([-5.20, -4.40, -4.40, -5.20], [2.15, 2.15, 2.65, 2.65], color='#ffd54f', alpha=0.9, edgecolor='#f57f17', lw=2, label='Brass Insert U-Bridge')

ax2.set_xlim(-7.5, 0.5)
ax2.set_ylim(-0.5, 12.0)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_xlabel('Y (mm)')
ax2.set_ylabel('Z (mm)')
ax2.set_title('Option B: Full Rib-to-Rib Raised Pedestal (Rib 4 to Rib 3)', fontsize=11, fontweight='bold')
ax2.legend(loc='upper left', fontsize=8)

plt.tight_layout()
plt.savefig('testing/rib_chamfer_options.png')
print("Saved testing/rib_chamfer_options.png")
