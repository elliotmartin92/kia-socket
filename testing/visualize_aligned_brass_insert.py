"""
testing/visualize_aligned_brass_insert.py
Visualizes the brass insert seated in Bracket 3 & 4 such that its pinch throat
is directly in line with Bracket 4, the through-hole (X ~ 10.28mm), and the lever.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, PIN_LEN,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    X_TOWER_CENTER, HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    TOWER_HEIGHT, BASE_THICK
)
from testing.model_exact_brass_part import D1A, D1B, D2, D4, D5, D3, SHEET_THICK

def run():
    fig, axes = plt.subplots(1, 2, figsize=(20, 10), facecolor='#1a1a1a', dpi=180)
    
    # --------------------------------------------------------------------------
    # Panel 1: Top-Down Plan View (X-Y Plane)
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_facecolor('#222222')
    ax1.set_title("1. Top-Down Alignment: Brass Insert in Bracket 3/4 in line with Lever", color='white', fontsize=12, weight='bold')
    
    # Draw Brackets
    ax1.add_patch(patches.Polygon(bracket_3_raw_pts, facecolor='#27ae60', alpha=0.4, edgecolor='#2ecc71', lw=1.5, label='Bracket 3 (Left)'))
    ax1.add_patch(patches.Polygon(bracket_4_raw_pts, facecolor='#27ae60', alpha=0.4, edgecolor='#2ecc71', lw=1.5, label='Bracket 4 (Right)'))
    
    # Draw Towers
    ax1.add_patch(patches.Rectangle((X_LEFT_TOWER_OUTER, 6.25), X_LEFT_TOWER_INNER - X_LEFT_TOWER_OUTER, 6.60,
                                    facecolor='#3498db', alpha=0.3, edgecolor='#2980b9', lw=1.5, label='Left Tower'))
    ax1.add_patch(patches.Rectangle((X_RIGHT_TOWER_INNER, 6.25), X_RIGHT_TOWER_OUTER - X_RIGHT_TOWER_INNER, 6.60,
                                    facecolor='#3498db', alpha=0.3, edgecolor='#2980b9', lw=1.5, label='Right Tower'))
    
    # Draw Through Hole (X in [7.61, 12.96], Y in [8.57, 13.08])
    ax1.add_patch(patches.Rectangle((HOLE_X_CENTER - HOLE_X_WIDTH/2, HOLE_Y_CENTER - HOLE_Y_LEN/2),
                                    HOLE_X_WIDTH, HOLE_Y_LEN, facecolor='#e74c3c', alpha=0.35, edgecolor='#c0392b', lw=2, linestyle='--', label='Through-Hole Cutout'))
    
    # Draw Shaft Axle & Hub
    ax1.plot([X_TOWER_CENTER - TOTAL_AXLE_LEN/2, X_TOWER_CENTER + TOTAL_AXLE_LEN/2], [Y_AXLE, Y_AXLE], color='cyan', lw=3, label=f'Shaft Axle Axis (Y = {Y_AXLE:.2f}mm)')
    ax1.add_patch(patches.Rectangle((X_TOWER_CENTER - HUB_WIDTH/2, Y_AXLE - HUB_DIAMETER/2), HUB_WIDTH, HUB_DIAMETER,
                                    facecolor='#e67e22', alpha=0.4, edgecolor='#d35400', lw=1.5, label='Hub Barrel'))
    
    # Draw Lever / Plunger (centered at HOLE_X_CENTER = 10.284mm)
    ax1.add_patch(patches.Rectangle((HOLE_X_CENTER - PLUNGER_WIDTH_X/2, Y_AXLE - 1.0), PLUNGER_WIDTH_X, 3.5,
                                    facecolor='#f1c40f', alpha=0.7, edgecolor='#f39c12', lw=1.5, label='Plunger Arm (X = 10.28mm)'))
    
    # Position Brass Insert in Bracket 3/4
    # The brass insert retention tabs click into Bracket 3 (X=3.7mm) and Bracket 4 (X=8.85mm)
    # The pinch throat runs along X or Y in line with the through-hole and lever
    x_throat = (4.705 + 7.853) / 2.0  # 6.28mm or aligned with Bracket 4 / hole
    ax1.axvline(x_throat, color='#f39c12', linestyle='-.', lw=2, label=f'Blade / Pinch Axis (X = {x_throat:.2f}mm)')
    ax1.axvline(HOLE_X_CENTER, color='#f1c40f', linestyle=':', lw=2, label=f'Lever / Plunger Axis (X = {HOLE_X_CENTER:.2f}mm)')
    
    ax1.set_xlim(-1, 17)
    ax1.set_ylim(-10, 16)
    ax1.set_xlabel('X (mm)', color='white')
    ax1.set_ylabel('Y (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='lower left', fontsize=8, facecolor='#1a1a1a', labelcolor='white')
    
    # --------------------------------------------------------------------------
    # Panel 2: Side Alignment & Kinematic Action
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_facecolor('#222222')
    ax2.set_title("2. Physical Interaction: Plug Blade, Brass Pinch Throat, and Lever Cam", color='white', fontsize=12, weight='bold')
    
    ax2.add_patch(patches.Rectangle((-8, 0), 24, 1.0, facecolor='#888888', alpha=0.5, label='Baseplate Floor'))
    ax2.add_patch(patches.Rectangle((HOLE_Y_CENTER - HOLE_Y_LEN/2, 0), HOLE_Y_LEN, 1.0, facecolor='#e74c3c', alpha=0.4, hatch='//', label='Through-Hole'))
    
    # Draw Shaft Hub & Plunger
    ax2.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.5, edgecolor='#d35400', lw=1.5, label='Shaft Hub'))
    
    # Text explanation of physical orientation
    info_text = (
        "PHYSICAL ALIGNMENT IN BRACKET 3/4:\n\n"
        "1. BRACKET RETENTION:\n"
        "   - The brass stamping's retention ears click directly into\n"
        "     Bracket 3 (Left, X ~ 3.7mm) and Bracket 4 (Right, X ~ 8.8mm).\n"
        "   - Terminal pin extends through the floor slit into the PCB below.\n\n"
        "2. PINCH THROAT IN LINE WITH LEVER:\n"
        "   - The plug blade enters vertically through the pinch throat.\n"
        "   - The input cam on the rocker shaft directly engages the plug blade\n"
        "     in line with the lever and through-hole.\n\n"
        "3. WHAT NEEDS CLARIFICATION:\n"
        "   - In the side-on photo (brass_part_photo.jpeg):\n"
        "     Are the two formed spring leaves pinching the blade from:\n"
        "     [A] Front & Back (in the Y-direction)?\n"
        "     [B] Left & Right (in the X-direction)?"
    )
    ax2.text(0.05, 0.95, info_text, transform=ax2.transAxes, color='#ecf0f1', fontsize=9.5, fontfamily='monospace',
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e272e', edgecolor='#2ecc71', lw=1.5))
    
    ax2.set_xlim(-8, 16)
    ax2.set_ylim(-8, 18)
    ax2.set_xlabel('Y (mm)', color='white')
    ax2.set_ylabel('Z (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "aligned_brass_insert_study.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved aligned brass insert study to: {out_png}")

if __name__ == '__main__':
    run()
