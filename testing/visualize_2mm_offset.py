"""
Visualize the exact 2mm offset of the curved feature relative to the brackets.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_part import (
    SCALE, X0, Y0, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

cx = 6.279          # Centered between brackets 3 & 4
w_x = 4.30          # 4.3mm wide
h_y = 1.62          # 1.62mm in Y
y_bot_inner = -17.339
datum_y = y_bot_inner + 11.27  # -6.069 mm (top of bracket bottom hook in PNG)

rx = w_x / 2.0      # 2.15 mm
ry = h_y            # 1.62 mm
wall_t = 0.60
rib_t = 0.60

# Option 1A: Base of curved feature at Y = datum_y + 2.0mm = -4.07mm (2mm in +Y from the bracket step)
base_y_1a = datum_y + 2.00  # -4.069 mm
angles = np.linspace(np.pi, 0, 32)
out_arc_1a = [(cx + rx * np.cos(a), base_y_1a + ry * np.sin(a)) for a in angles]
in_arc_1a = [(cx + (rx - wall_t) * np.cos(a), base_y_1a + (ry - wall_t) * np.sin(a)) for a in angles]
wall_poly_1a = Polygon(out_arc_1a + list(reversed(in_arc_1a)))
rib_poly_1a = box(cx - rib_t/2.0, base_y_1a, cx + rib_t/2.0, base_y_1a + ry)
feat_1a = unary_union([wall_poly_1a, rib_poly_1a])

# Option 1B: Base of curved feature at Y = -7.171 + 2.0mm = -5.171mm (2mm from lowest bracket edge)
base_y_1b = -7.171 + 2.00  # -5.171 mm
out_arc_1b = [(cx + rx * np.cos(a), base_y_1b + ry * np.sin(a)) for a in angles]
in_arc_1b = [(cx + (rx - wall_t) * np.cos(a), base_y_1b + (ry - wall_t) * np.sin(a)) for a in angles]
wall_poly_1b = Polygon(out_arc_1b + list(reversed(in_arc_1b)))
rib_poly_1b = box(cx - rib_t/2.0, base_y_1b, cx + rib_t/2.0, base_y_1b + ry)
feat_1b = unary_union([wall_poly_1b, rib_poly_1b])

fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=160)

# Panel 1: Option 1A (2.0mm above the horizontal step Y = -6.07mm -> Base at Y = -4.07mm)
ax1 = axes[0]
ax1.plot(*b3.exterior.xy, 'g-', linewidth=2, label='Bracket 3 (4.60mm)')
ax1.plot(*b4.exterior.xy, 'g-', linewidth=2, label='Bracket 4 (4.60mm)')
for geom in (feat_1a.geoms if hasattr(feat_1a, 'geoms') else [feat_1a]):
    ax1.fill(*geom.exterior.xy, color='#ab47bc', alpha=0.4)
    ax1.plot(*geom.exterior.xy, color='#8e24aa', linewidth=2.2, label='Curved Feature (10.5mm tall)')
    for interior in geom.interiors:
        ax1.plot(*interior.xy, color='#8e24aa', linewidth=1.5)

ax1.axhline(datum_y, color='red', linestyle='-.', linewidth=1.2, label=f'Bracket Step (Y = {datum_y:.2f}mm)')
ax1.axhline(base_y_1a, color='blue', linestyle=':', linewidth=1.2, label=f'Feature Base (Y = {base_y_1a:.2f}mm)')

# Dimension arrows for 2mm gap
ax1.annotate('', xy=(3.5, datum_y), xytext=(3.5, base_y_1a),
             arrowprops=dict(arrowstyle='<->', color='blue', lw=1.8))
ax1.text(3.3, (datum_y + base_y_1a)/2, '2.00 mm', ha='right', va='center', color='blue', fontweight='bold')

ax1.set_xlim(1, 12)
ax1.set_ylim(-8.5, -1)
ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_title('Option 1A: Base is 2.0mm in +Y from Bracket Step\n(Base: Y = -4.07mm, Apex: Y = -2.45mm)', fontsize=11, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8.5)

# Panel 2: Option 1B (2.0mm above the bottom edge Y = -7.17mm -> Base at Y = -5.17mm)
ax2 = axes[1]
ax2.plot(*b3.exterior.xy, 'g-', linewidth=2, label='Bracket 3 (4.60mm)')
ax2.plot(*b4.exterior.xy, 'g-', linewidth=2, label='Bracket 4 (4.60mm)')
for geom in (feat_1b.geoms if hasattr(feat_1b, 'geoms') else [feat_1b]):
    ax2.fill(*geom.exterior.xy, color='#ab47bc', alpha=0.4)
    ax2.plot(*geom.exterior.xy, color='#8e24aa', linewidth=2.2, label='Curved Feature (10.5mm tall)')
    for interior in geom.interiors:
        ax2.plot(*interior.xy, color='#8e24aa', linewidth=1.5)

ax2.axhline(-7.171, color='red', linestyle='-.', linewidth=1.2, label='Bracket Bottom Edge (Y = -7.17mm)')
ax2.axhline(base_y_1b, color='blue', linestyle=':', linewidth=1.2, label=f'Feature Base (Y = {base_y_1b:.2f}mm)')

ax2.annotate('', xy=(3.5, -7.171), xytext=(3.5, base_y_1b),
             arrowprops=dict(arrowstyle='<->', color='blue', lw=1.8))
ax2.text(3.3, (-7.171 + base_y_1b)/2, '2.00 mm', ha='right', va='center', color='blue', fontweight='bold')

ax2.set_xlim(1, 12)
ax2.set_ylim(-8.5, -1)
ax2.set_aspect('equal')
ax2.grid(True)
ax2.set_title('Option 1B: Base is 2.0mm in +Y from Bracket Bottom Edge\n(Base: Y = -5.17mm, Apex: Y = -3.55mm)', fontsize=11, fontweight='bold')
ax2.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
plt.savefig('curved_feature_2mm_offset.png', dpi=160)
print("Saved curved_feature_2mm_offset.png")
