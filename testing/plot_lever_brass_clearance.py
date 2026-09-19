import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER, CAM_X_CENTER
from build_part import BRACKET_SEATING_RIB_HEIGHT, BASE_THICK

fig, axes = plt.subplots(1, 2, figsize=(18, 9), facecolor='#1a1a1a', dpi=180)

# Panel 1: Current Collision in (Y-Z)
ax1 = axes[0]
ax1.set_facecolor('#222222')
ax1.set_title('1. CURRENT: Seated Brass Contact Collides with Cam (Pushes Lever Up)', color='white', fontsize=12, weight='bold')

# Baseplate and Tower
ax1.add_patch(patches.Rectangle((-2, 0), 16, 1.0, facecolor='#888888', alpha=0.5, label='Floor (Z=1.0mm)'))
ax1.add_patch(patches.Rectangle((2.7, 1.0), 7.2, 1.15, facecolor='#e67e22', alpha=0.4, label='Bracket Seating Ribs (Z=2.15mm)'))

# Brass contact profile in Y-Z:
# Seated on Z = 2.15mm, top at Z = 16.55mm, rear face at Y = 3.85mm
ax1.add_patch(patches.Rectangle((-1.0, 2.15), 4.85, 14.40, facecolor='#f1c40f', alpha=0.35, edgecolor='#f39c12', lw=2, label='Seated Brass Contact (Y <= 3.85mm)'))

# Shaft Hub
ax1.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#3498db', alpha=0.5, edgecolor='#2980b9', lw=2, label='Shaft Hub (Y=9.28, Z=12.59)'))

# Current Cam
curr_cam = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0 + 0.5),
    (5.00, 9.80),
    (1.50, 7.20),
    (1.80, 5.00),
    (4.50, 5.20),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
]
ax1.add_patch(patches.Polygon(curr_cam, facecolor='#e74c3c', alpha=0.6, edgecolor='red', lw=2, label='Current Cam (Reaches Y=1.50mm)'))

# Highlight collision zone
ax1.annotate('COLLISION OVERLAP\nDelta Y = 2.35 mm!\nBrass presses cam down,\nlever plunger pushed up!',
             xy=(2.8, 7.5), xytext=(0.5, 12.0),
             arrowprops=dict(arrowstyle='->', color='red', lw=2.5),
             color='red', fontsize=10, weight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#330000', edgecolor='red'))

ax1.set_xlim(-2, 14)
ax1.set_ylim(0, 18)
ax1.set_xlabel('Y (mm)', color='white')
ax1.set_ylabel('Z (mm)', color='white')
ax1.tick_params(colors='white')
ax1.grid(True, color='#444444', linestyle=':')
ax1.legend(loc='upper right', fontsize=8.5, facecolor='#111111', labelcolor='white')

# Panel 2: Optimized Cam in (Y-Z)
ax2 = axes[1]
ax2.set_facecolor('#222222')
ax2.set_title('2. OPTIMIZED: Terminated at Y=3.95mm (Zero Interference with Seated Brass)', color='white', fontsize=12, weight='bold')

ax2.add_patch(patches.Rectangle((-2, 0), 16, 1.0, facecolor='#888888', alpha=0.5, label='Floor (Z=1.0mm)'))
ax2.add_patch(patches.Rectangle((2.7, 1.0), 7.2, 1.15, facecolor='#e67e22', alpha=0.4, label='Bracket Seating Ribs (Z=2.15mm)'))
ax2.add_patch(patches.Rectangle((-1.0, 2.15), 4.85, 14.40, facecolor='#f1c40f', alpha=0.35, edgecolor='#f39c12', lw=2, label='Seated Brass Contact (Y <= 3.85mm)'))
ax2.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#3498db', alpha=0.5, edgecolor='#2980b9', lw=2, label='Shaft Hub'))

# Plug blade path (Y in [-0.68, 5.68])
ax2.add_patch(patches.Rectangle((-0.68, 3.0), 6.35, 15.0, facecolor='#ffffff', alpha=0.25, edgecolor='cyan', lw=1.5, linestyle='--', label='Plug Blade Path (Y in [-0.68, 5.68])'))

# Optimized Cam Profile
opt_cam = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0 + 0.3),
    (5.80, 11.20),
    (3.95, 6.80),   # Active contact tip at Y = 3.95mm (> 3.85mm -> CLEAR!)
    (4.30, 5.20),   # Rounded nose underside
    (5.60, 6.20),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
]
ax2.add_patch(patches.Polygon(opt_cam, facecolor='#2ecc71', alpha=0.7, edgecolor='#27ae60', lw=2, label='Optimized Cam (Y >= 3.95mm)'))

ax2.annotate('GUARANTEED CLEARANCE!\nAir gap = +0.10mm to brass.\nBlade rear (Y=3.95 to 5.68)\nactively drives cam downward!',
             xy=(4.2, 8.5), xytext=(5.5, 14.0),
             arrowprops=dict(arrowstyle='->', color='#2ecc71', lw=2.5),
             color='#2ecc71', fontsize=10, weight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#003300', edgecolor='#2ecc71'))

ax2.set_xlim(-2, 14)
ax2.set_ylim(0, 18)
ax2.set_xlabel('Y (mm)', color='white')
ax2.set_ylabel('Z (mm)', color='white')
ax2.tick_params(colors='white')
ax2.grid(True, color='#444444', linestyle=':')
ax2.legend(loc='upper right', fontsize=8.5, facecolor='#111111', labelcolor='white')

plt.tight_layout()
out_p = 'testing/lever_brass_clearance_optimization.png'
plt.savefig(out_p, dpi=180)
print(f'Saved {out_p}')
