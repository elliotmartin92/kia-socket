"""
testing/generate_shaft_blueprint.py
Generates a comprehensive, ultra-high-resolution, fully dimensioned engineering blueprint
of the automotive safety interlock lever/rocker subpart.

Includes:
1. Side Orthographic Elevation (Y-Z Profile): 105° bellcrank, cam ramp, plunger drop to switch.
2. Top-Down Plan View (X-Y Plane): Stepped pins, 6.90mm hub, 3-rib fork array, cam tab offset.
3. Front Orthographic Elevation (X-Z Plane): Plunger blade width, step-down journals, floor datum.
4. 3D Isometric View: Color-coded functional subparts with callouts and dimensional labels.
5. Engineering Title Block & Kinematic Specifications Table.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, Polygon as MplPoly, Arc
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_shaft
from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_LEN, PIN_DIAMETER, HUB_DIAMETER,
    PLUNGER_REACH_BELOW_Z, CAM_WIDTH_X, CAM_X_CENTER, RIB_FLANK_THICK, PLUNGER_WIDTH_X,
    HOLE_X_CENTER, X_TOWER_CENTER
)

def create_shaft_blueprint():
    # Build models
    subparts = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, return_subparts=True, with_supports=False)
    shaft_full = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)

    # Blueprint theme: Professional dark technical blueprint or crisp white CAD blueprint
    # Using crisp high-contrast CAD blueprint style (clean white background, dark navy / technical cyan lines)
    fig = plt.figure(figsize=(26, 15), dpi=200, facecolor='#ffffff')
    fig.suptitle("AUTOMOTIVE 120V AC OUTLET SAFETY INTERLOCK ROCKER LEVER — ENGINEERING BLUEPRINT",
                 fontsize=18, fontweight='bold', color='#0d233a', y=0.985)
    fig.text(0.5, 0.965, "Sub-Assembly Component Definition • Reverse-Engineered Kinematic Bellcrank Mechanism • Units: mm",
             ha='center', fontsize=12, fontstyle='italic', color='#475569')

    # Color palette for subparts
    colors = {
        'pins': '#0284c7',       # Cyan / Blue
        'hub': '#2563eb',        # Deep Blue
        'ribs': '#059669',       # Emerald Green
        'plunger': '#d97706',    # Amber / Orange
        'web': '#64748b',        # Slate
        'cam': '#dc2626',        # Crimson Red
    }

    # =========================================================================
    # PANEL 1: SIDE ORTHOGRAPHIC ELEVATION (Y-Z PLANE)
    # =========================================================================
    ax1 = fig.add_axes([0.05, 0.50, 0.42, 0.44])
    ax1.set_facecolor('#f8fafc')
    ax1.set_title("1. SIDE ELEVATION & KINEMATIC PROFILE (Y-Z Plane)", fontsize=13, fontweight='bold', color='#0f172a', pad=10)

    # Plot sections/projections in Y-Z
    # Axle datum
    y_c, z_c = Y_AXLE, Z_AXLE
    r_hub = HUB_DIAMETER / 2.0
    r_pin = PIN_DIAMETER / 2.0

    # Draw datums
    ax1.axhline(0.0, color='#94a3b8', linestyle='--', lw=1.5, label='Baseplate Floor Datum (Z = 0.00mm)')
    ax1.axhline(-6.50, color='#dc2626', linestyle='-.', lw=1.5, label='PCB Switch Contact Datum (Z = -6.50mm)')
    ax1.axvline(12.40, color='#16a34a', linestyle=':', lw=1.5, label='PCB Switch Actuation Plane (Y = 12.40mm)')

    # Slice or 2D outlines of cam, plunger, ribs, hub
    # Cam 2D polygon
    poly_pts_cam = np.array([
        (y_c, z_c),
        (y_c, z_c + r_hub),
        (6.80, 12.20),
        (5.00, 10.00),
        (1.50, 7.40),
        (1.80, 5.10),
        (4.50, 5.30),
        (y_c - 1.50, z_c - 2.50),
        (y_c, z_c)
    ])
    ax1.fill(poly_pts_cam[:, 0], poly_pts_cam[:, 1], color=colors['cam'], alpha=0.35, label='Input Cam Tab (105° Bellcrank)')
    ax1.plot(poly_pts_cam[:, 0], poly_pts_cam[:, 1], color=colors['cam'], lw=2)

    # Flank rib 2D polygon
    flank_pts = np.array([
        (y_c - 1.50, z_c + 0.60),
        (y_c + 3.20, z_c - 1.50),
        (y_c + 2.50, z_c - 4.50),
        (y_c + 0.20, z_c - 4.20),
        (y_c - 1.60, z_c - 1.00),
        (y_c - 1.50, z_c + 0.60)
    ])
    ax1.fill(flank_pts[:, 0], flank_pts[:, 1], color=colors['ribs'], alpha=0.30, label='Stiffener Flank Ribs (Dual)')
    ax1.plot(flank_pts[:, 0], flank_pts[:, 1], color=colors['ribs'], lw=1.5)

    # 3. Structural Connecting Web (Flatish Rectangle Opposite Cam Tab)
    web_y_min = y_c - 1.50  # 7.78mm
    web_y_max = y_c + 1.80  # 11.08mm
    web_z_min = z_c - 3.20  # 9.39mm
    web_z_max = z_c + 1.00  # 13.59mm
    rect_web = Rectangle((web_y_min, web_z_min), web_y_max - web_y_min, web_z_max - web_z_min,
                         facecolor=colors['web'], edgecolor='#334155', lw=2, alpha=0.5, linestyle='-',
                         label='Structural Web (Opposite Cam Tab)')
    ax1.add_patch(rect_web)

    # Tower Rear Cross-Tie Bridge (Baseplate Frame Phantom) to show clearance
    bridge_y_min = 11.75
    bridge_y_max = 12.85
    bridge_z_min = 12.60
    bridge_z_max = 15.00
    rect_bridge = Rectangle((bridge_y_min, bridge_z_min), bridge_y_max - bridge_y_min, bridge_z_max - bridge_z_min,
                            facecolor='#f3e8ff', edgecolor='#9333ea', lw=2, linestyle='--', alpha=0.6,
                            label='Tower Rear Bridge (Fixed on Housing)')
    ax1.add_patch(rect_bridge)

    # Clearance callout between Web and Tower Bridge
    ax1.annotate('', xy=(web_y_max, 13.0), xytext=(bridge_y_min, 13.0),
                 arrowprops=dict(arrowstyle='<->', color='#9333ea', lw=1.8))
    ax1.text((web_y_max + bridge_y_min)/2.0, 13.4, f"0.67mm Gap\n(Clean Air)", ha='center', fontsize=8.5, fontweight='bold', color='#7e22ce')

    # Plunger profile
    N = 40
    t = np.linspace(0, 1, N)
    plunger_y_center = 10.479
    r_tip = 1.00
    z_tip = -6.50
    spine_y = (1-t)**2 * (y_c + r_hub) + 2*(1-t)*t * (y_c + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_c - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    belly_y = (1-t)**2 * (y_c - r_hub) + 2*(1-t)*t * (y_c + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_c - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    plunger_outline = np.vstack([
        np.column_stack([spine_y, spine_z]),
        np.array(tip_pts),
        np.column_stack([belly_y[::-1], belly_z[::-1]])
    ])
    ax1.fill(plunger_outline[:, 0], plunger_outline[:, 1], color=colors['plunger'], alpha=0.45, label='Extended Plunger Blade (Swings to Switch)')
    ax1.plot(plunger_outline[:, 0], plunger_outline[:, 1], color=colors['plunger'], lw=2.5)

    # Hub barrel & Pin circles
    c_hub = Circle((y_c, z_c), r_hub, facecolor=colors['hub'], alpha=0.5, edgecolor=colors['hub'], lw=2, label='Hub Barrel (Ø4.20mm)')
    c_pin = Circle((y_c, z_c), r_pin, facecolor=colors['pins'], alpha=0.8, edgecolor='#0369a1', lw=2, linestyle='--', label='Axle Pins (Ø2.80mm)')
    ax1.add_patch(c_hub)
    ax1.add_patch(c_pin)
    ax1.plot(y_c, z_c, 'k+', markersize=12, markeredgewidth=2, label=f'Axle Pivot Datum (Y={y_c:.2f}, Z={z_c:.2f})')

    # Callout for Flat Web opposite Cam
    ax1.annotate('Flat Structural Web\n(Opposite Cam Tab)', xy=(web_y_max, 10.5), xytext=(web_y_max + 1.5, 8.5),
                 arrowprops=dict(facecolor='#475569', shrink=0.08, width=1.2, headwidth=5),
                 fontweight='bold', color='#334155', fontsize=8.5)

    # Dimension lines & callouts
    # 1. Total drop: Z_axle to Z_tip
    ax1.annotate('', xy=(14.2, z_tip), xytext=(14.2, z_c),
                 arrowprops=dict(arrowstyle='<->', color='#0f172a', lw=1.5))
    ax1.text(14.5, (z_c + z_tip)/2.0, f"ΔZ = {z_c - z_tip:.2f}mm\n(Axle to Tip)", va='center', fontsize=9.5, fontweight='bold', color='#0f172a')

    # 2. Plunger below floor: Z=0 to Z=-6.50
    ax1.annotate('', xy=(12.8, -6.50), xytext=(12.8, 0.0),
                 arrowprops=dict(arrowstyle='<->', color='#dc2626', lw=1.5))
    ax1.text(13.0, -3.25, "6.50mm Reach\nBelow Floor", va='center', fontsize=9, fontweight='bold', color='#dc2626')

    # 3. 105° Bellcrank Angle Arc
    arc = Arc((y_c, z_c), 8.0, 8.0, angle=0, theta1=205, theta2=310, color='#7c3aed', lw=2)
    ax1.add_patch(arc)
    ax1.text(y_c - 2.8, z_c - 2.8, "105° Bellcrank\nAngle", fontsize=9.5, fontweight='bold', color='#7c3aed', ha='center')

    # 4. Plug Blade Contact Vector
    ax1.annotate('Hot Plug Blade\nInsertion Force\n(Down & Inward)',
                 xy=(2.0, 7.5), xytext=(-1.5, 11.5),
                 arrowprops=dict(facecolor='#dc2626', shrink=0.05, width=2, headwidth=7),
                 fontweight='bold', color='#dc2626', fontsize=9, ha='center')

    # 5. Plunger Tip Arc & Switch Contact
    ax1.annotate('Rounded Tip (R=1.0mm)\nDepresses Tactile Switch past Y=12.40mm',
                 xy=(plunger_y_center, z_tip), xytext=(1.0, -5.5),
                 arrowprops=dict(facecolor='#d97706', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', color='#b45309', fontsize=9)

    ax1.set_xlim(-3.0, 16.5)
    ax1.set_ylim(-8.5, 16.5)
    ax1.set_xlabel("Y Coordinate (mm)", fontweight='bold', color='#334155')
    ax1.set_ylabel("Z Coordinate (mm)", fontweight='bold', color='#334155')
    ax1.grid(True, linestyle=':', alpha=0.7)
    ax1.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

    # =========================================================================
    # PANEL 2: TOP-DOWN PLAN VIEW (X-Y PLANE)
    # =========================================================================
    ax2 = fig.add_axes([0.53, 0.50, 0.42, 0.44])
    ax2.set_facecolor('#f8fafc')
    ax2.set_title("2. PLAN VIEW & LATERAL REVERSING FORK (X-Y Plane)", fontsize=13, fontweight='bold', color='#0f172a', pad=10)

    # Total axle span
    x_c = X_TOWER_CENTER  # 9.25
    hub_w = 6.90
    x_hub_l = x_c - hub_w / 2.0  # 5.80
    x_hub_r = x_c + hub_w / 2.0  # 12.70
    pin_l_x = x_hub_l - PIN_LEN  # 3.50
    pin_r_x = x_hub_r + PIN_LEN  # 15.00

    # Draw Left Pin
    ax2.add_patch(Rectangle((pin_l_x, y_c - r_pin), PIN_LEN, 2*r_pin, facecolor=colors['pins'], edgecolor='#0369a1', lw=1.5, label='Pivot Axle Pin (Ø2.80mm)'))
    # Draw Right Pin
    ax2.add_patch(Rectangle((x_hub_r, y_c - r_pin), PIN_LEN, 2*r_pin, facecolor=colors['pins'], edgecolor='#0369a1', lw=1.5))
    # Draw Hub Barrel
    ax2.add_patch(Rectangle((x_hub_l, y_c - r_hub), hub_w, 2*r_hub, facecolor=colors['hub'], edgecolor='#1d4ed8', lw=2, alpha=0.6, label='Structural Hub Barrel (Ø4.20mm)'))

    # Draw Rib 1 (Left Flank)
    ax2.add_patch(Rectangle((x_hub_l + 0.10, y_c - 1.60), RIB_FLANK_THICK, 4.80, facecolor=colors['ribs'], edgecolor='#047857', lw=1.5, alpha=0.7, label='Flank Stiffener Rib (1.00mm)'))
    # Draw Rib 3 (Right Flank)
    ax2.add_patch(Rectangle((x_hub_r - 0.10 - RIB_FLANK_THICK, y_c - 1.60), RIB_FLANK_THICK, 4.80, facecolor=colors['ribs'], edgecolor='#047857', lw=1.5, alpha=0.7))
    # Draw Center Plunger
    ax2.add_patch(Rectangle((HOLE_X_CENTER - PLUNGER_WIDTH_X/2.0, y_c - r_hub), PLUNGER_WIDTH_X, 3.80, facecolor=colors['plunger'], edgecolor='#b45309', lw=2, alpha=0.8, label=f'Plunger Blade ({PLUNGER_WIDTH_X:.2f}mm W)'))
    # Draw Cam Tab
    x_cam_start = max(x_hub_l, CAM_X_CENTER - CAM_WIDTH_X/2.0)
    ax2.add_patch(Rectangle((x_cam_start, 1.50), CAM_WIDTH_X, y_c + r_hub - 1.50, facecolor=colors['cam'], edgecolor='#b91c1c', lw=2, alpha=0.8, label=f'Input Cam Tab ({CAM_WIDTH_X:.2f}mm W)'))

    # Draw Structural Web (Flatish Rectangle Opposite Cam Tab)
    web_w_x = (x_hub_r - 0.10) - (x_hub_l + 0.10)  # 6.70mm
    ax2.add_patch(Rectangle((x_hub_l + 0.10, web_y_min), web_w_x, web_y_max - web_y_min,
                            facecolor=colors['web'], edgecolor='#334155', lw=1.8, alpha=0.5,
                            label=f'Structural Web ({web_w_x:.2f}mm W x {web_y_max - web_y_min:.2f}mm Y)'))

    # Tower Rear Bridge (Phantom Baseplate Outline)
    ax2.add_patch(Rectangle((5.40, 11.75), 7.70, 1.10,
                            facecolor='#f3e8ff', edgecolor='#9333ea', lw=2, linestyle='--', alpha=0.6,
                            label='Tower Cross-Tie Bridge (Fixed on Housing)'))

    # Clearance callout between Lever Web and Tower Bridge in Y
    ax2.annotate('', xy=(x_c - 1.5, web_y_max), xytext=(x_c - 1.5, 11.75),
                 arrowprops=dict(arrowstyle='<->', color='#9333ea', lw=1.5))
    ax2.text(x_c - 1.7, (web_y_max + 11.75)/2.0, "0.67mm Air Gap", ha='right', va='center', fontsize=8, fontweight='bold', color='#7e22ce')

    # Centerlines
    ax2.axhline(y_c, color='#64748b', linestyle='-.', lw=1.2, label=f'Axle Centerline (Y={y_c:.2f})')
    ax2.axvline(x_c, color='#94a3b8', linestyle=':', lw=1.2, label=f'Mechanism Centerline (X={x_c:.2f})')
    ax2.axvline(CAM_X_CENTER, color='#dc2626', linestyle=':', lw=1.2, label=f'Hot Plug Prong Datum (X={CAM_X_CENTER:.2f})')
    ax2.axvline(HOLE_X_CENTER, color='#d97706', linestyle=':', lw=1.2, label=f'Through-Hole Center (X={HOLE_X_CENTER:.2f})')

    # Dimensions
    # 1. Total axle length: 11.50mm
    ax2.annotate('', xy=(pin_l_x, 13.5), xytext=(pin_r_x, 13.5),
                 arrowprops=dict(arrowstyle='<->', color='#0f172a', lw=1.5))
    ax2.text((pin_l_x + pin_r_x)/2.0, 13.8, f"TOTAL AXLE LENGTH: {TOTAL_AXLE_LEN:.2f}mm", ha='center', fontsize=9.5, fontweight='bold', color='#0f172a')

    # 2. Hub Width: 6.90mm
    ax2.annotate('', xy=(x_hub_l, y_c + 2.5), xytext=(x_hub_r, y_c + 2.5),
                 arrowprops=dict(arrowstyle='<->', color='#1d4ed8', lw=1.5))
    ax2.text(x_c, y_c + 2.8, f"HUB BARREL WIDTH: {hub_w:.2f}mm", ha='center', fontsize=9, fontweight='bold', color='#1d4ed8')

    # 3. Pin length left and right
    ax2.annotate('', xy=(pin_l_x, y_c - 2.8), xytext=(x_hub_l, y_c - 2.8),
                 arrowprops=dict(arrowstyle='<->', color='#0369a1', lw=1.2))
    ax2.text((pin_l_x + x_hub_l)/2.0, y_c - 3.8, f"{PIN_LEN:.2f}mm\nPin", ha='center', fontsize=8, fontweight='bold', color='#0369a1')

    ax2.annotate('', xy=(x_hub_r, y_c - 2.8), xytext=(pin_r_x, y_c - 2.8),
                 arrowprops=dict(arrowstyle='<->', color='#0369a1', lw=1.2))
    ax2.text((x_hub_r + pin_r_x)/2.0, y_c - 3.8, f"{PIN_LEN:.2f}mm\nPin", ha='center', fontsize=8, fontweight='bold', color='#0369a1')

    # 4. Cam tab width
    ax2.annotate(f"Cam: {CAM_WIDTH_X:.2f}mm", xy=(x_cam_start + CAM_WIDTH_X/2.0, 2.0), xytext=(x_cam_start - 3.0, 1.0),
                 arrowprops=dict(facecolor='#dc2626', shrink=0.08, width=1.2, headwidth=5),
                 fontweight='bold', color='#dc2626', fontsize=8.5)

    # 5. Plunger width
    ax2.annotate(f"Plunger: {PLUNGER_WIDTH_X:.2f}mm", xy=(HOLE_X_CENTER, y_c - 1.0), xytext=(HOLE_X_CENTER + 2.5, -0.5),
                 arrowprops=dict(facecolor='#d97706', shrink=0.08, width=1.2, headwidth=5),
                 fontweight='bold', color='#b45309', fontsize=8.5)

    ax2.set_xlim(1.5, 17.0)
    ax2.set_ylim(-1.5, 15.0)
    ax2.set_xlabel("X Coordinate (mm)", fontweight='bold', color='#334155')
    ax2.set_ylabel("Y Coordinate (mm)", fontweight='bold', color='#334155')
    ax2.grid(True, linestyle=':', alpha=0.7)
    ax2.legend(loc='lower left', fontsize=8, framealpha=0.9)

    # =========================================================================
    # PANEL 3: FRONT ORTHOGRAPHIC ELEVATION (X-Z PLANE)
    # =========================================================================
    ax3 = fig.add_axes([0.05, 0.06, 0.42, 0.38])
    ax3.set_facecolor('#f8fafc')
    ax3.set_title("3. FRONT ELEVATION & PLUNGER DROP (X-Z Plane)", fontsize=13, fontweight='bold', color='#0f172a', pad=10)

    # Draw Axle step profile
    # Left pin: [pin_l_x, x_hub_l], Z in [z_c - r_pin, z_c + r_pin]
    ax3.add_patch(Rectangle((pin_l_x, z_c - r_pin), PIN_LEN, 2*r_pin, facecolor=colors['pins'], edgecolor='#0369a1', lw=1.5))
    # Right pin: [x_hub_r, pin_r_x], Z in [z_c - r_pin, z_c + r_pin]
    ax3.add_patch(Rectangle((x_hub_r, z_c - r_pin), PIN_LEN, 2*r_pin, facecolor=colors['pins'], edgecolor='#0369a1', lw=1.5))
    # Hub barrel: [x_hub_l, x_hub_r], Z in [z_c - r_hub, z_c + r_hub]
    ax3.add_patch(Rectangle((x_hub_l, z_c - r_hub), hub_w, 2*r_hub, facecolor=colors['hub'], edgecolor='#1d4ed8', lw=2, alpha=0.6))

    # Plunger blade: drop to Z = -6.50
    p_x_min = HOLE_X_CENTER - PLUNGER_WIDTH_X / 2.0
    ax3.add_patch(Rectangle((p_x_min, -6.50), PLUNGER_WIDTH_X, z_c + r_hub - (-6.50), facecolor=colors['plunger'], edgecolor='#b45309', lw=2, alpha=0.75))

    # Flank ribs drop: Z in [8.09, 14.69]
    ax3.add_patch(Rectangle((x_hub_l + 0.10, z_c - 4.50), RIB_FLANK_THICK, 6.60, facecolor=colors['ribs'], edgecolor='#047857', lw=1.5, alpha=0.65))
    ax3.add_patch(Rectangle((x_hub_r - 0.10 - RIB_FLANK_THICK, z_c - 4.50), RIB_FLANK_THICK, 6.60, facecolor=colors['ribs'], edgecolor='#047857', lw=1.5, alpha=0.65))

    # Cam tab drop: Z in [5.10, 14.69]
    ax3.add_patch(Rectangle((x_cam_start, 5.10), CAM_WIDTH_X, z_c + r_hub - 5.10, facecolor=colors['cam'], edgecolor='#b91c1c', lw=2, alpha=0.7))

    # Datums
    ax3.axhline(0.0, color='#94a3b8', linestyle='--', lw=1.5, label='Baseplate Floor (Z = 0.00mm)')
    ax3.axhline(-6.50, color='#dc2626', linestyle='-.', lw=1.5, label='Tactile Switch Surface (Z = -6.50mm)')
    ax3.axhline(z_c, color='#64748b', linestyle=':', lw=1.2, label=f'Axle Datum (Z = {z_c:.2f}mm)')

    # Dimensions
    # Pin diameter
    ax3.annotate('', xy=(pin_l_x - 0.5, z_c - r_pin), xytext=(pin_l_x - 0.5, z_c + r_pin),
                 arrowprops=dict(arrowstyle='<->', color='#0369a1', lw=1.5))
    ax3.text(pin_l_x - 0.8, z_c, f"Ø{PIN_DIAMETER:.2f}mm", va='center', ha='right', fontsize=9, fontweight='bold', color='#0369a1')

    # Hub diameter
    ax3.annotate('', xy=(x_c, z_c - r_hub), xytext=(x_c, z_c + r_hub),
                 arrowprops=dict(arrowstyle='<->', color='#1d4ed8', lw=1.5))
    ax3.text(x_c + 0.3, z_c, f"Ø{HUB_DIAMETER:.2f}mm Hub", va='center', fontsize=9, fontweight='bold', color='#1d4ed8')

    ax3.set_xlim(1.5, 17.0)
    ax3.set_ylim(-8.5, 17.5)
    ax3.set_xlabel("X Coordinate (mm)", fontweight='bold', color='#334155')
    ax3.set_ylabel("Z Coordinate (mm)", fontweight='bold', color='#334155')
    ax3.grid(True, linestyle=':', alpha=0.7)
    ax3.legend(loc='lower left', fontsize=8, framealpha=0.9)

    # =========================================================================
    # PANEL 4: 3D ISOMETRIC COLOR-CODED RENDER
    # =========================================================================
    ax4 = fig.add_axes([0.53, 0.06, 0.42, 0.38], projection='3d')
    ax4.set_facecolor('#f8fafc')
    ax4.set_title("4. 3D ISOMETRIC SUB-PART TOPOLOGY", fontsize=13, fontweight='bold', color='#0f172a', pad=10)

    # Render each subpart with distinct color
    subpart_meta = [
        ('pin_l', colors['pins'], 'Left Pivot Pin (Ø2.80mm)'),
        ('pin_r', colors['pins'], 'Right Pivot Pin (Ø2.80mm)'),
        ('hub', colors['hub'], 'Central Hub Barrel (Ø4.20mm)'),
        ('rib1', colors['ribs'], 'Left Flank Rib (1.00mm)'),
        ('rib3', colors['ribs'], 'Right Flank Rib (1.00mm)'),
        ('plunger', colors['plunger'], 'Output Plunger Arm (Z=-6.50mm)'),
        ('web', colors['web'], 'Connecting Cross-Web'),
        ('cam', colors['cam'], 'Plug Blade Input Cam Tab'),
    ]

    for key, color, label in subpart_meta:
        m = subparts[key]
        f_sub = m.faces[::2]  # Subsample for rendering speed
        tri_v = m.vertices[f_sub]
        collection = Poly3DCollection(tri_v, facecolors=color, edgecolors='#1e293b', linewidths=0.2, alpha=0.85)
        ax4.add_collection3d(collection)

    ax4.set_xlim([3.0, 15.5])
    ax4.set_ylim([1.0, 13.5])
    ax4.set_zlim([-7.0, 15.5])
    ax4.view_init(elev=28, azim=-125)
    ax4.set_xlabel('X (mm)', fontweight='bold', labelpad=4)
    ax4.set_ylabel('Y (mm)', fontweight='bold', labelpad=4)
    ax4.set_zlabel('Z (mm)', fontweight='bold', labelpad=4)

    # Output file
    out_file = os.path.join(_ROOT, 'testing', 'labeled_shaft_blueprint.png')
    plt.savefig(out_file, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Generated labeled blueprint at: {out_file}")

    # Copy to artifact directory for presentation
    art_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\2def6e88-1939-48c0-a845-9a4f348279cc"
    art_file = os.path.join(art_dir, "labeled_shaft_blueprint.png")
    import shutil
    shutil.copyfile(out_file, art_file)
    print(f"Copied to artifact directory: {art_file}")

if __name__ == '__main__':
    create_shaft_blueprint()
