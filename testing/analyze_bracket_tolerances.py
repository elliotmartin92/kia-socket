"""
testing/analyze_bracket_tolerances.py
Visualizes the bracket interior geometry and tests looser tolerance adjustments.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, BASE_THICK, BRACKET_HEIGHT
)

# Caliper dimensions of the brass part:
# Width of flat base strip: D3 = 6.74 mm
# Spring blade height/reach
# Brass sheet thickness: 0.50 mm

def plot_bracket_tolerances():
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)

    # -------------------------------------------------------------
    # Left Pair: Bracket 1 & Bracket 2
    # -------------------------------------------------------------
    ax1 = axes[0]
    p1 = Polygon(bracket_1_raw_pts)
    p2 = Polygon(bracket_2_raw_pts)

    ax1.plot(*p1.exterior.xy, 'b-o', lw=2, label='Current Bracket 1 (Left Outer)')
    ax1.plot(*p2.exterior.xy, 'g-o', lw=2, label='Current Bracket 2 (Left Inner)')

    # Add dimensions & annotations
    # Spine walls: B1 X=-9.707, B2 X=-2.851
    # Width = 6.856 mm
    ax1.annotate('', xy=(-9.707, 0), xytext=(-2.851, 0),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax1.text((-9.707 + -2.851)/2, 0.4, f'Spine Channel Width:\n6.856 mm (Clearance: +0.12mm)',
             ha='center', va='bottom', color='purple', fontweight='bold', fontsize=9)

    # Top Hook Entrance: B1 X=-7.853, B2 X=-4.670
    ax1.annotate('', xy=(-7.853, 4.8), xytext=(-4.670, 4.8),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax1.text((-7.853 + -4.670)/2, 5.0, f'Top Entrance: 3.183 mm',
             ha='center', va='bottom', color='red', fontweight='bold', fontsize=8.5)

    # Bottom Step Entrance: B1 X=-7.993, B2 X=-4.530
    ax1.annotate('', xy=(-7.993, -6.08), xytext=(-4.530, -6.08),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax1.text((-7.993 + -4.530)/2, -5.8, f'Bottom Entrance: 3.463 mm',
             ha='center', va='bottom', color='red', fontweight='bold', fontsize=8.5)

    # Pocket depth in Y: from 4.80 to 6.25 = 1.45 mm
    ax1.annotate('', xy=(-9.2, 4.8), xytext=(-9.2, 6.25),
                 arrowprops=dict(arrowstyle='<->', color='darkgreen', lw=1.5))
    ax1.text(-9.3, 5.5, 'Pocket:\n1.45mm', ha='right', va='center', color='darkgreen', fontsize=8)

    # Vertical span in Y: from -6.086 to 6.250 = 12.336 mm
    ax1.annotate('', xy=(-6.28, -6.086), xytext=(-6.28, 6.250),
                 arrowprops=dict(arrowstyle='<->', color='navy', lw=1.5))
    ax1.text(-6.1, 0, 'Internal Y Span:\n12.34 mm', ha='left', va='center', color='navy', fontsize=8.5)

    ax1.set_xlim(-12, 0)
    ax1.set_ylim(-8.5, 8.5)
    ax1.set_aspect('equal')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.set_title('Left Bracket Pair (Brackets 1 & 2)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.legend(loc='lower left', fontsize=9)

    # -------------------------------------------------------------
    # Right Pair: Bracket 3 & Bracket 4
    # -------------------------------------------------------------
    ax2 = axes[1]
    p3 = Polygon(bracket_3_raw_pts)
    p4 = Polygon(bracket_4_raw_pts)

    ax2.plot(*p3.exterior.xy, 'g-o', lw=2, label='Current Bracket 3 (Right Inner)')
    ax2.plot(*p4.exterior.xy, 'b-o', lw=2, label='Current Bracket 4 (Right Outer)')

    # Add dimensions & annotations
    # Spine walls: B3 X=2.851, B4 X=9.707
    ax2.annotate('', xy=(2.851, 0), xytext=(9.707, 0),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax2.text((2.851 + 9.707)/2, 0.4, f'Spine Channel Width:\n6.856 mm (Clearance: +0.12mm)',
             ha='center', va='bottom', color='purple', fontweight='bold', fontsize=9)

    # Top Hook Entrance: B3 X=4.705, B4 X=7.853
    ax2.annotate('', xy=(4.705, 4.8), xytext=(7.853, 4.8),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax2.text((4.705 + 7.853)/2, 5.0, f'Top Entrance: 3.148 mm',
             ha='center', va='bottom', color='red', fontweight='bold', fontsize=8.5)

    # Bottom Step Entrance: B3 X=4.565, B4 X=8.028
    ax2.annotate('', xy=(4.565, -6.08), xytext=(8.028, -6.08),
                 arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax2.text((4.565 + 8.028)/2, -5.8, f'Bottom Entrance: 3.463 mm',
             ha='center', va='bottom', color='red', fontweight='bold', fontsize=8.5)

    # Pocket depth in Y: from 4.80 to 6.25 = 1.45 mm
    ax2.annotate('', xy=(3.3, 4.8), xytext=(3.3, 6.25),
                 arrowprops=dict(arrowstyle='<->', color='darkgreen', lw=1.5))
    ax2.text(3.4, 5.5, 'Pocket:\n1.45mm', ha='left', va='center', color='darkgreen', fontsize=8)

    # Vertical span in Y: from -6.086 to 6.250 = 12.336 mm
    ax2.annotate('', xy=(6.28, -6.086), xytext=(6.28, 6.250),
                 arrowprops=dict(arrowstyle='<->', color='navy', lw=1.5))
    ax2.text(6.4, 0, 'Internal Y Span:\n12.34 mm', ha='left', va='center', color='navy', fontsize=8.5)

    ax2.set_xlim(0, 12)
    ax2.set_ylim(-8.5, 8.5)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.set_title('Right Bracket Pair (Brackets 3 & 4)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.legend(loc='lower right', fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'bracket_current_dimensions.png')
    plt.savefig(out_path, dpi=180)
    print(f"Saved {out_path}")

if __name__ == '__main__':
    plot_bracket_tolerances()
