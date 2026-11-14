"""
testing/generate_print_assembly_guide.py
Generates a highly visual, professional step-by-step assembly guide for the outlet sub-housing:
Updated Workflow:
  STEP 1: Remove Built-In Breakaway Supports (Bed Pad, Backplate Fins, Slit Struts, Clip Struts, Lever Struts)
  STEP 2: Free & Verify Print-in-Place Safety Lever (Captive 360° Enclosed Towers & Monolithic Rear Bridge)
  STEP 3: Seat OEM Brass Contacts (Neutral & Hot, Sliding into Brackets 1-4 with Monolithic Slit Shrouds)
  STEP 4: Assembly Complete & Final Motion Check (Full Kinematic & Mechanical Verification Checklist)
Features unified Poly3DCollection depth-sorted rendering, clean HUD banners, and crisp 3D callouts.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import to_rgb
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, build_45deg_supported_part_mesh, extrude_shapely_geom
from build_shaft import build_shaft_rocker_mesh

def build_brass_contact_mesh(is_hot=True):
    """
    Builds an exact 3D model of the OEM brass contact matching zoom_bracket34_photo.png:
    - Two horizontal contact leaves with curled inner wiping edges and rounded outer corners
    - Stepped-down U-bracket bridge at Y ~ -2.5mm
    - S-curved brass runner clearly visible above the floor extending to the slit
    - Vertical spade blade plunging through floor slit into -Z under the floor
    """
    xc = 6.28 if is_hot else -6.28
    slit_x = 8.453 if is_hot else -7.853
    
    # 1. Left and Right horizontal contact leaves (Z ~ 4.5 to 5.0mm)
    y_start = -1.0
    y_end   =  5.8
    w_pad = 2.20
    gap   = 1.10 # pinch slit gap
    
    # Pad top flat plate (Z = 4.5 to 5.0)
    p_left_flat = Polygon([
        (-(gap/2.0 + w_pad), y_start),
        (-gap/2.0, y_start),
        (-gap/2.0, y_end),
        (-(gap/2.0 + w_pad), y_end)
    ])
    m_left_flat = extrude_shapely_geom(p_left_flat, height=0.50)
    m_left_flat.apply_translation([0, 0, 4.5])
    
    p_right_flat = Polygon([
        (gap/2.0, y_start),
        (gap/2.0 + w_pad, y_start),
        (gap/2.0 + w_pad, y_end),
        (gap/2.0, y_end)
    ])
    m_right_flat = extrude_shapely_geom(p_right_flat, height=0.50)
    m_right_flat.apply_translation([0, 0, 4.5])
    
    # Inner curled wiping edges (curling down from Z=4.5 to Z=2.0 along the gap)
    p_left_curl = Polygon([
        (-gap/2.0 - 0.40, y_start),
        (-gap/2.0, y_start),
        (-gap/2.0, y_end),
        (-gap/2.0 - 0.40, y_end)
    ])
    m_left_curl = extrude_shapely_geom(p_left_curl, height=2.50)
    m_left_curl.apply_translation([0, 0, 2.0])
    
    p_right_curl = Polygon([
        (gap/2.0, y_start),
        (gap/2.0 + 0.40, y_start),
        (gap/2.0 + 0.40, y_end),
        (gap/2.0, y_end)
    ])
    m_right_curl = extrude_shapely_geom(p_right_curl, height=2.50)
    m_right_curl.apply_translation([0, 0, 2.0])
    
    # Outer side walls (curling down to seating shelf at Z=1.5)
    p_left_wall = Polygon([
        (-(gap/2.0 + w_pad), y_start),
        (-(gap/2.0 + w_pad) + 0.50, y_start),
        (-(gap/2.0 + w_pad) + 0.50, y_end),
        (-(gap/2.0 + w_pad), y_end)
    ])
    m_left_wall = extrude_shapely_geom(p_left_wall, height=3.00)
    m_left_wall.apply_translation([0, 0, 1.5])
    
    p_right_wall = Polygon([
        (gap/2.0 + w_pad - 0.50, y_start),
        (gap/2.0 + w_pad, y_start),
        (gap/2.0 + w_pad, y_end),
        (gap/2.0 + w_pad - 0.50, y_end)
    ])
    m_right_wall = extrude_shapely_geom(p_right_wall, height=3.00)
    m_right_wall.apply_translation([0, 0, 1.5])
    
    # 2. U-shaped step-down bridge at Y in [-2.5, -1.0], Z in [1.0, 1.5]
    p_riser_l = Polygon([(-(gap/2.0 + w_pad), -1.5), (-(gap/2.0 + w_pad - 0.6), -1.5),
                         (-(gap/2.0 + w_pad - 0.6), -1.0), (-(gap/2.0 + w_pad), -1.0)])
    m_riser_l = extrude_shapely_geom(p_riser_l, height=3.00)
    m_riser_l.apply_translation([0, 0, 1.5])
    
    p_riser_r = Polygon([(gap/2.0 + w_pad - 0.6, -1.5), (gap/2.0 + w_pad, -1.5),
                         (gap/2.0 + w_pad, -1.0), (gap/2.0 + w_pad - 0.6, -1.0)])
    m_riser_r = extrude_shapely_geom(p_riser_r, height=3.00)
    m_riser_r.apply_translation([0, 0, 1.5])
    
    # Horizontal crossbar at Y in [-2.5, -1.5], Z in [1.0, 1.5]
    p_crossbar = Polygon([
        (-(gap/2.0 + w_pad), -2.5),
        (gap/2.0 + w_pad, -2.5),
        (gap/2.0 + w_pad, -1.5),
        (-(gap/2.0 + w_pad), -1.5)
    ])
    m_crossbar = extrude_shapely_geom(p_crossbar, height=0.50)
    m_crossbar.apply_translation([0, 0, 1.0])
    
    # 3. S-curved runner clearly visible on the floor (Z = 1.0 to 1.5mm)
    dx_slit = slit_x - xc
    w_run = 1.80
    
    y_pts = np.linspace(-2.5, -12.1, 15)
    t = (y_pts - (-2.5)) / (-12.1 - (-2.5))
    s = 3*t**2 - 2*t**3
    x_centerline = s * dx_slit
    
    poly_left_edge = [(x_centerline[i] - w_run/2.0, y_pts[i]) for i in range(len(y_pts))]
    poly_right_edge = [(x_centerline[i] + w_run/2.0, y_pts[i]) for i in reversed(range(len(y_pts)))]
    p_runner = Polygon(poly_left_edge + poly_right_edge)
    m_runner = extrude_shapely_geom(p_runner, height=0.50)
    m_runner.apply_translation([0, 0, 1.0])
    
    # 4. Terminal blade plunging through floor slit into -Z under the floor
    # At Y in [-15.2, -12.1], extending from Z = 1.5 down to Z = -5.5
    p_blade = Polygon([
        (-15.2, -5.5),
        (-12.1, -5.5),
        (-12.1, 1.5),
        (-15.2, 1.5)
    ])
    m_blade = extrude_shapely_geom(p_blade, height=0.77)
    vb = m_blade.vertices.copy()
    vb_new = np.zeros_like(vb)
    vb_new[:, 0] = vb[:, 2] - 0.77 / 2.0 + dx_slit
    vb_new[:, 1] = vb[:, 0]
    vb_new[:, 2] = vb[:, 1]
    m_blade.vertices = vb_new
    
    all_pieces = [m_left_flat, m_right_flat, m_left_curl, m_right_curl,
                  m_left_wall, m_right_wall, m_riser_l, m_riser_r,
                  m_crossbar, m_runner, m_blade]
    m_tot = trimesh.util.concatenate(all_pieces)
    m_tot.apply_translation([xc, 0.0, 0.0])
    return m_tot

def shade_faces(mesh, base_color='#38bdf8', azdeg=315, altdeg=45):
    """Calculates shaded face colors using a simulated directional light source."""
    v = mesh.vertices
    f = mesh.faces
    v0 = v[f[:, 0]]
    v1 = v[f[:, 1]]
    v2 = v[f[:, 2]]
    normals = np.cross(v1 - v0, v2 - v0)
    norm = np.linalg.norm(normals, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    normals = normals / norm
    
    az = np.radians(azdeg)
    alt = np.radians(altdeg)
    lx = np.cos(alt) * np.cos(az)
    ly = np.cos(alt) * np.sin(az)
    lz = np.sin(alt)
    light_dir = np.array([lx, ly, lz])
    
    intensity = np.dot(normals, light_dir)
    intensity = np.clip(intensity, 0.0, 1.0)
    shade = 0.35 + 0.65 * intensity
    
    base_rgb = np.array(to_rgb(base_color))
    face_colors = shade[:, None] * base_rgb[None, :]
    face_colors = np.clip(face_colors, 0.0, 1.0)
    return face_colors

def render_unified_panel(ax, meshes_and_configs, elev=55, azim=-65, azdeg=315, altdeg=45):
    """Combines all meshes into a single Poly3DCollection so matplotlib sorts all faces properly."""
    all_verts = []
    all_facecolors = []
    all_edgecolors = []
    for m, col, alpha in meshes_and_configs:
        fc = shade_faces(m, base_color=col, azdeg=azdeg, altdeg=altdeg)
        rgba = np.column_stack([fc, np.full(len(fc), alpha)])
        all_verts.append(m.vertices[m.faces])
        all_facecolors.append(rgba)
        all_edgecolors.append(fc * 0.7)
    
    all_verts = np.concatenate(all_verts, axis=0)
    all_facecolors = np.concatenate(all_facecolors, axis=0)
    all_edgecolors = np.concatenate(all_edgecolors, axis=0)
    
    poly = Poly3DCollection(all_verts, facecolors=all_facecolors, edgecolors=all_edgecolors, linewidths=0.1)
    ax.add_collection3d(poly)
    ax.view_init(elev=elev, azim=azim)
    ax.axis('off')
    return poly

def render_assembly_guide():
    print("Generating Updated High-Resolution Visual Assembly Guide (PIP Lever, Breakaway Supports, Monolithic Shrouds)...")
    
    # 1. Build Baseplate CAD Model and Seated PIP Lever
    part_mesh, base_poly = build_exact_3d_model()
    shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)
    
    # 2. Extract Built-In Breakaway Support Structures (Transformed to Flat Assembly Space)
    _, m_tilted, all_fins = build_45deg_supported_part_mesh(part_mesh, base_poly, include_pip_shaft=False)
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    R_inv = trimesh.transformations.rotation_matrix(np.radians(-45.0), [1, 0, 0])
    z_min = part_mesh.copy().apply_transform(R).bounds[0, 2]
    fins_flat = all_fins.copy()
    fins_flat.apply_translation([0, 0, z_min])
    fins_flat.apply_transform(R_inv)
    
    # 3. Build OEM Brass Contact Busbars
    brass_hot = build_brass_contact_mesh(is_hot=True)
    brass_neutral = build_brass_contact_mesh(is_hot=False)
    
    fig = plt.figure(figsize=(26, 18), dpi=200, facecolor='#090d16')
    
    # =========================================================================
    # PANEL 1: STEP 1 - REMOVE BUILT-IN BREAKAWAY SUPPORTS
    # =========================================================================
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#111827')
    ax1.set_title("STEP 1: Remove Built-In Breakaway Supports", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    render_unified_panel(ax1, [
        (part_mesh, '#0284c7', 0.52),
        (shaft_assembled, '#f59e0b', 0.95),
        (fins_flat, '#f43f5e', 0.88)
    ], elev=55, azim=-65)
    
    # Step instructions banner
    ax1.text2D(0.5, 0.88, 
               "1. Peel off monolithic 0.60mm bed pad & 5 vertical backplate support fins from underside\n"
               "2. Snap off twin breakaway struts under backside slit chimneys & bottom snap clips\n"
               "3. Twist off 3x internal lever support struts (off Bracket 4, floor, and through-hole)", 
               transform=ax1.transAxes, color='#fecdd3', fontsize=11.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#0f172a', ec='#f43f5e', lw=1.8))
    
    # Callout: 3x Internal Lever Support Struts
    ax1.text2D(0.80, 0.72, 
               "✂ Twist-Off 3x Internal Lever Struts:\n"
               "• Hub strut off Bracket 4 (0.48mm gap)\n"
               "• Cam strut off floor (0.28mm gap)\n"
               "• Plunger strut through floor hole", 
               transform=ax1.transAxes, color='#fecdd3', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#1e1b4b', ec='#f43f5e', lw=1.5))
    
    # Callout: Bed Pad & 5 Backplate Support Fins
    ax1.text2D(0.18, 0.72, 
               "✂ Peel Bed Pad & 5 Backplate Fins:\n"
               "• 0.60mm monolithic base pad\n"
               "• 5 vertical fins on 45° backplate\n"
               "• Peels along 0.24mm release tines", 
               transform=ax1.transAxes, color='#fca5a5', fontsize=10.0, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#ef4444', lw=1.3))
    
    # Callout: Bottom Snap Clip Struts
    ax1.text2D(0.15, 0.20, 
               "✂ Snip Bottom Clip Struts (2x):\n"
               "• 45° struts under 211.3° & 327.5° shelves\n"
               "• Clean 0.28mm vertical release gap", 
               transform=ax1.transAxes, color='#fca5a5', fontsize=10.0, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#ef4444', lw=1.3))
    
    # Callout: Backside Slit Shroud Struts
    ax1.text2D(0.85, 0.20, 
               "✂ Snap Slit Shroud Struts (2x):\n"
               "• Twin 0.90mm struts under chimneys\n"
               "• 0.28mm gap; leaves slit hole clear", 
               transform=ax1.transAxes, color='#fca5a5', fontsize=10.0, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#ef4444', lw=1.3))
    
    ax1.set_xlim(-24, 24); ax1.set_ylim(-24, 24); ax1.set_zlim(-12, 26)

    # =========================================================================
    # PANEL 2: STEP 2 - FREE & VERIFY PRINT-IN-PLACE (PIP) SAFETY LEVER
    # =========================================================================
    ax2 = fig.add_subplot(2, 2, 2, projection='3d', facecolor='#111827')
    ax2.set_title("STEP 2: Free & Verify Print-in-Place Safety Lever", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    render_unified_panel(ax2, [
        (part_mesh, '#0284c7', 0.65),
        (shaft_assembled, '#f59e0b', 0.98)
    ], elev=55, azim=-65)
    
    # Rotational pivot arrows on cam and plunger
    ax2.plot([7.05, 7.05], [4.5, 6.2], [9.5, 7.0], color='#22c55e', lw=5.0, zorder=100)
    ax2.scatter([7.05], [6.2], [6.8], color='#22c55e', marker='v', s=180, depthshade=False, zorder=100)
    
    ax2.plot([10.28, 10.28], [10.5, 10.5], [2.5, -4.5], color='#38bdf8', lw=5.0, zorder=100)
    ax2.scatter([10.28], [10.5], [-4.8], color='#38bdf8', marker='v', s=180, depthshade=False, zorder=100)
    
    # Step instructions banner
    ax2.text2D(0.5, 0.88, 
               "1. Gently wiggle cam tab to free captive lever from 0.35mm teardrop journal gap\n"
               "2. Verify smooth pivot: Plunger arm swings freely through floor hole to Z ≤ -6.50mm\n"
               "3. Confirm tower rigidity: Monolithic rear cross-tie bridge permanently locks tower spacing", 
               transform=ax2.transAxes, color='#bae6fd', fontsize=11.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#0f172a', ec='#38bdf8', lw=1.8))
    
    # Callout: Enclosed 360° Teardrop Towers
    ax2.text2D(0.20, 0.72, 
               "Enclosed 360° Teardrop Towers:\n"
               "• Apex at Z = 14.19mm\n"
               "• 1.25mm solid arch crown roof\n"
               "• Ø3.50mm bore (0.35mm radial clearance)", 
               transform=ax2.transAxes, color='#38bdf8', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#0284c7', lw=1.3))
    
    # Callout: Monolithic Rear Cross-Tie Bridge
    ax2.text2D(0.80, 0.72, 
               "Monolithic Rear Cross-Tie Bridge:\n"
               "• Permanently spans full 7.70mm gap\n"
               "• 100% eliminates tower spreading\n"
               "• No secondary external clamps needed", 
               transform=ax2.transAxes, color='#38bdf8', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#0284c7', lw=1.3))
    
    # Callout: Input Cam Tab
    ax2.text2D(0.18, 0.20, 
               "Input Cam Tab (105° Direct):\n"
               "• Rotates downward when plug blade enters\n"
               "• Ample >1.0mm clearance to Hot leaves", 
               transform=ax2.transAxes, color='#fef08a', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#f59e0b', lw=1.3))
    
    # Callout: Plunger Through-Hole Travel
    ax2.text2D(0.85, 0.20, 
               "Plunger Output Arm:\n"
               "• Swings through 5.35x5.18mm floor hole\n"
               "• Reaches Z ≤ -6.50mm below floor", 
               transform=ax2.transAxes, color='#fef08a', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#f59e0b', lw=1.3))
    
    ax2.set_xlim(-24, 24); ax2.set_ylim(-24, 24); ax2.set_zlim(-8, 26)

    # =========================================================================
    # PANEL 3: STEP 3 - SEAT OEM BRASS CONTACT BUSBARS
    # =========================================================================
    ax3 = fig.add_subplot(2, 2, 3, projection='3d', facecolor='#111827')
    ax3.set_title("STEP 3: Seat OEM Brass Contacts", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    b_hot_elev = brass_hot.copy()
    b_hot_elev.apply_translation([0, 0, 8.0])
    b_neu_elev = brass_neutral.copy()
    b_neu_elev.apply_translation([0, 0, 8.0])
    
    render_unified_panel(ax3, [
        (part_mesh, '#0284c7', 0.65),
        (shaft_assembled, '#f59e0b', 0.98),
        (b_hot_elev, '#facc15', 0.98),
        (b_neu_elev, '#facc15', 0.98)
    ], elev=55, azim=-65)
    
    # Downward insertion arrows for brass
    for bx in [-6.28, 6.28]:
        ax3.plot([bx, bx], [2.4, 2.4], [19.0, 14.0], color='#facc15', lw=5.0, zorder=100)
        ax3.scatter([bx], [2.4], [13.5], color='#facc15', marker='v', s=180, depthshade=False, zorder=100)
    
    # Step instructions banner
    ax3.text2D(0.5, 0.88, 
               "1. Slide Neutral & Hot brass contacts DOWN into Guide Brackets 1-4\n"
               "2. Horizontal wiping leaves seat snug on 1.15mm floor ribs under bracket hooks\n"
               "3. Terminal blades pass directly into MONOLITHIC backside slit shrouds (No separate inserts!)", 
               transform=ax3.transAxes, color='#fef08a', fontsize=11.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#0f172a', ec='#eab308', lw=1.8))
    
    # Callout: Neutral Contact
    ax3.text2D(0.24, 0.72, 
               "Neutral Contact\n(Slide into Brackets 1 & 2)", 
               transform=ax3.transAxes, color='#fef08a', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))
    
    # Callout: Hot Contact
    ax3.text2D(0.68, 0.72, 
               "Hot Contact\n(Slide into Brackets 3 & 4)", 
               transform=ax3.transAxes, color='#fef08a', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))
    
    # Callout: Retention ribs & hooks
    ax3.text2D(0.18, 0.20, 
               "Seats on 1.15mm Floor Ribs:\n"
               "• Snug fit in guide channel\n"
               "• Trapped under Y = 4.95mm hooks", 
               transform=ax3.transAxes, color='#38bdf8', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#38bdf8', lw=1.2))
    
    # Callout: Monolithic Slit Shrouds (No inserts!)
    ax3.text2D(0.85, 0.20, 
               "MONOLITHIC Backside Slit Shrouds:\n"
               "• 100% integrated (Z = -2.47mm)\n"
               "• Terminal blades pass straight through\n"
               "• NO SEPARATE INSERTS NEEDED!", 
               transform=ax3.transAxes, color='#4ade80', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#064e3b', ec='#22c55e', lw=1.5))
    
    ax3.set_xlim(-24, 24); ax3.set_ylim(-24, 24); ax3.set_zlim(-6, 26)

    # =========================================================================
    # PANEL 4: STEP 4 - ASSEMBLED UNIT & KINEMATIC VERIFICATION
    # =========================================================================
    ax4 = fig.add_subplot(2, 2, 4, projection='3d', facecolor='#111827')
    ax4.set_title("STEP 4: Assembly Complete & Motion Check", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    render_unified_panel(ax4, [
        (part_mesh, '#0284c7', 0.72),
        (shaft_assembled, '#f59e0b', 0.98),
        (brass_hot, '#facc15', 0.95),
        (brass_neutral, '#facc15', 0.95)
    ], elev=55, azim=-65)
    
    # Verification Checklist Banner
    ax4.text2D(0.5, 0.87, 
               "VERIFICATION CHECKLIST:\n"
               "✔ Captive PIP lever pivots freely in enclosed 360° towers (zero binding)\n"
               "✔ Monolithic rear cross-tie bridge rigidly prevents tower spreading\n"
               "✔ Brass contacts seated snug on 1.15mm ribs under retention hooks\n"
               "✔ Cam tab clears Hot leaves with >1.0mm operating margin\n"
               "✔ Terminal blades extend through monolithic backside slit shrouds (Z = -2.47mm)\n"
               "✔ Downward plug push drives plunger to Z ≤ -6.50mm (triggers PCB switch)", 
               transform=ax4.transAxes, color='#4ade80', fontsize=11.0, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#064e3b', ec='#22c55e', lw=1.8))
    
    # Callout: Input Cam Tab
    ax4.text2D(0.85, 0.52, 
               "Input Cam Tab\n(Plug Blade Depresses Here)", 
               transform=ax4.transAxes, color='#fbbf24', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#f59e0b', lw=1.3))
    
    # Callout: Monolithic Rear Bridge
    ax4.text2D(0.20, 0.52, 
               "Monolithic Rear Cross-Tie Bridge\n(Permanent anti-spreading lock)", 
               transform=ax4.transAxes, color='#38bdf8', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#0284c7', lw=1.3))
    
    # Callout: Plunger Output
    ax4.text2D(0.85, 0.18, 
               "Plunger Output (Z ≤ -6.5mm)\n(Triggers PCB Tactile Switch)", 
               transform=ax4.transAxes, color='#f87171', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#ef4444', lw=1.3))
    
    # Callout: Integrated Backside Slit Shrouds
    ax4.text2D(0.20, 0.18, 
               "Integrated Backside Slit Shrouds\n(Terminal blades rigidly guided at Z = -2.47mm)", 
               transform=ax4.transAxes, color='#4ade80', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#064e3b', ec='#22c55e', lw=1.3))
    
    ax4.set_xlim(-24, 24); ax4.set_ylim(-24, 24); ax4.set_zlim(-9, 26)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'print_assembly_guide.png')
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"Assembly guide generated successfully: {out_path}")

if __name__ == '__main__':
    render_assembly_guide()
