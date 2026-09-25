"""
testing/plot_chamfered_rib_options.py
Visualizes chamfered ramp implementations:
1. Chamfered ramps between seating ribs (trapezoidal rib profiles / 45 deg fillets between ribs)
2. Chamfered ramp / solid bridge from Rib 4 into the half moon base
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Coordinates:
# Rib 4: Y in [-4.95, -4.35], Z in [1.00, 2.15] (height = 1.15mm)
# Half Moon: Y in [-4.30, -3.00], Z in [1.00, 10.50]
# Rib 3: Y in [-1.65, -1.05], Z in [1.00, 2.15]
# Rib 2: Y in [1.65, 2.25], Z in [1.00, 2.15]
# Rib 1: Y in [4.95, 5.55], Z in [1.00, 2.15]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), dpi=180)

# Panel 1: Chamfered Ramps between Seating Ribs (in Bracket 3 & 4)
# Y from -6.0 to +6.5mm, Z from 0.5 to 3.5mm
y_grid = np.linspace(-6.0, 6.5, 500)
z_floor = 1.00
z_rib = 2.15
h_rib = 1.15

# Existing rectangular ribs profile:
z_rect = np.full_like(y_grid, z_floor)
for y_c in [-4.65, -1.35, 1.95, 5.25]:
    mask = (y_grid >= y_c - 0.30) & (y_grid <= y_c + 0.30)
    z_rect[mask] = z_rib

ax1.plot(y_grid, z_rect, 'r--', lw=2, label='Current: Sharp 90° Rectangular Ribs (High Stress Concentration Kt ~ 3.0)')

# Chamfered ramp profile from one rib to the next:
# Flat top land of width 0.30mm at Z = 2.15mm for brass seating
# 45° chamfered ramps (dz/dy = 1) sloping down to floor (or continuous valley)
z_chamfer = np.full_like(y_grid, z_floor)
chamf_dx = h_rib  # 1.15mm for 45° chamfer
for y_c in [-4.65, -1.35, 1.95, 5.25]:
    # Top flat land: width 0.30mm (y in [y_c - 0.15, y_c + 0.15])
    top_w = 0.30
    y_top_min = y_c - top_w/2.0
    y_top_max = y_c + top_w/2.0
    for i, y in enumerate(y_grid):
        if y_top_min <= y <= y_top_max:
            z_chamfer[i] = max(z_chamfer[i], z_rib)
        elif y < y_top_min and y >= y_top_min - chamf_dx:
            # Left 45° ramp
            z_val = z_rib - (y_top_min - y)
            z_chamfer[i] = max(z_chamfer[i], z_val)
        elif y > y_top_max and y <= y_top_max + chamf_dx:
            # Right 45° ramp
            z_val = z_rib - (y - y_top_max)
            z_chamfer[i] = max(z_chamfer[i], z_val)

ax1.fill_between(y_grid, z_floor, z_chamfer, color='#4caf50', alpha=0.35)
ax1.plot(y_grid, z_chamfer, color='#2e7d32', lw=2.5, label='Chamfered Ramps between Ribs (45° Stress Relief Kt ~ 1.2)')

# Draw brass insert seating line at Z = 2.15mm
ax1.plot([-5.5, 6.0], [z_rib, z_rib], color='#ffd54f', lw=3, label='Brass Insert Seating Plane (Z = 2.15mm)')

ax1.set_xlim(-6.5, 6.5)
ax1.set_ylim(0.5, 3.5)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_xlabel('Y (mm)')
ax1.set_ylabel('Z (mm)')
ax1.set_title('1. Seating Ribs: 45° Chamfered Ramps from One Rib to the Next', fontsize=11, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8)

# Panel 2: Integration with Half Moon
# Half Moon is at Y in [-4.30, -3.00], Z in [1.00, 10.50]
# Rib 4 is at Y in [-4.95, -4.35]
# Rib 3 is at Y in [-1.65, -1.05]
ax2.fill([-6.5, 1.0, 1.0, -6.5], [0, 0, 1.0, 1.0], color='#b0bec5', alpha=0.7, label='Baseplate Floor')

# Draw Chamfered Rib 4 & Rib 3 profile
ax2.plot(y_grid[(y_grid >= -6.0) & (y_grid <= 0.5)], z_chamfer[(y_grid >= -6.0) & (y_grid <= 0.5)], color='#2e7d32', lw=2.5, label='Chamfered Rib Foundation')
ax2.fill_between(y_grid[(y_grid >= -6.0) & (y_grid <= 0.5)], z_floor, z_chamfer[(y_grid >= -6.0) & (y_grid <= 0.5)], color='#4caf50', alpha=0.3)

# Draw Half Moon
# Half Moon now roots into the chamfered rib foundation at Z = 2.15mm!
ax2.fill([-4.30, -3.00, -3.00, -3.25, -4.30], [2.15, 2.15, 8.5, 10.5, 10.5], color='#2196f3', alpha=0.6, label='Half Moon Body')
ax2.plot([-4.30, -4.30, -3.25, -3.00, -3.00, -4.30], [2.15, 10.5, 10.5, 8.5, 2.15, 2.15], color='#0d47a1', lw=2.5)

# Rear Gusset/Chamfer from Rib 4 (Y=-4.95, Z=2.15) up to Moon back wall (Z=3.50mm)
# Or fillet between Rib 4 and Moon base
ax2.plot([-4.95, -4.35], [2.15, 2.15], color='#e65100', lw=3, label='Rib 4 Brass Seating Land')

# Brass Insert
ax2.fill([-5.20, -4.40, -4.40, -5.20], [2.15, 2.15, 2.65, 2.65], color='#ffd54f', alpha=0.9, edgecolor='#f57f17', lw=1.5, label='Brass Insert (Z = 2.15 to 2.65mm)')

ax2.set_xlim(-6.5, 1.0)
ax2.set_ylim(0.0, 11.5)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_xlabel('Y (mm)')
ax2.set_ylabel('Z (mm)')
ax2.set_title('2. Half Moon Anchored to Continuous Chamfered Rib Base', fontsize=11, fontweight='bold')
ax2.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('testing/chamfered_rib_options.png')
print("Saved testing/chamfered_rib_options.png")
