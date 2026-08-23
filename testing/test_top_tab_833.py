import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, get_exact_base_polygon, OUTER_WALL_THICK
import numpy as np
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

def build_poly_with_top_tab(tab_width=8.20):
    half_x = tab_width / 2.0
    pts = outer_pts.copy()
    
    # 1. Side Ears (8.20mm)
    half_ear_w = 8.20 / 2.0
    pts[0] = [18.206, half_ear_w]
    pts[1] = [20.200, half_ear_w]
    pts[2] = [20.200, 0.0]
    pts[3] = [20.200, -half_ear_w]
    pts[4] = [18.206, -half_ear_w]
    if len(pts) > 242:
        pts[242] = [18.206, half_ear_w]
        pts[243] = [18.206, half_ear_w]
        
    pts[111] = [-19.081, -half_ear_w]
    for k in range(112, 136):
        pts[k] = [-21.075, -half_ear_w]
    pts[136] = [-21.075, -half_ear_w]
    pts[137] = [-21.075, 0.0]
    pts[138] = [-21.075, half_ear_w]
    pts[139] = [-19.081, half_ear_w]
    
    # 2. Top Tab (indices 189..192)
    # Original:
    # 189: [-4.530, 18.504]
    # 190: [-4.530, 20.008]
    # 191: [ 3.690, 20.008]
    # 192: [ 3.690, 18.504]
    pts[189] = [-half_x, 18.504]
    pts[190] = [-half_x, 20.008]
    pts[191] = [half_x, 20.008]
    pts[192] = [half_x, 18.504]
    
    # 3. Bottom notch
    for idx, (x, y) in enumerate(pts):
        if abs(y - (-18.539)) < 0.05:
            if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
                pts[idx] = [2.50, -18.539]
            elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
                pts[idx] = [-2.50, -18.539]
        elif abs(y - (-16.650)) < 0.05:
            if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
                pts[idx] = [2.50, -16.650]
            elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
                pts[idx] = [-2.50, -16.650]
                
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly

poly_orig = get_exact_base_polygon()[1]
poly_tab_820 = build_poly_with_top_tab(8.20)
poly_tab_823 = build_poly_with_top_tab(8.23)

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=160)

# Panel 1: Original vs Centered 8.20mm
axes[0].plot(*poly_orig.exterior.xy, 'k--', label='Original (Left X=-4.53, Right X=+3.69)')
axes[0].plot(*poly_tab_820.exterior.xy, 'b-o', markersize=3, label='Centered 8.20mm (X = ±4.10mm)')
axes[0].plot(*poly_tab_820.buffer(-OUTER_WALL_THICK).exterior.xy, 'r:', label='Inner Wall Face (1.2mm)')
axes[0].axvline(-8.33/2.0, color='orange', linestyle='--', label='8.33mm Gap Bound (X = ±4.165mm)')
axes[0].axvline(8.33/2.0, color='orange', linestyle='--')
axes[0].axvline(-4.10, color='green', linestyle=':', label='Tab Outer Face (X = ±4.10mm)')
axes[0].axvline(4.10, color='green', linestyle=':')

axes[0].set_xlim(-7, 7)
axes[0].set_ylim(16, 21.5)
axes[0].set_aspect('equal')
axes[0].grid(True)
axes[0].set_title('Top Tab: Centered 8.20mm Width (0.13mm Clearance for 8.33mm Gap)', fontsize=11, fontweight='bold')
axes[0].legend(loc='lower center')

# Panel 2: Full Perimeter Overview
axes[1].plot(*poly_tab_820.exterior.xy, 'b-', label='Outer Body (Ears 8.20mm, Tab 8.20mm, Arch 5.00mm)')
axes[1].plot(*poly_tab_820.buffer(-OUTER_WALL_THICK).exterior.xy, 'r--', label='Inner Wall (1.2mm)')
axes[1].set_xlim(-25, 25)
axes[1].set_ylim(-22, 23)
axes[1].set_aspect('equal')
axes[1].grid(True)
axes[1].set_title('Complete Perimeter Overview', fontsize=11, fontweight='bold')
axes[1].legend(loc='lower left')

plt.tight_layout()
plt.savefig('testing/top_tab_833_gap_test.png', dpi=160)
print("Saved testing/top_tab_833_gap_test.png")
