"""
Test 5.00mm interior width U-arch geometry.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString, box
import matplotlib.pyplot as plt

# Dimensions
w_inner = 5.00       # 5.00mm interior width
r_inner = w_inner / 2.0  # 2.50mm
wall_thick = 1.20    # 1.20mm wall thickness
r_outer = r_inner + wall_thick  # 3.70mm

y_bot = -16.65       # bottom baseline
# If inner apex is at Y = -11.00mm:
y_apex_inner = -11.00
y_arc_center = y_apex_inner - r_inner  # -13.50mm
y_apex_outer = y_arc_center + r_outer  # -9.80mm

# Inner contour:
angles = np.linspace(np.pi, 0, 32)
arc_inner_pts = [(r_inner * np.cos(a), y_arc_center + r_inner * np.sin(a)) for a in angles]
inner_pts = [(-r_inner, y_bot), (-r_inner, y_arc_center)] + arc_inner_pts + [(r_inner, y_arc_center), (r_inner, y_bot)]
inner_line = LineString(inner_pts)

# Outer contour:
arc_outer_pts = [(r_outer * np.cos(a), y_arc_center + r_outer * np.sin(a)) for a in angles]
outer_pts_list = [(r_outer, y_bot), (r_outer, y_arc_center)] + list(reversed(arc_outer_pts)) + [(-r_outer, y_arc_center), (-r_outer, y_bot)]
outer_line = LineString(outer_pts_list)

# Full wall polygon (closed loop)
wall_polygon_pts = outer_pts_list + inner_pts
arch_wall_poly = Polygon(wall_polygon_pts)

fig, ax = plt.subplots(figsize=(8, 8), dpi=160)
ix, iy = inner_line.xy
ox, oy = outer_line.xy
ax.plot(ix, iy, 'b-o', markersize=3, label=f'Inner Arch Profile (Interior Width: {w_inner:.2f}mm)')
ax.plot(ox, oy, 'r-', linewidth=2, label=f'Outer Arch Profile (Wall Thick: {wall_thick:.2f}mm)')

ax.axhline(y_bot, color='gray', linestyle=':', label=f'Bottom Inset Wall (Y = {y_bot:.2f}mm)')

# Dimension annotation for 5mm width
ax.annotate('', xy=(-r_inner, -15.5), xytext=(r_inner, -15.5),
            arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
ax.text(0, -15.2, f'{w_inner:.2f} mm Interior Width', ha='center', va='bottom',
        color='blue', fontweight='bold', fontsize=10)

ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Bottom Arch with 5.00 mm Interior Width at Base', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig('arch_5mm_test.png', dpi=160)
print("Saved arch_5mm_test.png successfully!")
