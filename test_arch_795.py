"""
Analyze the 7.95mm dimension for the bottom central arch.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

from build_part import OUTER_WALL_THICK, OUTER_WALL_HEIGHT

# In 2D (Y dimension):
# Base at Y = -16.650 mm (the inset bottom exterior wall)
# If total outer height in Y = 7.95 mm:
y_base = -16.650
y_outer_apex = y_base + 7.95  # -8.700 mm
wall_t = 1.20  # mm
y_inner_apex = y_outer_apex - wall_t  # -9.900 mm

# Arch width: inner width = 5.00 mm (R_inner = 2.50 mm)
r_in = 2.50
r_out = r_in + wall_t  # 3.70 mm

# The arch curve center in Y:
# Top apex of outer semicircle is at center_y + r_out = -8.700 -> center_y = -8.700 - 3.70 = -12.400 mm
# Top apex of inner semicircle is at center_y + r_in = -12.400 + 2.50 = -9.900 mm (exact match!)
center_y = y_outer_apex - r_out  # -12.400 mm

print(f"Arch in Y dimension (Total outer height = 7.95 mm):")
print(f"  Base at Inset Wall: Y = {y_base:.3f} mm")
print(f"  Arc Center Y:       Y = {center_y:.3f} mm")
print(f"  Inner Apex:         Y = {y_inner_apex:.3f} mm (Inner height = {y_inner_apex - y_base:.3f} mm)")
print(f"  Outer Apex:         Y = {y_outer_apex:.3f} mm (Outer height = {y_outer_apex - y_base:.3f} mm)")
print(f"  Straight wall leg:  {center_y - y_base:.3f} mm in Y before curve starts")

def make_arch_poly_795():
    th = np.linspace(0, np.pi, 50)
    outer_arc = [(r_out * np.cos(t), center_y + r_out * np.sin(t)) for t in th]
    outer_full = [(r_out, y_base)] + outer_arc + [(-r_out, y_base)]
    
    inner_arc = [(r_in * np.cos(t), center_y + r_in * np.sin(t)) for t in th[::-1]]
    inner_full = [(-r_in, y_base)] + inner_arc + [(r_in, y_base)]
    return Polygon(outer_full + inner_full)

arch_795 = make_arch_poly_795()
print(f"Arch polygon bounds: {arch_795.bounds}")
print(f"Outer height = {arch_795.bounds[3] - arch_795.bounds[1]:.3f} mm")

# Plot 2D comparison
fig, ax = plt.subplots(figsize=(10, 8), dpi=160)
ax.plot(*arch_795.exterior.xy, 'r-', linewidth=2, label='Arch Wall (7.95mm Outer Height, 5.0mm Inner Width)')
ax.axhline(y_base, color='blue', linestyle='-', label=f'Inset Bottom Ext Wall (Y = {y_base:.2f}mm)')
ax.axhline(y_outer_apex, color='green', linestyle=':', label=f'Outer Apex (Y = {y_outer_apex:.2f}mm, Total Height = 7.95mm)')

# Add dimension arrows
ax.annotate('', xy=(4.5, y_outer_apex), xytext=(4.5, y_base),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax.text(4.8, (y_base + y_outer_apex)/2, '7.95 mm\nOuter Height', va='center', fontweight='bold', fontsize=11)

ax.annotate('', xy=(-2.5, center_y), xytext=(2.5, center_y),
            arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
ax.text(0, center_y + 0.3, '5.00 mm Inner', ha='center', fontweight='bold', color='purple', fontsize=10)

ax.set_xlim(-8, 8)
ax.set_ylim(-19, -6)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Bottom Central Arch with 7.95mm Total Outer Height', fontsize=12, fontweight='bold')
ax.legend(loc='upper right')

plt.tight_layout()
plt.savefig('arch_795_preview.png', dpi=160)
print("Saved arch_795_preview.png")
