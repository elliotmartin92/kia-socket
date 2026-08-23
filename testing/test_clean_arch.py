"""
Test clean geometric curve for bottom arch.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString, box
import matplotlib.pyplot as plt

# Dimensions
w_arch = 3.67  # width in mm
r_arch = w_arch / 2.0  # 1.835 mm
y_bot = -16.65  # bottom baseline
y_top = -11.00  # apex of arch
y_arc_center = y_top - r_arch  # -12.835 mm

# Clean curve:
# 1. Left vertical leg: from ( -r_arch, y_bot ) up to ( -r_arch, y_arc_center )
# 2. Semicircular arc: from angle pi (left) to 0 (right)
#    x(a) = r_arch * cos(a), y(a) = y_arc_center + r_arch * sin(a)
# 3. Right vertical leg: from ( +r_arch, y_arc_center ) down to ( +r_arch, y_bot )

angles = np.linspace(np.pi, 0, 32)
arc_pts = [(r_arch * np.cos(a), y_arc_center + r_arch * np.sin(a)) for a in angles]

clean_arch_pts = [(-r_arch, y_bot), (-r_arch, y_arc_center)] + arc_pts + [(r_arch, y_arc_center), (r_arch, y_bot)]
clean_arch_line = LineString(clean_arch_pts)

# Plot
fig, ax = plt.subplots(figsize=(8, 8), dpi=160)
cx, cy = clean_arch_line.xy
ax.plot(cx, cy, 'b-o', markersize=3, label='Clean Geometric Arch (Ø3.67mm U-arch)')

# Wall buffer (1.2mm thick)
arch_wall = clean_arch_line.buffer(1.20 / 2.0, cap_style=2)
wx, wy = arch_wall.exterior.xy
ax.plot(wx, wy, 'r--', label='Arch Wall (1.20mm thick)')

# Baseline
ax.axhline(y_bot, color='gray', linestyle=':', label=f'Bottom Inset Wall (Y = {y_bot}mm)')

ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Clean Geometric Bottom Arch Profile', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.legend()

plt.tight_layout()
plt.savefig('clean_arch_test.png', dpi=160)
print("Saved clean_arch_test.png successfully!")
