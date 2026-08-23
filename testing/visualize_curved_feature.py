"""
Visualize candidate curved geometry for the 10.5mm tall feature between Brackets 3 & 4.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    SCALE, X0, Y0, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

# Coordinates
cx = 6.279          # Centered between brackets 3 & 4
w_x = 4.30          # 4.3mm wide
h_y = 1.62          # 1.62mm in Y
y_bot_inner = -17.339
datum_y = y_bot_inner + 11.27  # -6.069 mm

rx = w_x / 2.0      # 2.15 mm
ry = h_y            # 1.62 mm
wall_t = 0.60       # Wall thickness
rib_t = 0.60        # Rib thickness

# 1. Variation 1: Curved Wall (Convex in +Y) with Central Internal Rib down to Datum (Y = -6.07mm)
# Arc apex at datum_y + ry = -4.45mm, base at datum_y = -6.07mm
angles = np.linspace(np.pi, 0, 32)
# Outer ellipse arc
outer_arc_pts = [(cx + rx * np.cos(a), datum_y + ry * np.sin(a)) for a in angles]
# Inner ellipse arc
inner_arc_pts = [(cx + (rx - wall_t) * np.cos(a), datum_y + (ry - wall_t) * np.sin(a)) for a in angles]

# Curved wall polygon (closed loop)
curved_wall_pts = outer_arc_pts + list(reversed(inner_arc_pts))
curved_wall_poly = Polygon(curved_wall_pts)

# Internal Rib along center (X = cx), from inner apex down to datum_y
rib_poly_1 = box(cx - rib_t/2.0, datum_y, cx + rib_t/2.0, datum_y + ry)
feat_poly_1 = unary_union([curved_wall_poly, rib_poly_1])

# 2. Variation 2: Curved Wall (Convex in -Y) with Central Internal Rib
outer_arc_pts_2 = [(cx + rx * np.cos(a), datum_y - ry * np.sin(a)) for a in angles]
inner_arc_pts_2 = [(cx + (rx - wall_t) * np.cos(a), datum_y - (ry - wall_t) * np.sin(a)) for a in angles]
curved_wall_pts_2 = outer_arc_pts_2 + list(reversed(inner_arc_pts_2))
curved_wall_poly_2 = Polygon(curved_wall_pts_2)
rib_poly_2 = box(cx - rib_t/2.0, datum_y - ry, cx + rib_t/2.0, datum_y)
feat_poly_2 = unary_union([curved_wall_poly_2, rib_poly_2])

# 3. Variation 3: Closed Elliptical Shell (4.30 x 1.62mm) with Internal Rib
angles_full = np.linspace(0, 2*np.pi, 64)
ellipse_out = [(cx + rx * np.cos(a), (datum_y + ry/2.0) + (ry/2.0) * np.sin(a)) for a in angles_full]
ellipse_in = [(cx + (rx - wall_t) * np.cos(a), (datum_y + ry/2.0) + (ry/2.0 - wall_t) * np.sin(a)) for a in angles_full]
feat_poly_3 = Polygon(ellipse_out).difference(Polygon(ellipse_in))
feat_poly_3 = unary_union([feat_poly_3, box(cx - rib_t/2.0, datum_y, cx + rib_t/2.0, datum_y + ry)])

fig, axes = plt.subplots(1, 3, figsize=(21, 7), dpi=160)

for ax, poly, title in [
    (axes[0], feat_poly_1, "Option 1: Curved Wall (Convex +Y)\nInternal Rib extends to Datum Y = -6.07mm"),
    (axes[1], feat_poly_2, "Option 2: Curved Wall (Convex -Y)\nInternal Rib extends to Datum Y = -6.07mm"),
    (axes[2], feat_poly_3, "Option 3: Elliptical Enclosure (4.3x1.62mm)\nInternal Dividing Rib in Center")
]:
    ax.plot(*b3.exterior.xy, 'g-', linewidth=2, label='Bracket 3 (4.60mm)')
    ax.plot(*b4.exterior.xy, 'g-', linewidth=2, label='Bracket 4 (4.60mm)')
    
    for geom in (poly.geoms if hasattr(poly, 'geoms') else [poly]):
        ax.fill(*geom.exterior.xy, color='#ab47bc', alpha=0.4)
        ax.plot(*geom.exterior.xy, color='#8e24aa', linewidth=2.2, label='New Curved Feature (10.5mm)')
        for interior in geom.interiors:
            ax.plot(*interior.xy, color='#8e24aa', linewidth=1.5)
            
    ax.axhline(datum_y, color='red', linestyle='-.', linewidth=1.5, label=f'Datum: Y = {datum_y:.2f}mm (11.27mm from bottom)')
    ax.set_xlim(1, 12)
    ax.set_ylim(-9, -2.5)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('curved_feature_candidates.png', dpi=160)
print("Saved curved_feature_candidates.png")
