"""
testing/analyze_curved_feature_reinforcement.py
Detailed analysis of the center curved feature geometry, clearance to the plug blade,
clearance to the OEM brass insert, and proposed structural reinforcements.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    create_bracket_seating_ribs_poly, BRACKET_SEATING_RIB_Y,
    create_center_curved_feature_poly, BASE_THICK
)

def poly_moments(poly):
    pts = np.array(poly.exterior.coords)
    x = pts[:, 0]
    y = pts[:, 1]
    a = 0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])
    cx = np.sum((x[:-1] + x[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1])) / (6 * a)
    cy = np.sum((y[:-1] + y[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1])) / (6 * a)
    xs = x - cx
    ys = y - cy
    ixx = np.sum((ys[:-1]**2 + ys[:-1]*ys[1:] + ys[1:]**2) * (xs[:-1] * ys[1:] - xs[1:] * ys[:-1])) / 12.0
    iyy = np.sum((xs[:-1]**2 + xs[:-1]*xs[1:] + xs[1:]**2) * (xs[:-1] * ys[1:] - xs[1:] * ys[:-1])) / 12.0
    for interior in poly.interiors:
        ipts = np.array(interior.coords)
        ix = ipts[:, 0]
        iy = ipts[:, 1]
        ia = 0.5 * np.sum(ix[:-1] * iy[1:] - ix[1:] * iy[:-1])
        icx = np.sum((ix[:-1] + ix[1:]) * (ix[:-1] * iy[1:] - ix[1:] * iy[:-1])) / (6 * ia)
        icy = np.sum((iy[:-1] + iy[1:]) * (ix[:-1] * iy[1:] - ix[1:] * iy[:-1])) / (6 * ia)
        ixs = ix - cx
        iys = iy - cy
        ixx -= np.sum((iys[:-1]**2 + iys[:-1]*iys[1:] + iys[1:]**2) * (ixs[:-1] * iys[1:] - ixs[1:] * iys[:-1])) / 12.0
        iyy -= np.sum((ixs[:-1]**2 + ixs[:-1]*ixs[1:] + ixs[1:]**2) * (ixs[:-1] * iys[1:] - ixs[1:] * iys[:-1])) / 12.0
        a -= ia
    return abs(a), (cx, cy), abs(ixx), abs(iyy)

def analyze():
    b3 = to_mm_poly(bracket_3_raw_pts)
    b4 = to_mm_poly(bracket_4_raw_pts)
    curved_current = create_center_curved_feature_poly()
    ribs = create_bracket_seating_ribs_poly()

    cx = 6.279
    w_x = 4.30
    h_y = 1.62
    rx = w_x / 2.0
    ry = h_y
    base_y = -4.069

    # 1. Hot blade bounds:
    # NEMA 5-15 hot blade: width 6.35 mm in Y, thickness 1.52 mm in X, center at (6.279, 2.890)
    blade_x_min = 6.279 - 1.52/2.0  # 5.519 mm
    blade_x_max = 6.279 + 1.52/2.0  # 7.039 mm
    blade_y_min = 2.890 - 6.35/2.0  # -0.285 mm
    blade_y_max = 2.890 + 6.35/2.0  # +6.065 mm

    # 2. Brass insert location from photo and bracket seating:
    # Stamped brass insert rests on seating ribs (Rib 1 at Y=5.25, Rib 2 at Y=1.95, Rib 3 at Y=-1.35, Rib 4 at Y=-4.65)
    # The horizontal bridge rests across Rib 4: Y in [-6.00, -4.65] mm.
    # The two side legs go up to the pinching jaws.
    # Pinching jaws: Y in [-1.5, +5.5] mm, X in [3.5, 4.7] (left) and [7.85, 9.05] (right).
    # Inner opening between brass leaves/legs: X in [4.7, 7.85] mm (width = 3.15 mm).
    # Wait, in the photo, the bridge has a U-shaped pocket.
    # Top edge of horizontal brass bridge is at Y ≈ -4.65 mm (top of Rib 4 is at Y = -4.35 mm).

    print("=== GEOMETRIC CLEARANCES ===")
    print(f"Hot Blade Y: [{blade_y_min:.3f}, {blade_y_max:.3f}] mm")
    print(f"Curved Feature Apex Y: {base_y + ry:.3f} mm")
    print(f"Nominal Air Gap (Blade to Curved Feature Apex): {blade_y_min - (base_y + ry):.3f} mm")
    print(f"Curved Feature Base Y: {base_y:.3f} mm")
    print(f"Seating Rib 4 Top Y: {-4.65 + 0.30:.3f} mm")
    print(f"Gap from Curved Feature Base to Rib 4: {base_y - (-4.65 + 0.30):.3f} mm")

    # Options for reinforcing the bottom of the curved feature:
    angles = np.linspace(np.pi, 0, 32)
    out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]

    # Option A: Solid D-shape (flat bottom at base_y = -4.069 mm)
    # Fills the entire hollow interior solid.
    poly_opt_a = Polygon(out_arc + [(cx - rx, base_y)])

    # Option B: Solid with extended flat bottom in -Y (down to Y = -4.35 mm, meeting Rib 4 top)
    # Extends the side legs straight down from base_y (-4.069) to Y = -4.35 mm (0.281 mm extension)
    y_ext_b = -4.350
    poly_opt_b = Polygon([(cx - rx, y_ext_b), (cx - rx, base_y)] + out_arc + [(cx + rx, base_y), (cx + rx, y_ext_b)])

    # Option C: Solid with thickened bottom wall / gusseted back
    # Extends straight down to Y = -4.30 mm (leaving 0.05mm clearance to Rib 4 / brass bridge)
    y_ext_c = -4.300
    poly_opt_c = Polygon([(cx - rx, y_ext_c), (cx - rx, base_y)] + out_arc + [(cx + rx, base_y), (cx + rx, y_ext_c)])

    # Option D: Solid D-shape + Base draft/fillet in 3D (Z-axis flare at floor)
    # At floor Z = 1.0 mm, flare outward by +0.8 mm in -Y and +0.4 mm in X, tapering to nominal at Z = 3.0 mm.

    print("\n=== SECTION PROPERTIES & STRENGTH COMPARISON ===")
    for name, p in [
        ("Current Hollow 0.6mm Arc", curved_current),
        ("Option A: Solid D-Shape (Flat Base at Y=-4.07)", poly_opt_a),
        ("Option B: Solid Extended to Y=-4.35 (Flush with Rib 4)", poly_opt_b),
        ("Option C: Solid Extended to Y=-4.30 (0.05mm from Rib 4)", poly_opt_c),
    ]:
        area, cent, ixx, iyy = poly_moments(p)
        print(f"{name}:")
        print(f"  Area: {area:.3f} mm^2 (rel: {area/poly_moments(curved_current)[0]:.2f}x)")
        print(f"  Ixx (Bending about X / Y-flexure): {ixx:.4f} mm^4 (rel: {ixx/poly_moments(curved_current)[2]:.2f}x)")
        print(f"  Iyy (Bending about Y / X-flexure): {iyy:.4f} mm^4 (rel: {iyy/poly_moments(curved_current)[3]:.2f}x)")

    # Plot comparison diagram
    fig, axes = plt.subplots(1, 3, figsize=(21, 8), dpi=180)

    # Common background elements:
    # Bracket 3, Bracket 4, Seating ribs, Blade, Brass Insert
    def draw_surroundings(ax, title):
        ax.plot(*b3.exterior.xy, color='#2e7d32', lw=2, label='Bracket 3')
        ax.plot(*b4.exterior.xy, color='#1565c0', lw=2, label='Bracket 4')
        ax.fill(*b3.exterior.xy, color='#e8f5e9', alpha=0.3)
        ax.fill(*b4.exterior.xy, color='#e3f2fd', alpha=0.3)

        # Seating ribs (Rib 4 at Y = -4.65)
        for geom in (ribs.geoms if hasattr(ribs, 'geoms') else [ribs]):
            gx, gy = geom.exterior.xy
            if min(gx) > 0 and max(gy) < -3.0: # Rib 4
                ax.fill(gx, gy, color='#c8e6c9', edgecolor='#4caf50', lw=1.2, ls=':')
        ax.plot([], [], color='#4caf50', lw=1.5, ls=':', label='Seating Rib 4 (Y=-4.65)')

        # Brass insert (bridge across Rib 4)
        # Bridge: Y in [-5.85, -4.65], X in [3.70, 8.85]
        # Left leg/jaw: X in [3.70, 4.70], Y in [-4.65, 5.50]
        # Right leg/jaw: X in [7.85, 8.85], Y in [-4.65, 5.50]
        brass_bridge = patches.Rectangle((3.70, -5.85), 5.15, 1.20,
                                         facecolor='#ffd54f', alpha=0.5, edgecolor='#f57f17', lw=1.8, label='Brass Insert Bridge')
        brass_left_jaw = patches.Rectangle((3.70, -4.65), 1.00, 7.00,
                                           facecolor='#ffe082', alpha=0.4, edgecolor='#f57f17', lw=1.2, ls='--')
        brass_right_jaw = patches.Rectangle((7.85, -4.65), 1.00, 7.00,
                                            facecolor='#ffe082', alpha=0.4, edgecolor='#f57f17', lw=1.2, ls='--', label='Brass Insert Jaws')
        ax.add_patch(brass_bridge)
        ax.add_patch(brass_left_jaw)
        ax.add_patch(brass_right_jaw)

        # Hot Blade
        blade_box = patches.Rectangle((blade_x_min, blade_y_min), blade_x_max - blade_x_min, blade_y_max - blade_y_min,
                                      facecolor='#42a5f5', alpha=0.35, edgecolor='#1976d2', lw=1.8, label='Plug Blade (1.52x6.35mm)')
        ax.add_patch(blade_box)

        ax.set_xlim(1.5, 11.0)
        ax.set_ylim(-7.5, 1.5)
        ax.set_aspect('equal')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_xlabel('X (mm)', fontweight='bold')
        ax.set_ylabel('Y (mm)', fontweight='bold')
        ax.set_title(title, fontsize=11, fontweight='bold')

    # Panel 1: Current vs Option A (Solid D-shape at base_y = -4.07)
    draw_surroundings(axes[0], "Current Hollow vs Option A (Solid D-Shape)")
    for geom in (curved_current.geoms if hasattr(curved_current, 'geoms') else [curved_current]):
        axes[0].plot(*geom.exterior.xy, color='#d32f2f', lw=2, ls='--', label='Current Hollow Arc (0.6mm wall)')
    axes[0].fill(*poly_opt_a.exterior.xy, color='#ba68c8', alpha=0.6, edgecolor='#6a1b9a', lw=2, label='Option A: Solid D-Shape')
    axes[0].legend(loc='upper right', fontsize=7.5)

    # Panel 2: Option B (Solid Extended to Y = -4.35, Meeting Rib 4)
    draw_surroundings(axes[1], "Option B: Solid Extended to Y = -4.35mm")
    axes[1].fill(*poly_opt_b.exterior.xy, color='#ab47bc', alpha=0.6, edgecolor='#4a148c', lw=2, label='Option B: Extended to Y=-4.35')
    axes[1].plot(*poly_opt_a.exterior.xy, color='gray', lw=1, ls=':', label='Option A Boundary')
    axes[1].legend(loc='upper right', fontsize=7.5)

    # Panel 3: Option C (Solid with 0.20mm extension to Y = -4.27mm, 0.38mm Brass Gap)
    y_ext_c = -4.250
    poly_opt_c = Polygon([(cx - rx, y_ext_c), (cx - rx, base_y)] + out_arc + [(cx + rx, base_y), (cx + rx, y_ext_c)])
    draw_surroundings(axes[2], "Option C: Solid with +0.18mm Base Extension (Y=-4.25mm)")
    axes[2].fill(*poly_opt_c.exterior.xy, color='#7b1fa2', alpha=0.6, edgecolor='#4a148c', lw=2, label='Option C: Extended Base (Y=-4.25)')
    axes[2].legend(loc='upper right', fontsize=7.5)

    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), 'curved_feature_reinforcement_options.png')
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved comparison plot to {out_png}")

if __name__ == '__main__':
    analyze()
