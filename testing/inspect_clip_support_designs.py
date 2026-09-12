"""
testing/inspect_clip_support_designs.py
Investigate clip dimensions and support designs that support the edges better with equal contact area.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MplPoly

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_HOOK_DEPTH, CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT
)

print(f"Current CLIP_HOOK_DEPTH: {CLIP_HOOK_DEPTH:.2f} mm")
print(f"Current CLIP_ARM_WIDTH:  {CLIP_ARM_WIDTH:.2f} mm")

# If outer clips are ~0.1mm too large:
# If CLIP_HOOK_DEPTH reduced by 0.10mm: 2.59 -> 2.49 mm
# Or CLIP_ARM_WIDTH reduced by 0.10mm: 4.20 -> 4.10 mm
# Or both!

hook_depth_new = CLIP_HOOK_DEPTH - 0.10  # 2.49 mm
hook_width = CLIP_ARM_WIDTH             # 4.20 mm

print(f"Target hook_depth: {hook_depth_new:.2f} mm (-0.10 mm)")

# Analyze current support tip
# tip = box([0.50, 1.80, 0.12]) (radial: 0.50, tangential: 1.80)
curr_area = 0.50 * 1.80
print(f"Current contact area: {curr_area:.2f} mm² (radial 0.50mm x tang 1.80mm)")

# Plot comparison of support tip layouts on the hook shelf
fig, axs = plt.subplots(1, 3, figsize=(16, 5), dpi=180)

# Local coordinate system for hook shelf:
# X_local = radial distance from wall (0 to hook_depth)
# Y_local = tangential distance along wall (-hook_width/2 to +hook_width/2)

def draw_shelf(ax, title):
    # Shelf boundary
    ax.fill([0, hook_depth_new, hook_depth_new, 0],
            [-hook_width/2, -hook_width/2, hook_width/2, hook_width/2],
            color='#e3f2fd', ec='#1565c0', lw=2, label='Hook Shelf (Overhang)')
    # Wall attachment
    ax.plot([0, 0], [-hook_width/2 - 0.5, hook_width/2 + 0.5], 'k-', lw=3.5, label='Perimeter Wall (Root)')
    ax.set_xlim(-0.5, hook_depth_new + 0.8)
    ax.set_ylim(-hook_width/2 - 0.6, hook_width/2 + 0.6)
    ax.set_aspect('equal')
    ax.set_xlabel("Radial Distance from Wall (mm)", fontsize=9, fontweight='bold')
    ax.set_ylabel("Tangential Span (mm)", fontsize=9, fontweight='bold')
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)

# 1. Current Design
ax = axs[0]
draw_shelf(ax, "1. Current Center Chisel Tip\n(Area = 0.90 mm²)")
# Current tip is at radial = hook_depth * 0.50, width 1.80, radial 0.50
c_rad = hook_depth_new * 0.50
rect_curr = Rectangle((c_rad - 0.25, -0.90), 0.50, 1.80,
                      facecolor='#e53935', edgecolor='#b71c1c', lw=1.5,
                      label=f'Contact Tip (0.50 x 1.80 = {0.5*1.8:.2f} mm²)')
ax.add_patch(rect_curr)
# Annotate unsupported edges
ax.annotate('Unsupported edge!\n(1.20mm span)', xy=(c_rad, 1.5), xytext=(c_rad + 0.3, 1.8),
            arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.2),
            fontsize=8, color='#b71c1c', fontweight='bold')
ax.annotate('Unsupported edge!\n(1.20mm span)', xy=(c_rad, -1.5), xytext=(c_rad + 0.3, -2.2),
            arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.2),
            fontsize=8, color='#b71c1c', fontweight='bold')
ax.annotate('Unsupported outer rim!\n(1.00mm overhang)', xy=(hook_depth_new, 0), xytext=(hook_depth_new - 0.4, 0.4),
            arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.2),
            fontsize=8, color='#b71c1c', fontweight='bold')
ax.legend(loc='lower left', fontsize=7.5)

# 2. Design A: Twin Lateral Edge Pads
ax = axs[1]
draw_shelf(ax, "2. Twin Lateral Edge Pads\n(Area = 2 x 0.45 = 0.90 mm²)")
# Two pads at edges:
# Tangential: centered at ±1.45mm, width = 0.90mm (covers from ±1.00 to ±1.90mm, leaving 0.20mm to outer edge)
# Radial: centered at hook_depth * 0.60, radial depth = 0.50mm
rad_pos_a = hook_depth_new * 0.60
rect_a1 = Rectangle((rad_pos_a - 0.25, 1.00), 0.50, 0.90,
                    facecolor='#2e7d32', edgecolor='#1b5e20', lw=1.5,
                    label=f'Twin Edge Pads\n(2x 0.50x0.90 = {2*0.5*0.9:.2f} mm²)')
rect_a2 = Rectangle((rad_pos_a - 0.25, -1.90), 0.50, 0.90,
                    facecolor='#2e7d32', edgecolor='#1b5e20', lw=1.5)
ax.add_patch(rect_a1)
ax.add_patch(rect_a2)
ax.annotate('2.0mm bridged span\n(no droop)', xy=(rad_pos_a, 0), xytext=(rad_pos_a - 0.8, -0.2),
            arrowprops=dict(arrowstyle='<->', color='#2e7d32', lw=1.2),
            fontsize=8, color='#1b5e20', fontweight='bold')
ax.annotate('Directly supports\nlateral corners!', xy=(rad_pos_a + 0.25, 1.45), xytext=(rad_pos_a + 0.4, 1.8),
            arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.2),
            fontsize=8, color='#1b5e20', fontweight='bold')
ax.legend(loc='lower left', fontsize=7.5)

# 3. Design B: Tri-Point Perimeter Tripod (2 Edges + 1 Outer Front Lip)
ax = axs[2]
draw_shelf(ax, "3. Tri-Point Perimeter Tripod\n(Area = 3 x 0.30 = 0.90 mm²)")
# 3 small pads:
# Left edge: (rad=1.35, tang=1.45), 0.50 radial x 0.60 tang = 0.30 mm²
# Right edge: (rad=1.35, tang=-1.45), 0.50 radial x 0.60 tang = 0.30 mm²
# Outer center lip: (rad=hook_depth - 0.45, tang=0.0), 0.40 radial x 0.75 tang = 0.30 mm²
rad_pos_side = hook_depth_new * 0.55
rect_b1 = Rectangle((rad_pos_side - 0.25, 1.15), 0.50, 0.60,
                    facecolor='#0288d1', edgecolor='#01579b', lw=1.5,
                    label=f'Tri-Point Tripod\n(3x ~0.30 = {2*0.5*0.6 + 0.4*0.75:.2f} mm²)')
rect_b2 = Rectangle((rad_pos_side - 0.25, -1.75), 0.50, 0.60,
                    facecolor='#0288d1', edgecolor='#01579b', lw=1.5)
rad_pos_front = hook_depth_new - 0.45
rect_b3 = Rectangle((rad_pos_front - 0.20, -0.375), 0.40, 0.75,
                    facecolor='#0288d1', edgecolor='#01579b', lw=1.5)
ax.add_patch(rect_b1)
ax.add_patch(rect_b2)
ax.add_patch(rect_b3)

ax.annotate('Supports outer lip!', xy=(rad_pos_front + 0.2, 0), xytext=(rad_pos_front + 0.2, 0.8),
            arrowprops=dict(arrowstyle='->', color='#0288d1', lw=1.2),
            fontsize=8, color='#01579b', fontweight='bold')
ax.annotate('Supports left edge', xy=(rad_pos_side, 1.45), xytext=(rad_pos_side - 0.9, 1.8),
            arrowprops=dict(arrowstyle='->', color='#0288d1', lw=1.2),
            fontsize=8, color='#01579b', fontweight='bold')
ax.legend(loc='lower left', fontsize=7.5)

plt.tight_layout()
out_png = 'testing/clip_support_design_comparison.png'
plt.savefig(out_png, dpi=180)
print(f"Saved comparison to {out_png}")
