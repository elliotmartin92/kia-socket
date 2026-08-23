import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, get_exact_base_polygon, OUTER_WALL_THICK
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

def build_ear_poly(ear_w):
    half_w = ear_w / 2.0
    pts = outer_pts.copy()
    
    # 1. Right Ear:
    pts[0] = [18.206, half_w]
    pts[1] = [20.200, half_w]
    pts[2] = [20.200, 0.0]
    pts[3] = [20.200, -half_w]
    pts[4] = [18.206, -half_w]
    if len(pts) > 242:
        pts[242] = [18.206, half_w]
        pts[243] = [18.206, half_w]
        
    # 2. Left Ear:
    pts[111] = [-19.081, -half_w]
    for k in range(112, 136):
        pts[k] = [-21.075, -half_w]
    pts[136] = [-21.075, -half_w]
    pts[137] = [-21.075, 0.0]
    pts[138] = [-21.075, half_w]
    pts[139] = [-19.081, half_w]
    
    # Bottom notch alignment
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

poly_orig = build_ear_poly(8.884)
poly_830 = build_ear_poly(8.30)
poly_820 = build_ear_poly(8.20)

fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=160)

# Left Ear
axes[0, 0].plot(*poly_orig.exterior.xy, 'k--', label='Original 8.88mm')
axes[0, 0].plot(*poly_830.exterior.xy, 'b-o', markersize=3, label='8.30mm Nominal')
axes[0, 0].plot(*poly_830.buffer(-OUTER_WALL_THICK).exterior.xy, 'r:', label='Inner Wall Face (1.2mm)')
axes[0, 0].axhline(4.15, color='green', linestyle='--', label='Y = +4.15mm')
axes[0, 0].axhline(-4.15, color='green', linestyle='--', label='Y = -4.15mm')
axes[0, 0].set_xlim(-22.5, -17.5)
axes[0, 0].set_ylim(-6.0, 6.0)
axes[0, 0].set_aspect('equal')
axes[0, 0].grid(True)
axes[0, 0].set_title('Left Ear: 8.30mm Nominal Width', fontsize=12, fontweight='bold')
axes[0, 0].legend()

# Right Ear
axes[0, 1].plot(*poly_orig.exterior.xy, 'k--', label='Original 8.88mm')
axes[0, 1].plot(*poly_830.exterior.xy, 'b-o', markersize=3, label='8.30mm Nominal')
axes[0, 1].plot(*poly_830.buffer(-OUTER_WALL_THICK).exterior.xy, 'r:', label='Inner Wall Face (1.2mm)')
axes[0, 1].axhline(4.15, color='green', linestyle='--', label='Y = +4.15mm')
axes[0, 1].axhline(-4.15, color='green', linestyle='--', label='Y = -4.15mm')
axes[0, 1].set_xlim(17.5, 21.5)
axes[0, 1].set_ylim(-6.0, 6.0)
axes[0, 1].set_aspect('equal')
axes[0, 1].grid(True)
axes[0, 1].set_title('Right Ear: 8.30mm Nominal Width', fontsize=12, fontweight='bold')
axes[0, 1].legend()

# Left Ear 8.20mm (with 0.10mm clearance for 8.30mm gap)
axes[1, 0].plot(*poly_orig.exterior.xy, 'k--', label='Original 8.88mm')
axes[1, 0].plot(*poly_820.exterior.xy, 'b-o', markersize=3, label='8.20mm (0.10mm clearance)')
axes[1, 0].plot(*poly_820.buffer(-OUTER_WALL_THICK).exterior.xy, 'r:', label='Inner Wall Face (1.2mm)')
axes[1, 0].axhline(4.15, color='orange', linestyle=':', label='8.30mm Mating Gap')
axes[1, 0].axhline(-4.15, color='orange', linestyle=':', label='8.30mm Mating Gap')
axes[1, 0].axhline(4.10, color='green', linestyle='--', label='Y = +4.10mm (Ear Wall)')
axes[1, 0].axhline(-4.10, color='green', linestyle='--', label='Y = -4.10mm (Ear Wall)')
axes[1, 0].set_xlim(-22.5, -17.5)
axes[1, 0].set_ylim(-6.0, 6.0)
axes[1, 0].set_aspect('equal')
axes[1, 0].grid(True)
axes[1, 0].set_title('Left Ear: 8.20mm Width (0.10mm Clearance into 8.30mm Gap)', fontsize=12, fontweight='bold')
axes[1, 0].legend()

# Right Ear 8.20mm
axes[1, 1].plot(*poly_orig.exterior.xy, 'k--', label='Original 8.88mm')
axes[1, 1].plot(*poly_820.exterior.xy, 'b-o', markersize=3, label='8.20mm (0.10mm clearance)')
axes[1, 1].plot(*poly_820.buffer(-OUTER_WALL_THICK).exterior.xy, 'r:', label='Inner Wall Face (1.2mm)')
axes[1, 1].axhline(4.15, color='orange', linestyle=':', label='8.30mm Mating Gap')
axes[1, 1].axhline(-4.15, color='orange', linestyle=':', label='8.30mm Mating Gap')
axes[1, 1].axhline(4.10, color='green', linestyle='--', label='Y = +4.10mm (Ear Wall)')
axes[1, 1].axhline(-4.10, color='green', linestyle='--', label='Y = -4.10mm (Ear Wall)')
axes[1, 1].set_xlim(17.5, 21.5)
axes[1, 1].set_ylim(-6.0, 6.0)
axes[1, 1].set_aspect('equal')
axes[1, 1].grid(True)
axes[1, 1].set_title('Right Ear: 8.20mm Width (0.10mm Clearance into 8.30mm Gap)', fontsize=12, fontweight='bold')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('testing/ear_comparison_830_vs_820.png', dpi=160)
print("Saved testing/ear_comparison_830_vs_820.png")
