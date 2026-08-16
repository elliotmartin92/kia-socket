"""
Test updating the side ears (left and right) to 3.55mm interior width.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt

from build_part import outer_pts, OUTER_WALL_THICK

pts = outer_pts.copy()

# Target interior width = 3.55mm
# With wall thickness = 1.20mm, outer width = 3.55 + 2 * 1.20 = 5.95mm (Y in [-2.975, +2.975]mm)
y_outer_half = 3.55 / 2.0 + OUTER_WALL_THICK  # 2.975mm

# Let's inspect modifying the right side ear:
# In outer_pts:
# Right side ear: indices 0..4 (and 242..243)
# Index 0: X = 18.206, Y = 4.442 -> Y = +2.975
# Index 1: X = 20.200, Y = 4.442 -> Y = +2.975
# Index 2: X = 20.200, Y = 0.000 -> Y = 0.000
# Index 3: X = 20.200, Y = -4.442 -> Y = -2.975
# Index 4: X = 18.206, Y = -4.442 -> Y = -2.975

# Left side ear: indices 111..139
# Index 111: X = -19.081, Y = -4.407 -> Y = -2.975
# Index 136: X = -21.075, Y = -4.407 -> Y = -2.975
# Index 137: X = -21.075, Y = 0.035 -> Y = 0.000
# Index 138: X = -21.075, Y = 4.477 -> Y = +2.975
# Index 139: X = -19.081, Y = 4.477 -> Y = +2.975

def build_poly_with_side_ears_355(target_interior_w=3.55):
    y_half_out = target_interior_w / 2.0 + OUTER_WALL_THICK # 2.975mm
    
    new_pts = pts.copy()
    
    # 1. Right Ear (indices 0..4, 242..243)
    new_pts[0] = [18.206, y_half_out]
    new_pts[1] = [20.200, y_half_out]
    new_pts[2] = [20.200, 0.0]
    new_pts[3] = [20.200, -y_half_out]
    new_pts[4] = [18.206, -y_half_out]
    if len(new_pts) > 242:
        new_pts[242] = [18.206, y_half_out]
        new_pts[243] = [18.206, y_half_out]
        
    # 2. Left Ear (indices 111..139)
    # The intermediate arc points on the outer perimeter can be filtered/adjusted
    # Or clean rectangular flange:
    # From Index 110 (X = -18.954, Y = -4.774), we step to (-19.081, -y_half_out) -> (-21.075, -y_half_out) -> (-21.075, +y_half_out) -> (-19.081, +y_half_out)
    new_pts[111] = [-19.081, -y_half_out]
    new_pts[136] = [-21.075, -y_half_out]
    new_pts[137] = [-21.075, 0.0]
    new_pts[138] = [-21.075, y_half_out]
    new_pts[139] = [-19.081, y_half_out]
    
    # Remove any intermediate points between 111 and 136, or set their Y to -y_half_out
    for k in range(112, 136):
        new_pts[k] = new_pts[136]
        
    # Also align bottom notch (X = ±3.70mm)
    for idx, (x, y) in enumerate(new_pts):
        if abs(y - (-18.539)) < 0.05:
            if abs(x - 1.382) < 0.05:
                new_pts[idx] = [3.70, -18.539]
            elif abs(x - (-2.291)) < 0.05:
                new_pts[idx] = [-3.70, -18.539]
        elif abs(y - (-16.650)) < 0.05:
            if abs(x - 1.382) < 0.05:
                new_pts[idx] = [3.70, -16.650]
            elif abs(x - (-2.291)) < 0.05:
                new_pts[idx] = [-3.70, -16.650]
                
    poly = Polygon(new_pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly

poly_355 = build_poly_with_side_ears_355(3.55)
inner_355 = poly_355.buffer(-OUTER_WALL_THICK)

fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=160)

# Right Side Ear Close Up
axes[0].plot(*poly_355.exterior.xy, 'b-o', markersize=3, label='Outer Perimeter')
axes[0].plot(*inner_355.exterior.xy, 'r--', linewidth=1.5, label='Inner Perimeter Wall')
axes[0].axhline(3.55/2.0, color='green', linestyle=':', label='Y = +1.775mm (Interior Bound)')
axes[0].axhline(-3.55/2.0, color='green', linestyle=':', label='Y = -1.775mm (Interior Bound)')
axes[0].annotate(f'Interior Width = 3.55mm\nOuter Width = 5.95mm', xy=(19.0, 0), xytext=(15.0, 0),
                arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=10, fontweight='bold')
axes[0].set_xlim(16, 22)
axes[0].set_ylim(-6, 6)
axes[0].set_aspect('equal')
axes[0].grid(True)
axes[0].set_title('Right Side Ear (3.55mm Interior Width)', fontsize=12, fontweight='bold')
axes[0].legend(loc='lower left')

# Left Side Ear Close Up
axes[1].plot(*poly_355.exterior.xy, 'b-o', markersize=3, label='Outer Perimeter')
axes[1].plot(*inner_355.exterior.xy, 'r--', linewidth=1.5, label='Inner Perimeter Wall')
axes[1].axhline(3.55/2.0, color='green', linestyle=':', label='Y = +1.775mm (Interior Bound)')
axes[1].axhline(-3.55/2.0, color='green', linestyle=':', label='Y = -1.775mm (Interior Bound)')
axes[1].annotate(f'Interior Width = 3.55mm\nOuter Width = 5.95mm', xy=(-20.0, 0), xytext=(-16.0, 0),
                arrowprops=dict(facecolor='black', arrowstyle='->'), fontsize=10, fontweight='bold')
axes[1].set_xlim(-22, -16)
axes[1].set_ylim(-6, 6)
axes[1].set_aspect('equal')
axes[1].grid(True)
axes[1].set_title('Left Side Ear (3.55mm Interior Width)', fontsize=12, fontweight='bold')
axes[1].legend(loc='lower right')

plt.tight_layout()
plt.savefig('side_ears_355_preview.png', dpi=160)
print("Saved side_ears_355_preview.png")
