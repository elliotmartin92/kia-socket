"""
testing/generate_print_assembly_guide.py
Generates a highly visual, professional step-by-step assembly guide for the outlet sub-housing:
Order of steps: Shaft Rocker -> OEM Brass Contacts -> Slit Inserts -> Complete Unit & Motion Check.
Features unified Poly3DCollection depth-sorted rendering, clean HUD banners, and crisp 3D arrows.
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
from build_part import build_exact_3d_model, build_slit_insert_mesh, extrude_shapely_geom
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
    # Matching the two rounded rectangular pads in zoom_bracket34_photo.png
    y_start = -1.0
    y_end   =  5.8
    y_len   = y_end - y_start # 6.8mm
    
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
    # Stepped risers at Y in [-1.5, -1.0] connecting leaves down to floor
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
    # Runs from crossbar (Y = -2.5) to the slit (Y = -12.10)
    dx_slit = slit_x - xc
    w_run = 1.80
    
    # Smooth S-curve profile
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
    print("Generating High-Resolution Visual Assembly Guide (Order: Shaft -> Brass -> Slit Inserts)...")
    
    # 1. Load / build meshes
    part_mesh, _ = build_exact_3d_model()
    shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)
    
    brass_hot = build_brass_contact_mesh(is_hot=True)
    brass_neutral = build_brass_contact_mesh(is_hot=False)
    
    ins_left = build_slit_insert_mesh(is_right=False)
    ins_right = build_slit_insert_mesh(is_right=True)
    
    fig = plt.figure(figsize=(26, 18), dpi=200, facecolor='#090d16')
    
    # =========================================================================
    # PANEL 1: STEP 1 - INSTALL SAFETY SHAFT ROCKER
    # =========================================================================
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#111827')
    ax1.set_title("STEP 1: Install Safety Shaft Rocker", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    s_elev = shaft_assembled.copy()
    s_elev.apply_translation([0, 0, 8.0])
    
    render_unified_panel(ax1, [
        (part_mesh, '#0284c7', 0.65),
        (s_elev, '#f59e0b', 0.98)
    ], elev=55, azim=-65)
    
    # Downward drop arrows for pins & plunger
    for px in [4.65, 13.85]:
        ax1.plot([px, px], [9.28, 9.28], [20.0, 14.5], color='#ef4444', lw=5.0, zorder=100)
        ax1.scatter([px], [9.28], [14.0], color='#ef4444', marker='v', s=180, depthshade=False, zorder=100)
    ax1.plot([10.28, 10.28], [7.5, 7.5], [9.0, 3.5], color='#fbbf24', lw=4.5, zorder=100)
    ax1.scatter([10.28], [7.5], [3.0], color='#fbbf24', marker='v', s=180, depthshade=False, zorder=100)
    
    ax1.text2D(0.5, 0.88, "1. Angle plunger arm DOWN through 5.35x4.51mm floor hole\n2. Snap Ø2.80mm axle pins into tower cradles (2.60mm throat)", 
               transform=ax1.transAxes, color='#fef08a', fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#0f172a', ec='#fbbf24', lw=1.8))
    
    ax1.text2D(0.08, 0.80, "✂ PRE-STEP:\nTwist or snip breakaway\nfork supports under 4 clips", 
               transform=ax1.transAxes, color='#f43f5e', fontsize=10.5, fontweight='bold', ha='left',
               bbox=dict(boxstyle='round,pad=0.35', fc='#ffe4e6', ec='#e11d48', lw=1.6))
    
    ax1.text2D(0.82, 0.72, "Snap Axle Pins into\nTower Cradles", 
               transform=ax1.transAxes, color='#fca5a5', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#ef4444', lw=1.2))
    
    ax1.text2D(0.85, 0.20, "Plunger Arm\n(Passes through floor hole)", 
               transform=ax1.transAxes, color='#fde047', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#fbbf24', lw=1.2))
    
    ax1.set_xlim(-24, 24); ax1.set_ylim(-24, 24); ax1.set_zlim(-6, 26)

    # =========================================================================
    # PANEL 2: STEP 2 - SEAT OEM BRASS CONTACT BUSBARS
    # =========================================================================
    ax2 = fig.add_subplot(2, 2, 2, projection='3d', facecolor='#111827')
    ax2.set_title("STEP 2: Seat OEM Brass Contacts", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    b_hot_elev = brass_hot.copy()
    b_hot_elev.apply_translation([0, 0, 8.0])
    b_neu_elev = brass_neutral.copy()
    b_neu_elev.apply_translation([0, 0, 8.0])
    
    render_unified_panel(ax2, [
        (part_mesh, '#0284c7', 0.65),
        (shaft_assembled, '#f59e0b', 0.98),
        (b_hot_elev, '#facc15', 0.98),
        (b_neu_elev, '#facc15', 0.98)
    ], elev=55, azim=-65)
    
    # Downward insertion arrows for brass
    for bx in [-6.28, 6.28]:
        ax2.plot([bx, bx], [2.4, 2.4], [19.0, 14.0], color='#facc15', lw=5.0, zorder=100)
        ax2.scatter([bx], [2.4], [13.5], color='#facc15', marker='v', s=180, depthshade=False, zorder=100)
    
    ax2.text2D(0.5, 0.88, "1. Slide Neutral & Hot brass contacts DOWN into Brackets 1-4\n2. Horizontal wiping leaves seat snug in brackets; S-curve sits on floor\n3. Terminal blades pass through floor slits to protrude underneath", 
               transform=ax2.transAxes, color='#fef08a', fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#0f172a', ec='#eab308', lw=1.8))
    
    ax2.text2D(0.24, 0.72, "Neutral Contact\n(Slide into Brackets 1 & 2)", 
               transform=ax2.transAxes, color='#fef08a', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))
    
    ax2.text2D(0.68, 0.72, "Hot Contact\n(Slide into Brackets 3 & 4)", 
               transform=ax2.transAxes, color='#fef08a', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))
    
    ax2.text2D(0.85, 0.22, "Terminal blades pass\nthrough floor slits\nprotruding underneath", 
               transform=ax2.transAxes, color='#38bdf8', fontsize=10, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#38bdf8', lw=1.2))
    
    ax2.set_xlim(-24, 24); ax2.set_ylim(-24, 24); ax2.set_zlim(-6, 26)

    # =========================================================================
    # PANEL 3: STEP 3 - PRESS-FIT BACKSIDE SLIT INSERTS (BOTTOM VIEW)
    # =========================================================================
    ax3 = fig.add_subplot(2, 2, 3, projection='3d', facecolor='#111827')
    ax3.set_title("STEP 3: Press-Fit Backside Slit Inserts (Bottom View)", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    il_exp = ins_left.copy()
    il_exp.apply_translation([-7.853, -13.589, -10.0])
    ir_exp = ins_right.copy()
    ir_exp.apply_translation([8.453, -13.589, -10.0])
    
    render_unified_panel(ax3, [
        (part_mesh, '#64748b', 0.60),
        (brass_hot, '#facc15', 0.90),
        (brass_neutral, '#facc15', 0.90),
        (il_exp, '#10b981', 0.98),
        (ir_exp, '#10b981', 0.98)
    ], elev=-50, azim=-90, altdeg=-45)
    
    # Bold Green upward insertion arrows
    for ix in [-7.853, 8.453]:
        ax3.plot([ix, ix], [-13.589, -13.589], [-7.5, -2.5], color='#22c55e', lw=5.0, zorder=100)
        ax3.scatter([ix], [-13.589], [-2.0], color='#22c55e', marker='^', s=180, depthshade=False, zorder=100)
    
    ax3.text2D(0.5, 0.88, "▲ Press straight UP over protruding brass contact blades\n▲ 45° chamfered key guarantees 1-way insertion\n▲ Flange seats flush with Z = 0.00mm floor", 
               transform=ax3.transAxes, color='#38bdf8', fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#0f172a', ec='#38bdf8', lw=1.8))
    
    ax3.text2D(0.18, 0.12, "Left Insert\n(45° Polarized Key)", 
               transform=ax3.transAxes, color='#4ade80', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#064e3b', ec='#22c55e', lw=1.3))
    
    ax3.text2D(0.82, 0.12, "Right Insert\n(45° Polarized Key)", 
               transform=ax3.transAxes, color='#4ade80', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#064e3b', ec='#22c55e', lw=1.3))
    
    ax3.set_xlim(-22, 22); ax3.set_ylim(-22, 18); ax3.set_zlim(-18, 16)

    # =========================================================================
    # PANEL 4: STEP 4 - ASSEMBLED UNIT & KINEMATIC VERIFICATION
    # =========================================================================
    ax4 = fig.add_subplot(2, 2, 4, projection='3d', facecolor='#111827')
    ax4.set_title("STEP 4: Assembly Complete & Motion Check", color='#f8fafc', fontsize=18, fontweight='bold', pad=22)
    
    il_seat = ins_left.copy()
    il_seat.apply_translation([-7.853, -13.589, 0.0])
    ir_seat = ins_right.copy()
    ir_seat.apply_translation([8.453, -13.589, 0.0])
    
    render_unified_panel(ax4, [
        (part_mesh, '#0284c7', 0.75),
        (shaft_assembled, '#f59e0b', 0.98),
        (brass_hot, '#facc15', 0.95),
        (brass_neutral, '#facc15', 0.95),
        (il_seat, '#10b981', 0.95),
        (ir_seat, '#10b981', 0.95)
    ], elev=55, azim=-65)
    
    ax4.text2D(0.5, 0.87, "VERIFICATION CHECKLIST:\n✔ Rocker axle locked in 240° cradles\n✔ Brass seated on ribs under bracket hooks\n✔ Cam sits in front of Hot leaves without bind\n✔ Slit inserts flush at bottom datum over blades", 
               transform=ax4.transAxes, color='#4ade80', fontsize=11.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.45', fc='#064e3b', ec='#22c55e', lw=1.8))
    
    ax4.text2D(0.85, 0.48, "Input Cam Tab\n(Plug Blade Depresses Here)", 
               transform=ax4.transAxes, color='#fbbf24', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#f59e0b', lw=1.3))
    
    ax4.text2D(0.85, 0.18, "Plunger Output (Z ≤ -6.5mm)\n(Triggers PCB Tactile Switch)", 
               transform=ax4.transAxes, color='#f87171', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#ef4444', lw=1.3))
    
    ax4.set_xlim(-24, 24); ax4.set_ylim(-24, 24); ax4.set_zlim(-9, 26)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'print_assembly_guide.png')
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"Assembly guide generated successfully: {out_path}")

if __name__ == '__main__':
    render_assembly_guide()
