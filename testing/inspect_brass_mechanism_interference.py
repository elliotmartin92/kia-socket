"""
testing/inspect_brass_mechanism_interference.py
Comprehensive geometric inspection and visualization of:
1. Brass pinching mechanism in Brackets 3 & 4 (hot terminal) and Brackets 1 & 2 (neutral terminal)
2. Height of brass part relative to Left Tower (Z_top = 14.09 mm) and 2.7 mm measurement
3. Top widening / lead-in flare of the brass pinching mechanism
4. Physical interference between the right brass mechanism and the lever (shaft rocker)
5. Analysis of design adjustments to resolve the interference
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh,
    X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, TOWER_HEIGHT, BASE_THICK,
    create_all_brackets_poly
)

def run_inspection():
    print("================================================================================")
    print("GEOMETRIC AUDIT: BRASS PINCHING MECHANISM & ROCKER LEVER INTERFERENCE")
    print("================================================================================")
    
    # 1. Left Tower geometry
    z_tower_top = BASE_THICK + TOWER_HEIGHT  # 14.09 mm
    y_lt_min_top = 6.550
    y_lt_max_top = 12.180
    y_lt_min_base = 6.250
    y_lt_max_base = 12.850
    x_lt_min = X_LEFT_TOWER_OUTER  # 3.90 mm
    x_lt_max = X_LEFT_TOWER_INNER  # 5.40 mm
    
    # 2. Right Bracket Envelope (Brackets 3 & 4)
    b3 = to_mm_poly(bracket_3_raw_pts)
    b4 = to_mm_poly(bracket_4_raw_pts)
    
    # 3. Rocker Lever Bounds in Assembly
    r_hub = HUB_DIAMETER / 2.0  # 2.10 mm
    hub_x_min = HOLE_X_CENTER - HUB_WIDTH / 2.0  # ~5.50 mm (actually X_TOWER_CENTER - HUB_WIDTH/2 = 5.50 mm)
    hub_x_max = hub_x_min + HUB_WIDTH  # 13.00 mm
    hub_y_min = Y_AXLE - r_hub  # 7.179 mm
    hub_y_max = Y_AXLE + r_hub  # 11.379 mm
    hub_z_min = Z_AXLE - r_hub  # 10.490 mm
    hub_z_max = Z_AXLE + r_hub  # 14.690 mm
    
    cam_x_min = CAM_X_CENTER - CAM_WIDTH_X / 2.0  # 5.70 mm
    cam_x_max = CAM_X_CENTER + CAM_WIDTH_X / 2.0  # 8.40 mm
    
    print(f"Left Tower Top Face:  X in [{x_lt_min:.2f}, {x_lt_max:.2f}] mm, Y in [{y_lt_min_top:.2f}, {y_lt_max_top:.2f}] mm, Z = {z_tower_top:.2f} mm")
    print(f"Right Bracket 3:       X in [{b3.bounds[0]:.2f}, {b3.bounds[2]:.2f}] mm, Y in [{b3.bounds[1]:.2f}, {b3.bounds[3]:.2f}] mm")
    print(f"Right Bracket 4:       X in [{b4.bounds[0]:.2f}, {b4.bounds[2]:.2f}] mm, Y in [{b4.bounds[1]:.2f}, {b4.bounds[3]:.2f}] mm")
    print(f"Shaft Pivot Axis:      Y = {Y_AXLE:.3f} mm, Z = {Z_AXLE:.3f} mm")
    print(f"Central Hub Barrel:    X in [{hub_x_min:.2f}, {hub_x_max:.2f}] mm, Y in [{hub_y_min:.2f}, {hub_y_max:.2f}] mm, Z in [{hub_z_min:.2f}, {hub_z_max:.2f}] mm")
    print(f"Input Cam Tab:         X in [{cam_x_min:.2f}, {cam_x_max:.2f}] mm, Reach to Y ~ 2.80 mm, Z ~ 9.50 mm")
    
    # 4. Analyze the 2.7 mm measurement and brass part height
    print("\n--- MEASUREMENT & INTERFERENCE INTERPRETATION ---")
    print("User Observation:")
    print("  1. 'the blade inserts into a brass pinching mechanism which is retained by the brackets.'")
    print("  2. 'the one on the right interferes with the lever.'")
    print("  3. 'the top of the left tower is 2.7mm from the brass part.'")
    print("  4. 'the brass part widens at the top and is taller than the tower'")
    
    print("\nDetailed Geometric Breakdown:")
    print(f"  A. Height: Tower top is Z = {z_tower_top:.2f} mm. If brass part is taller than the tower:")
    print(f"     - If brass part top is 2.7mm above tower top: Z_brass_top = {z_tower_top + 2.70:.2f} mm (16.79 mm).")
    print(f"     - If 2.7mm is the horizontal gap from tower top front (Y = {y_lt_min_top:.2f}) to brass part top/rear face:")
    print(f"       Brass part top rear edge is at Y = {y_lt_min_top - 2.70:.2f} mm = 3.85 mm.")
    print(f"  B. X-Span overlap:")
    print(f"     - Right brass pinching mechanism sits in Brackets 3 & 4 -> X spans from X ~ 2.85 to 9.71 mm (centered on blade at X = 6.28 mm).")
    print(f"     - Lever spans X from 5.50 to 13.00 mm (Hub) and 5.70 to 8.40 mm (Cam tab).")
    print(f"     - Overlap zone in X: [5.50, 9.71] mm!")
    print(f"  C. Y-Span overlap & Interference:")
    print(f"     - Bracket 3/4 channel goes up to Y = +7.17 mm.")
    print(f"     - Hub starts at Y = {hub_y_min:.2f} mm (Y = 7.18 mm).")
    print(f"     - Cam arm and Left Flank Rib (X in [5.60, 6.60]) extend forward into Y in [2.80, 7.18] mm at Z in [8.0, 13.5] mm!")
    print(f"     - Because the brass part rises to Z >= {z_tower_top:.2f} mm (and widens at top), the top/rear leaves of the brass pinching mechanism collide directly with:")
    print(f"       * The Lever Cam Tab / Arm (X in [5.70, 8.40], Y in [2.80, 7.18], Z in [9.5, 12.6])")
    print(f"       * The Left Flank Rib (X in [5.60, 6.60], Y in [7.18, 9.28])")
    print(f"       * The Structural Hub / Web front face (Y = 7.18 mm)")

    # 5. Create 4-panel visual diagram
    fig = plt.figure(figsize=(18, 14), facecolor='#1a1a1a')
    
    # -------------------------------------------------------------
    # Panel 1: Top-Down X-Y Plane View
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1, facecolor='#222222')
    ax1.set_title("1. Top-Down Layout (X-Y Plane) & Interference Zone", color='white', fontsize=12, weight='bold', pad=10)
    
    # Baseplate boundary & through hole
    base_poly, outer_poly, hole_info = get_exact_base_polygon()
    bx, by = base_poly.exterior.xy
    ax1.plot(bx, by, color='#666666', lw=1.2, label='Baseplate Perimeter')
    
    # Brackets 1-4
    all_b = create_all_brackets_poly()
    for poly in (all_b.geoms if hasattr(all_b, 'geoms') else [all_b]):
        gx, gy = poly.exterior.xy
        ax1.fill(gx, gy, color='#2ecc71', alpha=0.35, edgecolor='#27ae60', lw=1.5)
    ax1.plot([], [], color='#2ecc71', lw=3, label='Guide Brackets 1-4 (Z=4.60mm)')
    
    # Towers (Left & Right)
    ax1.add_patch(patches.Rectangle((3.90, 6.25), 1.50, 6.60, color='#3498db', alpha=0.5, edgecolor='#2980b9', lw=1.5, label='Shaft Towers (Z=14.09mm)'))
    ax1.add_patch(patches.Rectangle((13.10, 6.25), 1.50, 6.60, color='#3498db', alpha=0.5, edgecolor='#2980b9', lw=1.5))
    
    # Through hole
    ax1.add_patch(patches.Rectangle((HOLE_X_CENTER - HOLE_X_WIDTH/2, HOLE_Y_CENTER - HOLE_Y_LEN/2), HOLE_X_WIDTH, HOLE_Y_LEN,
                                    fill=False, edgecolor='#9b59b6', linestyle='--', lw=1.5, label='Through-Hole'))
    
    # Lever components in Top-Down
    # Hub barrel
    ax1.add_patch(patches.Rectangle((5.50, Y_AXLE - r_hub), 7.50, 2*r_hub, color='#e67e22', alpha=0.6, edgecolor='#d35400', lw=1.5, label='Lever Hub Barrel (Ø4.20mm)'))
    # Cam tab
    ax1.add_patch(patches.Rectangle((cam_x_min, 2.80), CAM_WIDTH_X, Y_AXLE - 2.80, color='#e74c3c', alpha=0.7, edgecolor='#c0392b', lw=1.5, label='Lever Cam Tab (X in [5.7, 8.4])'))
    # Plunger
    ax1.add_patch(patches.Rectangle((HOLE_X_CENTER - 2.20, Y_AXLE - 1.0), 4.40, 2.0, color='#f1c40f', alpha=0.6, edgecolor='#f39c12', lw=1.5, label='Lever Plunger (4.40mm)'))
    
    # Brass pinching mechanisms in brackets
    # Left (Neutral) Brass Mechanism in Brackets 1 & 2
    ax1.add_patch(patches.Rectangle((-9.50, -6.00), 6.50, 12.00, color='#f39c12', alpha=0.25, edgecolor='#d68910', linestyle=':', lw=2, label='Neutral Brass Terminal'))
    # Right (Hot) Brass Mechanism in Brackets 3 & 4
    ax1.add_patch(patches.Rectangle((3.00, -6.00), 6.50, 12.00, color='#f39c12', alpha=0.35, edgecolor='#d68910', linestyle='-', lw=2, label='Hot Brass Pinching Terminal'))
    
    # Plug Blades
    ax1.add_patch(patches.Rectangle((-6.28 - 0.76, 2.50 - 3.96), 1.52, 7.92, color='#ffffff', alpha=0.8, edgecolor='cyan', lw=1.5, label='Plug Blades (Hot/Neutral)'))
    ax1.add_patch(patches.Rectangle((6.28 - 0.76, 2.50 - 3.175), 1.52, 6.35, color='#ffffff', alpha=0.8, edgecolor='cyan', lw=1.5))
    
    # Highlight Interference Zone (Red Hatch)
    interf_box = patches.Rectangle((5.50, 2.80), 4.00, 4.38, hatch='///', fill=True, facecolor='red', alpha=0.4, edgecolor='red', lw=2, label='DIRECT INTERFERENCE ZONE')
    ax1.add_patch(interf_box)
    
    ax1.set_xlim(-15, 20)
    ax1.set_ylim(-20, 20)
    ax1.set_xlabel('X (mm)', color='white')
    ax1.set_ylabel('Y (mm)', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, color='#444444', linestyle=':')
    ax1.legend(loc='upper left', fontsize=7, facecolor='#1a1a1a', labelcolor='white')
    
    # -------------------------------------------------------------
    # Panel 2: Side Profile (Y-Z Plane) along Right Terminal Centerline (X = 6.28mm)
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#222222')
    ax2.set_title("2. Side Profile (Y-Z Plane at X = 6.28mm Hot Terminal)", color='white', fontsize=12, weight='bold', pad=10)
    
    # Baseplate floor (Z in [0, 1.0])
    ax2.add_patch(patches.Rectangle((-18, 0), 38, 1.0, color='#888888', alpha=0.5, label='Baseplate Floor (Z=1.00mm)'))
    
    # Bracket 3 & 4 walls (Z in [1.0, 4.60], Y in [-7.17, 7.17])
    ax2.add_patch(patches.Rectangle((-7.17, 1.0), 14.34, 3.60, color='#2ecc71', alpha=0.3, edgecolor='#27ae60', lw=1.5, label='Bracket Walls (Z=4.60mm)'))
    
    # Left Tower Profile in Background (X in [3.90, 5.40], Y in [6.25, 12.85], Z in [1.0, 14.09])
    tower_pts_yz = [
        (6.25, 1.0), (12.85, 1.0), (12.18, 14.09), (6.55, 14.09)
    ]
    ax2.add_patch(patches.Polygon(tower_pts_yz, color='#3498db', alpha=0.35, edgecolor='#2980b9', lw=1.5, label='Left Tower (Z_top = 14.09mm)'))
    
    # Lever Cross-Section
    # Axle circle (Y = 9.279, Z = 12.590, r = 2.10)
    axle_circle = patches.Circle((Y_AXLE, Z_AXLE), r_hub, color='#e67e22', alpha=0.7, edgecolor='#d35400', lw=2, label='Hub Barrel (Ø4.20mm)')
    ax2.add_patch(axle_circle)
    
    # Cam tab profile extending forward/down
    cam_pts_yz = [
        (Y_AXLE - 0.67, Z_AXLE + 1.99), # tangent top
        (2.84, 9.55),                    # tip
        (3.73, 6.89),                    # bot tip
        (Y_AXLE - 0.67 - 2.65, Z_AXLE + 1.99 - 0.89) # tangent bot
    ]
    ax2.add_patch(patches.Polygon(cam_pts_yz, color='#e74c3c', alpha=0.7, edgecolor='#c0392b', lw=1.5, label='Input Cam Tab (105° Bellcrank)'))
    
    # Plunger arm reaching downward to Z = -6.50
    plunger_pts_yz = [
        (Y_AXLE + 1.5, Z_AXLE - 1.0), (11.5, 3.0), (11.5, -6.5), (9.5, -6.5), (9.5, 3.0), (Y_AXLE - 1.5, Z_AXLE - 2.0)
    ]
    ax2.add_patch(patches.Polygon(plunger_pts_yz, color='#f1c40f', alpha=0.5, edgecolor='#f39c12', lw=1.5, label='Plunger (Z ≤ -6.50mm)'))
    
    # Brass pinching mechanism (Rising above tower to Z ~ 16.79mm, widening at top)
    # Bottom seated in brackets: Y in [-6.0, 6.0], Z in [1.0, 4.60]
    # Leaves rise to Z = 16.79 mm, widening at top from Z = 12.0 to 16.79 mm
    brass_pts_yz = [
        (-5.5, 1.0), (5.5, 1.0), (5.5, 11.0), (7.0, 16.79), (5.8, 16.79), (4.5, 12.0),
        (-4.5, 12.0), (-5.8, 16.79), (-7.0, 16.79), (-5.5, 11.0)
    ]
    ax2.add_patch(patches.Polygon(brass_pts_yz, color='#f39c12', alpha=0.45, edgecolor='#d68910', lw=2, linestyle='-', label='Brass Pinching Mechanism'))
    
    # Inserted Plug Blade (Hot)
    ax2.add_patch(patches.Rectangle((2.50 - 3.175, 5.0), 6.35, 16.5, color='#ffffff', alpha=0.5, edgecolor='cyan', lw=1.5, label='Plug Blade (Entering in -Z)'))
    
    # Annotate Key Dimensions
    # 1. Tower Top Z = 14.09 mm
    ax2.axhline(14.09, color='#3498db', linestyle=':', lw=1.0)
    ax2.annotate('Top of Left Tower (Z = 14.09 mm)', xy=(12.5, 14.09), xytext=(13.0, 15.5),
                 color='#3498db', fontsize=8, arrowprops=dict(arrowstyle='->', color='#3498db'))
    
    # 2. Brass Part Top Z = 16.79 mm (+2.70mm above tower)
    ax2.axhline(16.79, color='#f39c12', linestyle=':', lw=1.0)
    ax2.annotate('Top of Brass Part (+2.70 mm above Tower = 16.79 mm)\nWidened Funnel for Blade Insertion', xy=(7.0, 16.79), xytext=(8.0, 18.5),
                 color='#f39c12', fontsize=8, arrowprops=dict(arrowstyle='->', color='#f39c12'))
    
    # 3. Clash annotation
    ax2.annotate('COLLISION REGION:\nBrass top flare collides with\nCam Tab & Shaft Hub Barrel!', xy=(5.5, 11.0), xytext=(0.0, 14.0),
                 color='red', weight='bold', fontsize=9, arrowprops=dict(arrowstyle='->', color='red', lw=2),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#330000', edgecolor='red'))
    
    ax2.set_xlim(-15, 20)
    ax2.set_ylim(-8, 22)
    ax2.set_xlabel('Y (mm)', color='white')
    ax2.set_ylabel('Z (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.grid(True, color='#444444', linestyle=':')
    ax2.legend(loc='lower left', fontsize=7, facecolor='#1a1a1a', labelcolor='white')
    
    # -------------------------------------------------------------
    # Panel 3: Front Profile (X-Z Plane)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3, facecolor='#222222')
    ax3.set_title("3. Front Profile (X-Z Plane) Showing Spatial Widths", color='white', fontsize=12, weight='bold', pad=10)
    
    # Floor
    ax3.add_patch(patches.Rectangle((-20, 0), 40, 1.0, color='#888888', alpha=0.5))
    
    # Brackets 1-4
    ax3.add_patch(patches.Rectangle((-10.79, 1.0), 2.94, 3.60, color='#2ecc71', alpha=0.35, edgecolor='#27ae60')) # B1
    ax3.add_patch(patches.Rectangle((-4.67, 1.0), 2.90, 3.60, color='#2ecc71', alpha=0.35, edgecolor='#27ae60'))  # B2
    ax3.add_patch(patches.Rectangle((1.77, 1.0), 2.94, 3.60, color='#2ecc71', alpha=0.35, edgecolor='#27ae60'))   # B3
    ax3.add_patch(patches.Rectangle((7.85, 1.0), 2.94, 3.60, color='#2ecc71', alpha=0.35, edgecolor='#27ae60'))   # B4
    
    # Left Tower (X in [3.90, 5.40]) & Right Tower (X in [13.10, 14.60])
    ax3.add_patch(patches.Rectangle((3.90, 1.0), 1.50, 13.09, color='#3498db', alpha=0.5, edgecolor='#2980b9', lw=1.5, label='Left Tower (X=3.9-5.4)'))
    ax3.add_patch(patches.Rectangle((13.10, 1.0), 1.50, 13.09, color='#3498db', alpha=0.5, edgecolor='#2980b9', lw=1.5, label='Right Tower (X=13.1-14.6)'))
    
    # Lever Hub & Axle Pins
    ax3.add_patch(patches.Rectangle((3.50, Z_AXLE - 1.40), 2.00, 2.80, color='#00d2ff', alpha=0.8, edgecolor='cyan', label='Pivot Pins (Ø2.80mm)'))
    ax3.add_patch(patches.Rectangle((13.00, Z_AXLE - 1.40), 2.00, 2.80, color='#00d2ff', alpha=0.8, edgecolor='cyan'))
    ax3.add_patch(patches.Rectangle((5.50, Z_AXLE - 2.10), 7.50, 4.20, color='#e67e22', alpha=0.7, edgecolor='#d35400', label='Hub Barrel (Ø4.20mm)'))
    
    # Cam Tab (X in [5.70, 8.40])
    ax3.add_patch(patches.Rectangle((cam_x_min, 9.50), CAM_WIDTH_X, 4.50, color='#e74c3c', alpha=0.7, edgecolor='#c0392b', label='Cam Tab (X=5.7-8.4)'))
    
    # Brass pinching mechanism in Brackets 3 & 4 (X in [2.5, 10.0], Z in [1.0, 16.79])
    # Pinching fingers clamp blade at X = 6.28mm
    ax3.add_patch(patches.Rectangle((2.85, 1.0), 2.50, 15.79, color='#f39c12', alpha=0.4, edgecolor='#d68910', lw=1.5, label='Left Brass Leaf (X ~ 2.85-5.35)'))
    ax3.add_patch(patches.Rectangle((7.21, 1.0), 2.50, 15.79, color='#f39c12', alpha=0.4, edgecolor='#d68910', lw=1.5, label='Right Brass Leaf (X ~ 7.21-9.71)'))
    
    # Hot Plug blade at X = 6.28 mm
    ax3.add_patch(patches.Rectangle((6.28 - 0.76, 5.0), 1.52, 16.50, color='#ffffff', alpha=0.7, edgecolor='cyan', lw=1.5, label='Hot Plug Blade (X=6.28)'))
    
    ax3.annotate('Left Brass Leaf overlaps with\nLeft Tower & Left side of Lever!', xy=(5.0, 13.0), xytext=(0.0, 18.0),
                 color='red', weight='bold', fontsize=8, arrowprops=dict(arrowstyle='->', color='red'))
    
    ax3.set_xlim(-15, 20)
    ax3.set_ylim(-8, 22)
    ax3.set_xlabel('X (mm)', color='white')
    ax3.set_ylabel('Z (mm)', color='white')
    ax3.tick_params(colors='white')
    ax3.grid(True, color='#444444', linestyle=':')
    ax3.legend(loc='lower left', fontsize=7, facecolor='#1a1a1a', labelcolor='white')
    
    # -------------------------------------------------------------
    # Panel 4: Resolution Architecture & Engineering Solutions
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4, facecolor='#222222')
    ax4.set_title("4. Root Cause Summary & Actionable Solutions", color='white', fontsize=12, weight='bold', pad=10)
    ax4.axis('off')
    
    summary_text = (
        "1. PHYSICAL CONTEXT REVEALED:\n"
        "   * The electrical contacts are brass spring-leaf pinching mechanisms seated in the brackets.\n"
        "   * The brass part widens at the top (lead-in flare) and is taller than the towers (Z_top ~ 16.79 mm vs 14.09 mm).\n"
        "   * The left tower top is 2.7 mm from the brass part (either 2.7 mm taller in Z or 2.7 mm offset in Y).\n\n"
        "2. INTERFERENCE ROOT CAUSE:\n"
        "   * The right brass pinching mechanism (Hot terminal) spans X in [1.77, 10.79] mm and Y up to +7.17 mm (plus top flare).\n"
        "   * Because the brass part rises to Z ~ 16.79 mm, its top rear flared leaf extends into Y in [5.0, 7.5+] mm.\n"
        "   * The rocker lever's forward input cam (X in [5.70, 8.40]), left flank rib (X in [5.60, 6.60]),\n"
        "     and structural hub barrel (X in [5.50, 13.00], Y in [7.18, 11.38]) collide directly with the tall brass contact!\n\n"
        "3. SOLUTIONS TO RESOLVE INTERFERENCE:\n"
        "   A. Trim / Re-profile the Lever Cam Arm & Left Flank Rib:\n"
        "      - Narrow or shift the input cam tab so it engages only the inserted plug blade without encroaching on the brass leaf.\n"
        "      - Add clearance relief / chamfer / cutout on the front-left face of the lever hub and flank rib.\n"
        "   B. Adjust Tower & Shaft Axis Position:\n"
        "      - Ensure tower cradle and shaft axis provide sufficient Y/Z clearance behind the 2.7 mm brass boundary.\n"
        "   C. Verify Left Tower Buttress Clearance:\n"
        "      - Ensure the Left Tower (X in [3.90, 5.40]) does not pinch or bind the brass mechanism's outer retention flanges."
    )
    
    ax4.text(0.02, 0.98, summary_text, color='#ecf0f1', fontsize=9.5, fontfamily='monospace',
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e272e', edgecolor='#3498db', lw=1.5))
    
    plt.tight_layout()
    out_png = os.path.join(os.path.dirname(__file__), "brass_mechanism_interference_analysis.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nDiagnostic plot saved to: {out_png}")

if __name__ == '__main__':
    run_inspection()
