"""
testing/compare_reinforcement_variations.py
Compares 4 variations of reinforcing the center curved feature:
- Var 1: Solid D-Shape (flat base at Y = -4.069mm, 100% solid core)
- Var 2: Solid with +0.13mm Base Extension (flat base at Y = -4.200mm, depth = 1.75mm)
- Var 3: Solid D-shape + Central Rear Buttress (X in [5.48, 7.08], extending to Y = -4.35mm)
- Var 4: 3D Flared Base (tapered from top Z=10.5 down to wider base at Z=1.0)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    create_bracket_seating_ribs_poly, BRACKET_SEATING_RIB_Y,
    create_center_curved_feature_poly, BASE_THICK
)

cx = 6.279
w_x = 4.30
h_y = 1.62
rx = w_x / 2.0
ry = h_y
base_y = -4.069

angles = np.linspace(np.pi, 0, 32)
out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]

# Current hollow
wall_t = 0.60
rib_t = 0.60
in_arc = [(cx + (rx - wall_t) * np.cos(a), base_y + (ry - wall_t) * np.sin(a)) for a in angles]
p_current = unary_union([
    Polygon(out_arc + list(reversed(in_arc))),
    box(cx - rib_t/2, base_y, cx + rib_t/2, base_y + ry)
])

# Var 1: Solid D-Shape
p_var1 = Polygon(out_arc + [(cx - rx, base_y)])

# Var 2: Solid Extended to Y = -4.20mm (Depth = 1.75mm, +0.131mm reinforcement in -Y)
p_var2 = Polygon([(cx - rx, -4.200), (cx - rx, base_y)] + out_arc + [(cx + rx, base_y), (cx + rx, -4.200)])

# Var 3: Solid D-Shape + Central Rear Buttress (width = 1.60mm, extending to Y = -4.35mm)
buttress_w = 1.60
buttress_poly = box(cx - buttress_w/2, -4.350, cx + buttress_w/2, base_y)
p_var3 = unary_union([p_var1, buttress_poly])

# Var 4: Solid with full rear contour (convex ellipse arc or rounded bottom)
# Sits at Y in [-4.20, -2.45]
p_var4 = Polygon([(cx - rx, -4.150)] + [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles] + [(cx + rx, -4.150)])

print("=== VARIATION CLEARANCES AND METRICS ===")
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)
ribs = create_bracket_seating_ribs_poly()

# Rib 4 is at Y = -4.65, top at Y = -4.35.
# Brass bridge top is at Y = -4.65.
for name, p in [
    ("Current Hollow Arc", p_current),
    ("Var 1: Solid D-Shape (Base Y=-4.069)", p_var1),
    ("Var 2: Solid Base Y=-4.200 (Depth=1.75)", p_var2),
    ("Var 3: Solid D-Shape + Central Buttress (Y=-4.35)", p_var3),
    ("Var 4: Solid Base Y=-4.150 (Depth=1.70)", p_var4)
]:
    b = p.bounds
    gap_rib4 = b[1] - (-4.35)
    gap_brass = b[1] - (-4.65)
    print(f"{name}:")
    print(f"  Bounds: X in [{b[0]:.3f}, {b[2]:.3f}], Y in [{b[1]:.3f}, {b[3]:.3f}]")
    print(f"  Area: {p.area:.3f} mm² (+{(p.area/p_current.area - 1)*100:.1f}%)")
    print(f"  Gap to Rib 4 top (Y=-4.35): {gap_rib4:.3f} mm")
    print(f"  Gap to Brass Bridge (Y=-4.65): {gap_brass:.3f} mm")

# Plot 4-panel comparison
fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=180)

# Hot blade
blade_x_min = 6.279 - 1.52/2.0
blade_x_max = 6.279 + 1.52/2.0
blade_y_min = 2.890 - 6.35/2.0
blade_y_max = 2.890 + 6.35/2.0

panels = [
    (axes[0, 0], "Variation 1: 100% Solid D-Shape\n(Base: Y = -4.07mm, Depth: 1.62mm)", p_var1, '#8e24aa'),
    (axes[0, 1], "Variation 2: 100% Solid with +0.13mm Base Extension\n(Base: Y = -4.20mm, Depth: 1.75mm)", p_var2, '#6a1b9a'),
    (axes[1, 0], "Variation 3: Solid D-Shape + Central Rear Buttress\n(Buttress to Y = -4.35mm in central corridor)", p_var3, '#4a148c'),
    (axes[1, 1], "Variation 4: 100% Solid with +0.08mm Base Extension\n(Base: Y = -4.15mm, Depth: 1.70mm)", p_var4, '#311b92'),
]

for ax, title, poly, col in panels:
    ax.plot(*b3.exterior.xy, color='#2e7d32', lw=2)
    ax.plot(*b4.exterior.xy, color='#1565c0', lw=2)
    ax.fill(*b3.exterior.xy, color='#e8f5e9', alpha=0.3)
    ax.fill(*b4.exterior.xy, color='#e3f2fd', alpha=0.3)
    
    # Seating Rib 4
    for geom in (ribs.geoms if hasattr(ribs, 'geoms') else [ribs]):
        gx, gy = geom.exterior.xy
        if min(gx) > 0 and max(gy) < -3.0:
            ax.fill(gx, gy, color='#c8e6c9', edgecolor='#4caf50', lw=1.2, ls=':')
            
    # Brass insert
    brass_bridge = patches.Rectangle((3.70, -5.85), 5.15, 1.20,
                                     facecolor='#ffd54f', alpha=0.5, edgecolor='#f57f17', lw=1.8, label='Brass Insert Bridge')
    brass_left_jaw = patches.Rectangle((3.70, -4.65), 1.00, 7.00,
                                       facecolor='#ffe082', alpha=0.4, edgecolor='#f57f17', lw=1.2, ls='--')
    brass_right_jaw = patches.Rectangle((7.85, -4.65), 1.00, 7.00,
                                        facecolor='#ffe082', alpha=0.4, edgecolor='#f57f17', lw=1.2, ls='--', label='Brass Insert Jaws')
    ax.add_patch(brass_bridge)
    ax.add_patch(brass_left_jaw)
    ax.add_patch(brass_right_jaw)
    
    # Blade
    blade_box = patches.Rectangle((blade_x_min, blade_y_min), blade_x_max - blade_x_min, blade_y_max - blade_y_min,
                                  facecolor='#42a5f5', alpha=0.35, edgecolor='#1976d2', lw=1.8, label='Hot Plug Blade')
    ax.add_patch(blade_box)
    
    # Current hollow outline
    for geom in (p_current.geoms if hasattr(p_current, 'geoms') else [p_current]):
        ax.plot(*geom.exterior.xy, color='#d32f2f', lw=1.5, ls='--', label='Original Hollow 0.6mm Wall')
        
    # Reinforced poly
    for geom in (poly.geoms if hasattr(poly, 'geoms') else [poly]):
        ax.fill(*geom.exterior.xy, color=col, alpha=0.6, edgecolor='#1a237e', lw=2, label='Reinforced Solid Feature')
        
    # Dimension callout to brass bridge
    gap = poly.bounds[1] - (-4.65)
    ax.annotate(f'Clearance to Brass = {gap:.2f}mm',
                xy=(cx, poly.bounds[1]), xytext=(cx + 1.8, poly.bounds[1] - 0.4),
                arrowprops=dict(facecolor='#2e7d32', edgecolor='#1b5e20', width=1.2, headwidth=4),
                fontsize=8.5, fontweight='bold', color='#1b5e20',
                bbox=dict(boxstyle='round,pad=0.3', fc='#e8f5e9', ec='#2e7d32'))
                
    ax.set_xlim(2.0, 10.5)
    ax.set_ylim(-7.0, 0.5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel('X (mm)', fontweight='bold')
    ax.set_ylabel('Y (mm)', fontweight='bold')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=7.5)

plt.tight_layout()
out_png = os.path.join(os.path.dirname(__file__), 'reinforcement_variations_comparison.png')
plt.savefig(out_png, dpi=180)
print(f"\nSaved comparison plot to {out_png}")
