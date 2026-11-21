"""
testing/generate_side_diagram.py
Generate high-resolution, millimeter-accurate side-on diagrams of the baseplate (towers omitted)
with the safety interlock rocker mechanism (cam arm, hub, and plunger) fully visible in position
specifically designed for manual engineering annotation and review.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle, Polygon as MplPolygon, FancyArrowPatch, Circle
from shapely.geometry import Polygon as SgPolygon, MultiPolygon, box, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate

from build_part import (
    get_exact_base_polygon, extrude_shapely_geom, BASE_THICK, OUTER_WALL_HEIGHT,
    OUTER_WALL_THICK, create_arch_wall_poly, create_grid_ribs_poly,
    create_all_brackets_poly, build_chamfered_seating_ribs_mesh,
    build_center_curved_feature_mesh, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_ARM_WIDTH, CLIP_HOOK_DEPTH_BY_ANGLE, CLIP_HOOK_DEPTH,
    CLIP_SHELF_Z_BY_ANGLE, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_BLUNT_HEIGHT,
    CLIP_CROWN_EASE, CLIP_GAP_DEPTH, CLIP_ROOT_RADIUS, CLIP_SLOT_CLEARANCE,
    create_frustum_mesh, INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X,
    INSERT_BODY_LEN_Y, SLIT_BOSS_HEIGHT, SLIT_W_X, SLIT_LEN_Y
)
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE

def build_plate_without_towers():
    """Builds the complete baseplate solid model, strictly omitting the support towers."""
    base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
    mesh_base = extrude_shapely_geom(base_poly, height=BASE_THICK)

    # In-place backside slit chimneys
    cx_left, cx_right, cy_sock = -7.853, 8.453, -13.589
    shroud_l = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, -SLIT_BOSS_HEIGHT, 0.0)
    shroud_l.apply_translation([cx_left, cy_sock, 0.0])
    shroud_r = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, -SLIT_BOSS_HEIGHT, 0.0)
    shroud_r.apply_translation([cx_right, cy_sock, 0.0])

    slit_cutter_l = extrude_shapely_geom(box(cx_left - SLIT_W_X/2, cy_sock - SLIT_LEN_Y/2, cx_left + SLIT_W_X/2, cy_sock + SLIT_LEN_Y/2), height=SLIT_BOSS_HEIGHT + 2.0)
    slit_cutter_l.apply_translation([0, 0, -SLIT_BOSS_HEIGHT - 1.0])
    shroud_l_hollow = shroud_l.difference(slit_cutter_l, engine='manifold')

    slit_cutter_r = extrude_shapely_geom(box(cx_right - SLIT_W_X/2, cy_sock - SLIT_LEN_Y/2, cx_right + SLIT_W_X/2, cy_sock + SLIT_LEN_Y/2), height=SLIT_BOSS_HEIGHT + 2.0)
    slit_cutter_r.apply_translation([0, 0, -SLIT_BOSS_HEIGHT - 1.0])
    shroud_r_hollow = shroud_r.difference(slit_cutter_r, engine='manifold')
    mesh_shrouds = trimesh.util.concatenate([shroud_l_hollow, shroud_r_hollow])

    # Outer wall
    inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_poly)
    arch_wall_poly = create_arch_wall_poly()
    all_walls_poly = unary_union([wall_poly, arch_wall_poly])
    mesh_wall = extrude_shapely_geom(all_walls_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
    mesh_wall.apply_translation([0, 0, BASE_THICK])

    # Grid ribs
    all_ribs_poly = create_grid_ribs_poly(base_poly, outer_body_poly)
    bridge_box = box(13.10, 8.5, 25.0, 14.0)
    bridge_ribs_poly = all_ribs_poly.intersection(bridge_box)
    normal_ribs_poly = all_ribs_poly.difference(bridge_box)
    mesh_normal_ribs = extrude_shapely_geom(normal_ribs_poly, height=0.50)
    mesh_normal_ribs.apply_translation([0, 0, BASE_THICK])
    mesh_bridge_ribs = extrude_shapely_geom(bridge_ribs_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
    mesh_bridge_ribs.apply_translation([0, 0, BASE_THICK])
    mesh_ribs = trimesh.util.concatenate([mesh_normal_ribs, mesh_bridge_ribs])

    # Guide brackets
    brackets_poly = create_all_brackets_poly()
    mesh_brackets = extrude_shapely_geom(brackets_poly, height=4.60)
    mesh_brackets.apply_translation([0, 0, BASE_THICK])

    # Chamfered seating ribs
    mesh_seating_ribs = build_chamfered_seating_ribs_mesh()

    # Snap clips (outer wall hooks + flex slots)
    slot_cuts = []
    hook_meshes = []
    slot_z_bot = OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH
    z_root_center = slot_z_bot + CLIP_ROOT_RADIUS
    slot_t = CLIP_SLOT_CLEARANCE

    for angle_deg in CLIP_ANGLES:
        center_rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        d_theta = CLIP_ARM_WIDTH / r_est
        slot_d_theta = slot_t / r_est
        hook_depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        stem_h = CLIP_SHELF_Z_BY_ANGLE.get(angle_deg, CLIP_HEIGHT - CLIP_HOOK_HEIGHT)
        for th_slot in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
            slot_p = np.array([np.cos(th_slot), np.sin(th_slot)]) * r_est
            rot_mat = trimesh.transformations.rotation_matrix(th_slot, [0, 0, 1])
            box_h = (OUTER_WALL_HEIGHT + 1.0) - z_root_center
            s_box = trimesh.creation.box([OUTER_WALL_THICK * 4.0, slot_t, box_h])
            s_box.apply_transform(rot_mat)
            s_box.apply_translation([slot_p[0], slot_p[1], z_root_center + box_h / 2.0])
            cyl = trimesh.creation.cylinder(radius=CLIP_ROOT_RADIUS, height=OUTER_WALL_THICK * 4.0, sections=16)
            rot_to_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
            cyl.apply_transform(rot_to_x)
            cyl.apply_transform(rot_mat)
            cyl.apply_translation([slot_p[0], slot_p[1], z_root_center])
            s_cutter = trimesh.util.concatenate([s_box, cyl])
            slot_cuts.append(s_cutter)

        N = 32
        theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
        half_w = CLIP_ARM_WIDTH / 2.0
        outer_coords, shelf_coords, inner_overlap_coords = [], [], []
        for th in theta_vals:
            ray_dir = np.array([np.cos(th), np.sin(th)])
            ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
            inter_out = outer_body_poly.exterior.intersection(ray)
            if inter_out.geom_type == 'Point':
                po = np.array([inter_out.x, inter_out.y])
            elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
                po = np.array([inter_out.x, inter_out.y]) if hasattr(inter_out, 'x') else np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
            else:
                po = ray_dir * r_est
            n_dir = po / np.linalg.norm(po)
            t = (th - center_rad) * r_est
            frac = abs(t / half_w)
            eff_depth = hook_depth - CLIP_CROWN_EASE * (frac ** 2.0)
            ps = po + n_dir * eff_depth
            p_in = po - n_dir * 0.25
            outer_coords.append(po)
            shelf_coords.append(ps)
            inner_overlap_coords.append(p_in)
        inner_overlap_coords = np.array(inner_overlap_coords)
        shelf_coords = np.array(shelf_coords)
        v0 = np.column_stack([inner_overlap_coords, np.full(N, stem_h)])
        v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
        v_face = np.column_stack([shelf_coords, np.full(N, stem_h + CLIP_BLUNT_HEIGHT)])
        v2 = np.column_stack([inner_overlap_coords, np.full(N, CLIP_HEIGHT)])
        hook_verts = np.vstack([v0, v1, v_face, v2])
        hook_faces = []
        for i in range(N - 1):
            hook_faces.append([i, N + i + 1, N + i])
            hook_faces.append([i, i + 1, N + i + 1])
            hook_faces.append([N + i, 2*N + i + 1, 2*N + i])
            hook_faces.append([N + i, N + i + 1, 2*N + i + 1])
            hook_faces.append([2*N + i, 3*N + i + 1, 3*N + i])
            hook_faces.append([2*N + i, 2*N + i + 1, 3*N + i + 1])
            hook_faces.append([3*N + i, i + 1, i])
            hook_faces.append([3*N + i, 3*N + i + 1, i + 1])
        hook_faces.append([0, 2*N, 3*N])
        hook_faces.append([0, N, 2*N])
        hook_faces.append([N - 1, 3*N - 1, 2*N - 1])
        hook_faces.append([N - 1, 4*N - 1, 3*N - 1])
        hook_mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
        if hook_mesh.volume < 0:
            hook_mesh.faces = np.fliplr(hook_mesh.faces)
        hook_meshes.append(hook_mesh)

    for hm in hook_meshes:
        try:
            mesh_wall = mesh_wall.union(hm, engine='manifold')
        except Exception:
            pass
    all_slot_cuts = trimesh.util.concatenate(slot_cuts)
    mesh_wall = mesh_wall.difference(all_slot_cuts, engine='manifold')

    # Center curved D-wall
    mesh_curved_feat = build_center_curved_feature_mesh()

    # Note: Support towers (mesh_towers_assembly) are explicitly omitted per user request!
    plate_mesh = trimesh.util.concatenate([
        mesh_base, mesh_shrouds, mesh_wall, mesh_ribs,
        mesh_brackets, mesh_seating_ribs, mesh_curved_feat
    ])
    
    parts = {
        'base': mesh_base,
        'shrouds': mesh_shrouds,
        'wall': mesh_wall,
        'ribs': mesh_ribs,
        'brackets': mesh_brackets,
        'seating_ribs': mesh_seating_ribs,
        'curved_feat': mesh_curved_feat,
        'full': plate_mesh
    }
    return parts, base_poly, outer_body_poly, hole_info

def project_mesh_to_2d(mesh, plane='yz'):
    """Computes exact 2D outline polygon of a 3D mesh projected onto YZ or XZ plane."""
    coords = [1, 2] if plane == 'yz' else [0, 2]
    verts = mesh.vertices[:, coords]
    polys = []
    for f in mesh.faces:
        p = SgPolygon(verts[f])
        if p.is_valid and p.area > 1e-4:
            polys.append(p)
    return unary_union(polys)

def plot_shapely_geom(ax, geom, facecolor, edgecolor, linewidth=1.5, alpha=0.85, label=None, linestyle='-', zorder=3):
    """Plots a Shapely Polygon or MultiPolygon onto matplotlib axes."""
    if geom is None or geom.is_empty:
        return
    geoms = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for i, g in enumerate(geoms):
        lbl = label if i == 0 else None
        patch = MplPolygon(np.array(g.exterior.coords), facecolor=facecolor,
                           edgecolor=edgecolor, linewidth=linewidth, alpha=alpha,
                           linestyle=linestyle, label=lbl, zorder=zorder)
        ax.add_patch(patch)
        for interior in g.interiors:
            hole_patch = MplPolygon(np.array(interior.coords), facecolor='white',
                                    edgecolor=edgecolor, linewidth=linewidth,
                                    linestyle='--', zorder=zorder+1)
            ax.add_patch(hole_patch)

def generate_annotatable_side_view(output_path):
    """
    Generates a dedicated, large, high-contrast, millimeter-accurate side-on (Y-Z) diagram
    with the safety interlock rocker (cam arm, hub, plunger) fully visible in position,
    with generous margins and clean annotation space.
    """
    parts, base_poly, outer_body_poly, hole_info = build_plate_without_towers()
    shaft_subparts = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False, return_subparts=True)
    
    fig, ax = plt.subplots(figsize=(26, 16), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Compute 2D projections of baseplate features onto Y-Z plane
    poly_full = project_mesh_to_2d(parts['full'], 'yz')
    poly_curved = project_mesh_to_2d(parts['curved_feat'], 'yz')
    poly_wall = project_mesh_to_2d(parts['wall'], 'yz')
    poly_brackets = project_mesh_to_2d(parts['brackets'], 'yz')
    poly_base = project_mesh_to_2d(parts['base'], 'yz')
    poly_shrouds = project_mesh_to_2d(parts['shrouds'], 'yz')

    # Compute 2D projections of rocker mechanism features
    poly_cam = project_mesh_to_2d(shaft_subparts['cam'], 'yz')
    poly_plunger = project_mesh_to_2d(shaft_subparts['plunger'], 'yz')
    poly_hub = project_mesh_to_2d(shaft_subparts['hub'], 'yz')

    # 1. Background Grid & Coordinates
    ax.set_xlim(-26.0, 28.0)
    ax.set_ylim(-9.5, 17.5)
    
    # 1mm minor grid and 5mm major grid
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))

    ax.grid(which='major', color='#b0bec5', linestyle='-', linewidth=0.9, alpha=0.8, zorder=1)
    ax.grid(which='minor', color='#eceff1', linestyle=':', linewidth=0.5, alpha=0.9, zorder=1)

    # 2. Key Datum Lines
    # Z = 0.00 Base Datum
    ax.axhline(0.00, color='#263238', linestyle='-', linewidth=1.5, zorder=2)
    ax.text(-25.2, 0.18, 'Z = 0.00 mm (Base Datum / Floor Bottom)', color='#263238', fontsize=9.0, fontweight='bold', zorder=5)

    # Z = 1.00 Top of Floor
    ax.axhline(1.00, color='#546e7a', linestyle='--', linewidth=1.0, zorder=2)
    ax.text(-25.2, 1.18, 'Z = 1.00 mm (Top of Floor Plate / 1.0mm thickness)', color='#546e7a', fontsize=8.5, zorder=5)

    # Z = 4.72 Snap Hook Shelf Datum
    ax.axhline(4.72, color='#0288d1', linestyle=':', linewidth=1.1, zorder=2)
    ax.text(17.5, 4.88, 'Z = 4.72 mm (Snap Hook Shelf)', color='#0288d1', fontsize=8.5, fontweight='bold', zorder=5)

    # Z = 6.77 Outer Perimeter Wall Top
    ax.axhline(6.77, color='#1565c0', linestyle='--', linewidth=1.0, zorder=2)
    ax.text(-25.2, 6.95, 'Z = 6.77 mm (Outer Wall & Clip Tops)', color='#1565c0', fontsize=8.5, zorder=5)

    # Z = 10.50 Center Curved D-Wall Apex
    ax.axhline(10.50, color='#6a1b9a', linestyle='--', linewidth=1.0, zorder=2)
    ax.text(-25.2, 10.65, 'Z = 10.50 mm (Center Curved D-Wall Apex)', color='#6a1b9a', fontsize=8.5, fontweight='bold', zorder=5)

    # Z = -2.47 Backside Slit Chimneys
    ax.axhline(-2.47, color='#2e7d32', linestyle='--', linewidth=1.0, zorder=2)
    ax.text(-25.2, -2.32, 'Z = -2.47 mm (Backside Slit Chimneys)', color='#2e7d32', fontsize=8.5, zorder=5)

    # Z = -7.00 Plunger Extended Reach Tip
    ax.axhline(-7.00, color='#b91c1c', linestyle=':', linewidth=1.2, zorder=2)
    ax.text(-25.2, -6.82, 'Z = -7.00 mm (Extended Plunger Switch Actuation Tip)', color='#b91c1c', fontsize=8.5, fontweight='bold', zorder=5)

    # Y = 0.00 Center Datum
    ax.axvline(0.00, color='#37474f', linestyle='-', linewidth=1.2, zorder=2)
    ax.text(0.2, -8.8, 'Y = 0.00 mm (Center Datum)', color='#37474f', fontsize=8.5, rotation=90, zorder=5)

    # 3. Baseplate Geometry Layers (Background & Structural Context)
    # Full Baseplate Silhouette Outline (Soft Background Fill)
    plot_shapely_geom(ax, poly_full, facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1.2, alpha=0.4, label='Baseplate Silhouette', zorder=2)

    # Floor Base (Z: 0 to 1.0mm)
    plot_shapely_geom(ax, poly_base, facecolor='#94a3b8', edgecolor='#334155', linewidth=1.5, alpha=0.85, label='Floor Plate (1.00mm thick)', zorder=3)

    # Backside Slit Bosses (Z: -2.47 to 0.0mm)
    plot_shapely_geom(ax, poly_shrouds, facecolor='#a7f3d0', edgecolor='#059669', linewidth=1.5, alpha=0.9, label='Backside Slit Chimneys (-2.47mm)', zorder=3)

    # Outer Perimeter Wall & Clips (Z: 1.0 to 6.77mm)
    plot_shapely_geom(ax, poly_wall, facecolor='#bae6fd', edgecolor='#0369a1', linewidth=1.4, alpha=0.65, label='Perimeter Wall (6.77mm)', zorder=3)

    # Guide Brackets (Z: 1.0 to 5.60mm)
    plot_shapely_geom(ax, poly_brackets, facecolor='#fed7aa', edgecolor='#ea580c', linewidth=1.2, alpha=0.6, label='Guide Brackets (5.60mm)', zorder=3)

    # Center Curved D-Wall (Z: 1.0 to 10.50mm)
    plot_shapely_geom(ax, poly_curved, facecolor='#e9d5ff', edgecolor='#7e22ce', linewidth=1.8, alpha=0.8, label='Center Curved D-Wall (10.50mm)', zorder=3)

    # Re-draw clean through hole opening in the floor (Z: 0 to 1.0 mm, Y: 8.57 to 13.75 mm)
    ax.add_patch(Rectangle((8.570, 0.00), 13.750 - 8.570, 1.00, facecolor='#ffffff', edgecolor='#dc2626',
                           linewidth=1.8, linestyle='--', zorder=4))

    # Re-draw through slits in the backside chimney (Z: -2.47 to 1.00 mm, Y: -15.29 to -11.89 mm)
    ax.add_patch(Rectangle((-15.289, -2.47), 3.40, 3.47, facecolor='#ffffff', edgecolor='#059669',
                           linewidth=1.4, linestyle=':', alpha=0.9, zorder=4))

    # 4. Plug Blade Insertion Corridor & Contact Action
    # Plug Blade Corridor (Y in [0.5, 4.5] mm, inserting downward from +Z)
    blade_poly = SgPolygon([(0.5, 7.55), (4.5, 7.55), (4.5, 17.0), (0.5, 17.0)])
    plot_shapely_geom(ax, blade_poly, facecolor='#bfdbfe', edgecolor='#2563eb', linewidth=1.5,
                      alpha=0.35, linestyle='--', label='Right Plug Blade Corridor (Engages Cam)', zorder=3)
    ax.annotate('US AC Plug Right Blade\nInsertion Corridor (Downwards)',
                xy=(2.5, 14.5), xytext=(2.5, 16.8),
                fontsize=8.5, fontweight='bold', color='#1d4ed8', ha='center',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#eff6ff', edgecolor='#3b82f6'),
                arrowprops=dict(arrowstyle='->', color='#2563eb', lw=1.5), zorder=7)

    # 5. SAFETY INTERLOCK ROCKER MECHANISM (PROMINENT HIGHLIGHT)
    # Plunger Arm (swings through floor to Z = -7.00mm)
    plot_shapely_geom(ax, poly_plunger, facecolor='#fb923c', edgecolor='#c2410c', linewidth=2.0, alpha=0.90,
                      label='Extended Output Plunger (Z to -7.00mm)', zorder=6)

    # Shaft Hub Barrel (Ø4.20mm at Y=9.279, Z=12.590)
    plot_shapely_geom(ax, poly_hub, facecolor='#fef08a', edgecolor='#ca8a04', linewidth=2.0, alpha=0.95,
                      label='Shaft Hub Barrel (Ø4.20mm)', zorder=6)

    # CAM ARM (The Primary Feature requested!)
    plot_shapely_geom(ax, poly_cam, facecolor='#f59e0b', edgecolor='#b45309', linewidth=2.5, alpha=0.95,
                      label='Safety Interlock Cam Arm (Apex Y=2.45, Z=7.55mm)', zorder=7)

    # Shaft Axle Pivot Datum
    y_axle, z_axle = Y_AXLE, Z_AXLE
    ax.scatter([y_axle], [z_axle], marker='+', s=250, c='#dc2626', linewidth=2.8, zorder=8)
    ax.scatter([y_axle], [z_axle], marker='o', s=180, facecolors='none', edgecolors='#dc2626', linewidth=1.8, linestyle='--', zorder=8)
    ax.annotate(f'Shaft Axle Datum (Y={y_axle:.2f}, Z={z_axle:.2f})\n[SUPPORT TOWERS OMITTED]',
                xy=(y_axle, z_axle), xytext=(y_axle + 2.5, z_axle + 1.8),
                fontsize=9.0, fontweight='bold', color='#c62828',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffebee', edgecolor='#c62828', alpha=0.95),
                arrowprops=dict(arrowstyle='->', color='#c62828', lw=1.5), zorder=8)

    # Cam Apex Marker & Callout
    cam_apex_y, cam_apex_z = 2.45, 7.55
    ax.scatter([cam_apex_y], [cam_apex_z], marker='*', s=220, c='#b45309', edgecolors='#ffffff', linewidth=1.2, zorder=8)
    ax.annotate(f'Cam Arm Apex Nose (Y = {cam_apex_y:.2f}, Z = {cam_apex_z:.2f} mm)\n'
                f'Engaged by Plug Blade (+0.35mm air gap to brass flare)',
                xy=(cam_apex_y, cam_apex_z), xytext=(-10.0, 4.0),
                fontsize=9.0, fontweight='bold', color='#92400e',
                bbox=dict(boxstyle='round,pad=0.35', facecolor='#fef3c7', edgecolor='#d97706', linewidth=1.4),
                arrowprops=dict(arrowstyle='->', color='#b45309', lw=1.6), zorder=8)

    # Plunger Tip Callout
    plunger_tip_y, plunger_tip_z = 10.95, -7.00
    ax.scatter([plunger_tip_y], [plunger_tip_z], marker='v', s=180, c='#c2410c', zorder=8)
    ax.annotate(f'Plunger Tip (Y = {plunger_tip_y:.2f}, Z = {plunger_tip_z:.2f} mm)\n'
                f'Deep Reach: Actuates Tactile Switch at Z ≤ -6.50mm',
                xy=(plunger_tip_y, plunger_tip_z), xytext=(13.0, -8.2),
                fontsize=8.5, fontweight='bold', color='#9a3412',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffedd5', edgecolor='#ea580c'),
                arrowprops=dict(arrowstyle='->', color='#c2410c', lw=1.5), zorder=8)

    # Kinematic Motion Ghost (6.0° CCW Rotation under Plug Insertion)
    poly_cam_rot = rotate(poly_cam, 6.0, origin=(y_axle, z_axle))
    poly_plunger_rot = rotate(poly_plunger, 6.0, origin=(y_axle, z_axle))
    plot_shapely_geom(ax, poly_cam_rot, facecolor='#fde68a', edgecolor='#d97706', linewidth=1.2,
                      alpha=0.35, linestyle=':', zorder=5)
    plot_shapely_geom(ax, poly_plunger_rot, facecolor='#fed7aa', edgecolor='#ea580c', linewidth=1.2,
                      alpha=0.35, linestyle=':', zorder=5)
    
    # Kinematic rotation arc arrow
    arc_rad = 4.2
    arc_angles = np.linspace(math.pi * 0.95, math.pi * 1.15, 20)
    arc_ys = y_axle + arc_rad * np.cos(arc_angles)
    arc_zs = z_axle + arc_rad * np.sin(arc_angles)
    ax.plot(arc_ys, arc_zs, color='#d97706', linestyle='--', linewidth=1.5, zorder=7)
    ax.annotate('', xy=(arc_ys[-1], arc_zs[-1]), xytext=(arc_ys[-3], arc_zs[-3]),
                arrowprops=dict(arrowstyle='->', color='#d97706', lw=2.0), zorder=7)
    ax.text(y_axle - 4.8, z_axle - 0.2, 'CCW Stroke\n(θ ≈ 3°–7.5°)', fontsize=7.5, fontweight='bold',
            color='#b45309', ha='center', va='center')

    # Tactile Switch Zone Indicator
    ax.add_patch(Rectangle((11.4, -7.5), 2.0, 5.0, facecolor='#fff9c4', edgecolor='#fbc02d',
                           linewidth=1.2, linestyle=':', alpha=0.75, zorder=3))
    ax.text(12.4, -5.0, 'PCB Tactile Switch\n(Station Y=12.40mm)', fontsize=7.5, ha='center', va='center', color='#f57f17', fontweight='bold')

    # Air Gap Dimension between D-Wall Foot and Cam Apex
    # D-wall foot is at Y = -2.45, Cam Apex is at Y = 2.45. Gap = 4.90mm in Y!
    dim_gap_z = 2.15
    ax.plot([-2.45, 2.45], [dim_gap_z, dim_gap_z], color='#6b21a8', linewidth=1.4, linestyle='-', zorder=7)
    ax.plot([-2.45, -2.45], [dim_gap_z - 0.3, dim_gap_z + 0.3], color='#6b21a8', linewidth=1.4, zorder=7)
    ax.plot([2.45, 2.45], [dim_gap_z - 0.3, dim_gap_z + 0.3], color='#6b21a8', linewidth=1.4, zorder=7)
    ax.text(0.0, dim_gap_z + 0.3, 'CLEAR THROAT GAP = 4.90 mm (Plug Blade Path)', fontsize=7.5,
            fontweight='bold', ha='center', color='#581c87', zorder=8)

    # 6. Title Block & Engineering Metadata
    title_box = dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#64748b', linewidth=1.5)
    ax.text(-25.0, 16.5,
            'AUTOMOTIVE 120V AC OUTLET — BASEPLATE & CAM ARM LATERAL VIEW (Y-Z PLANE)\n'
            'TOWERS OMITTED • CAM ARM & PLUNGER IN FULL ASSEMBLY POSITION • 1:1 MM GRID',
            fontsize=11.5, fontweight='heavy', color='#0f172a', bbox=title_box, va='top', zorder=9)

    badge_box = dict(boxstyle='round,pad=0.4', facecolor='#fef2f2', edgecolor='#ef4444', linewidth=1.5)
    ax.text(26.5, 16.5,
            'TOWERS OMITTED FOR UNOBSTRUCTED VIEW\n'
            'CAM ARM & PLUNGER VISIBLE FOR ANNOTATION',
            fontsize=9.0, fontweight='heavy', color='#b91c1c', bbox=badge_box, ha='right', va='top', zorder=9)

    # Axes styling
    ax.set_xlabel('Y Coordinate (Depth / Insertion Direction) [mm]', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel('Z Coordinate (Elevation Datum: Z = 0.00 mm) [mm]', fontsize=11, fontweight='bold', labelpad=8)
    
    # Secondary X and Y axes on top and right for easy annotation measurement
    ax_top = ax.secondary_xaxis('top')
    ax_top.set_xlabel('Y Coordinate [mm]', fontsize=9.5, fontweight='semibold', labelpad=6)
    ax_top.xaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax_top.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))

    ax_right = ax.secondary_yaxis('right')
    ax_right.set_ylabel('Z Coordinate [mm]', fontsize=9.5, fontweight='semibold', labelpad=6)
    ax_right.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax_right.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))

    # Legend in lower right corner
    leg = ax.legend(loc='lower right', framealpha=0.95, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.2)
    leg.set_zorder(9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated annotatable side view with cam arm: {output_path}")

def generate_midline_cross_section(output_path):
    """
    Generates a midline cross-section cut (Y-Z plane sliced at X=0) with cam arm projected
    showing wall thicknesses, internal floor pocket, through-hole, and D-wall section.
    """
    parts, base_poly, outer_body_poly, hole_info = build_plate_without_towers()
    shaft_subparts = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False, return_subparts=True)
    
    fig, ax = plt.subplots(figsize=(24, 14), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    ax.set_xlim(-26.0, 28.0)
    ax.set_ylim(-9.5, 17.5)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))

    ax.grid(which='major', color='#cbd5e1', linestyle='-', linewidth=0.8, alpha=0.7, zorder=1)
    ax.grid(which='minor', color='#f1f5f9', linestyle=':', linewidth=0.5, alpha=0.8, zorder=1)

    # Datum lines
    ax.axhline(0.00, color='#1e293b', linestyle='-', linewidth=1.4, zorder=2)
    ax.axhline(1.00, color='#64748b', linestyle='--', linewidth=1.0, zorder=2)
    ax.axhline(6.77, color='#0284c7', linestyle='--', linewidth=1.0, zorder=2)
    ax.axhline(10.50, color='#7c3aed', linestyle='--', linewidth=1.0, zorder=2)
    ax.axhline(-7.00, color='#b91c1c', linestyle=':', linewidth=1.1, zorder=2)
    ax.axvline(0.00, color='#475569', linestyle='-', linewidth=1.2, zorder=2)

    # Slice full part at X=0
    slice_x0 = parts['full'].section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    if slice_x0:
        for loop in slice_x0.discrete:
            ax.fill(loop[:, 1], loop[:, 2], facecolor='#93c5fd', edgecolor='#1d4ed8', linewidth=1.8, alpha=0.75, hatch='///', zorder=3)

    # Slice Center Curved D-wall specifically to highlight solid core
    slice_d = parts['curved_feat'].section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    if slice_d:
        for loop in slice_d.discrete:
            ax.fill(loop[:, 1], loop[:, 2], facecolor='#c084fc', edgecolor='#6b21a8', linewidth=2.0, alpha=0.85, hatch='\\\\\\', zorder=4)

    # Plot Cam Arm & Plunger in elevation (since cam arm spans X in [5.35, 7.15], it sits in the channel behind/in front of X=0)
    poly_cam = project_mesh_to_2d(shaft_subparts['cam'], 'yz')
    poly_plunger = project_mesh_to_2d(shaft_subparts['plunger'], 'yz')
    poly_hub = project_mesh_to_2d(shaft_subparts['hub'], 'yz')

    plot_shapely_geom(ax, poly_plunger, facecolor='#fb923c', edgecolor='#c2410c', linewidth=1.8, alpha=0.85, zorder=5)
    plot_shapely_geom(ax, poly_hub, facecolor='#fef08a', edgecolor='#ca8a04', linewidth=1.8, alpha=0.9, zorder=5)
    plot_shapely_geom(ax, poly_cam, facecolor='#f59e0b', edgecolor='#b45309', linewidth=2.2, alpha=0.92, zorder=6)

    # Axle marker
    y_axle, z_axle = Y_AXLE, Z_AXLE
    ax.scatter([y_axle], [z_axle], marker='+', s=250, c='#dc2626', linewidth=2.5, zorder=7)
    ax.scatter([y_axle], [z_axle], marker='o', s=180, facecolors='none', edgecolors='#dc2626', linewidth=1.5, linestyle='--', zorder=7)
    ax.annotate(f'Shaft Axle Center (Y={y_axle:.2f}, Z={z_axle:.2f})\n[TOWERS OMITTED]',
                xy=(y_axle, z_axle), xytext=(y_axle + 2.5, z_axle + 1.2),
                fontsize=9.0, fontweight='bold', color='#b91c1c',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef2f2', edgecolor='#ef4444'),
                arrowprops=dict(arrowstyle='->', color='#dc2626', lw=1.5), zorder=7)

    # Title block
    title_box = dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#64748b', linewidth=1.5)
    ax.text(-25.0, 16.5,
            'BASEPLATE MIDLINE SECTION (X = 0.00 mm) WITH CAM ARM & ROCKER OVERLAY\n'
            'TOWERS OMITTED • TRUE INTERNAL CAVITY & ROCKER KINEMATIC CLEARANCE',
            fontsize=11.5, fontweight='heavy', color='#0f172a', bbox=title_box, va='top', zorder=8)

    ax.set_xlabel('Y Coordinate [mm]', fontsize=11, fontweight='bold')
    ax.set_ylabel('Z Coordinate [mm]', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated midline cross-section with cam arm: {output_path}")

def generate_multi_view_blueprint(output_path):
    """
    Generates a 3-panel engineering blueprint containing:
    1. Primary Side Elevation with Cam Arm & Rocker (Y-Z View)
    2. Kinematic Stroke Profile (Rest vs 6° CCW Actuation)
    3. Front/End Elevation with Cam Arm & Plunger (X-Z View)
    """
    parts, base_poly, outer_body_poly, hole_info = build_plate_without_towers()
    shaft_subparts = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False, return_subparts=True)
    
    fig = plt.figure(figsize=(30, 12), dpi=200)
    fig.patch.set_facecolor('#ffffff')

    poly_cam = project_mesh_to_2d(shaft_subparts['cam'], 'yz')
    poly_plunger = project_mesh_to_2d(shaft_subparts['plunger'], 'yz')
    poly_hub = project_mesh_to_2d(shaft_subparts['hub'], 'yz')

    poly_base = project_mesh_to_2d(parts['base'], 'yz')
    poly_shrouds = project_mesh_to_2d(parts['shrouds'], 'yz')
    poly_wall = project_mesh_to_2d(parts['wall'], 'yz')
    poly_curved = project_mesh_to_2d(parts['curved_feat'], 'yz')

    # Panel 1: Side Elevation (Y-Z) with Cam Arm
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.set_facecolor('#ffffff')
    ax1.set_xlim(-24.0, 26.0)
    ax1.set_ylim(-8.5, 16.0)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax1.grid(which='major', color='#cbd5e1', linestyle='-', linewidth=0.8, alpha=0.7)
    ax1.grid(which='minor', color='#f1f5f9', linestyle=':', linewidth=0.5, alpha=0.8)

    plot_shapely_geom(ax1, poly_base, '#94a3b8', '#334155', 1.5, 0.85)
    plot_shapely_geom(ax1, poly_shrouds, '#a7f3d0', '#059669', 1.5, 0.9)
    plot_shapely_geom(ax1, poly_wall, '#bae6fd', '#0369a1', 1.4, 0.65)
    plot_shapely_geom(ax1, poly_curved, '#e9d5ff', '#7e22ce', 1.6, 0.8)
    ax1.add_patch(Rectangle((8.570, 0.00), 13.750 - 8.570, 1.00, facecolor='#ffffff', edgecolor='#dc2626', linewidth=1.5, linestyle='--'))
    
    # Rocker features
    plot_shapely_geom(ax1, poly_plunger, '#fb923c', '#c2410c', 1.8, 0.90)
    plot_shapely_geom(ax1, poly_hub, '#fef08a', '#ca8a04', 1.8, 0.95)
    plot_shapely_geom(ax1, poly_cam, '#f59e0b', '#b45309', 2.2, 0.95)
    ax1.scatter([Y_AXLE], [Z_AXLE], marker='+', s=150, c='#dc2626', linewidth=2.0)
    ax1.scatter([2.45], [7.55], marker='*', s=150, c='#b45309', zorder=6)
    
    ax1.set_title('1. Lateral Elevation with Cam Arm (Y-Z Plane)', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Y [mm]', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Z [mm]', fontsize=10, fontweight='bold')

    # Panel 2: Kinematic Stroke Profile
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.set_facecolor('#ffffff')
    ax2.set_xlim(-24.0, 26.0)
    ax2.set_ylim(-8.5, 16.0)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax2.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax2.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax2.grid(which='major', color='#cbd5e1', linestyle='-', linewidth=0.8, alpha=0.7)
    ax2.grid(which='minor', color='#f1f5f9', linestyle=':', linewidth=0.5, alpha=0.8)

    # Rest position
    plot_shapely_geom(ax2, poly_base, '#94a3b8', '#334155', 1.5, 0.5)
    plot_shapely_geom(ax2, poly_curved, '#e9d5ff', '#7e22ce', 1.4, 0.5)
    plot_shapely_geom(ax2, poly_cam, '#f59e0b', '#b45309', 1.8, 0.5, label='Cam at Rest (Apex Y=2.45, Z=7.55)')
    plot_shapely_geom(ax2, poly_plunger, '#fb923c', '#c2410c', 1.6, 0.5, label='Plunger at Rest (Z=-7.00)')
    
    # Actuated position (6.0° CCW)
    poly_cam_rot = rotate(poly_cam, 6.0, origin=(Y_AXLE, Z_AXLE))
    poly_plunger_rot = rotate(poly_plunger, 6.0, origin=(Y_AXLE, Z_AXLE))
    plot_shapely_geom(ax2, poly_cam_rot, '#f59e0b', '#b45309', 2.2, 0.95, label='Actuated Cam (6° CCW Stroke)')
    plot_shapely_geom(ax2, poly_plunger_rot, '#ea580c', '#9a3412', 2.0, 0.95, label='Actuated Plunger (Drives Switch)')
    
    ax2.scatter([Y_AXLE], [Z_AXLE], marker='+', s=150, c='#dc2626', linewidth=2.0)
    leg2 = ax2.legend(loc='lower right', fontsize=8.0, framealpha=0.9)
    ax2.set_title('2. Kinematic Stroke: Rest vs 6° Actuation', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('Y [mm]', fontsize=10, fontweight='bold')
    ax2.set_ylabel('Z [mm]', fontsize=10, fontweight='bold')

    # Panel 3: Front/End Elevation (X-Z)
    ax3 = fig.add_subplot(1, 3, 3)
    ax3.set_facecolor('#ffffff')
    ax3.set_xlim(-26.0, 26.0)
    ax3.set_ylim(-8.5, 16.0)
    ax3.xaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax3.xaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax3.yaxis.set_major_locator(ticker.MultipleLocator(5.0))
    ax3.yaxis.set_minor_locator(ticker.MultipleLocator(1.0))
    ax3.grid(which='major', color='#cbd5e1', linestyle='-', linewidth=0.8, alpha=0.7)
    ax3.grid(which='minor', color='#f1f5f9', linestyle=':', linewidth=0.5, alpha=0.8)

    poly_xz_base = project_mesh_to_2d(parts['base'], 'xz')
    poly_xz_shrouds = project_mesh_to_2d(parts['shrouds'], 'xz')
    poly_xz_wall = project_mesh_to_2d(parts['wall'], 'xz')
    poly_xz_curved = project_mesh_to_2d(parts['curved_feat'], 'xz')

    plot_shapely_geom(ax3, poly_xz_base, '#94a3b8', '#334155', 1.5, 0.85)
    plot_shapely_geom(ax3, poly_xz_shrouds, '#a7f3d0', '#059669', 1.5, 0.9)
    plot_shapely_geom(ax3, poly_xz_wall, '#bae6fd', '#0369a1', 1.4, 0.65)
    plot_shapely_geom(ax3, poly_xz_curved, '#e9d5ff', '#7e22ce', 1.6, 0.8)

    # Rocker in X-Z
    poly_xz_cam = project_mesh_to_2d(shaft_subparts['cam'], 'xz')
    poly_xz_plunger = project_mesh_to_2d(shaft_subparts['plunger'], 'xz')
    poly_xz_hub = project_mesh_to_2d(shaft_subparts['hub'], 'xz')
    poly_xz_pins = unary_union([project_mesh_to_2d(shaft_subparts['pin_l'], 'xz'), project_mesh_to_2d(shaft_subparts['pin_r'], 'xz')])

    plot_shapely_geom(ax3, poly_xz_pins, '#fde047', '#a16207', 1.4, 0.9)
    plot_shapely_geom(ax3, poly_xz_hub, '#fef08a', '#ca8a04', 1.6, 0.95)
    plot_shapely_geom(ax3, poly_xz_plunger, '#fb923c', '#c2410c', 1.8, 0.90)
    plot_shapely_geom(ax3, poly_xz_cam, '#f59e0b', '#b45309', 2.2, 0.95)

    ax3.set_title('3. Front/End Elevation with Cam Arm (X-Z Plane)', fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel('X [mm]', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Z [mm]', fontsize=10, fontweight='bold')

    plt.suptitle('AUTOMOTIVE OUTLET SUB-HOUSING — BASEPLATE & CAM ARM BLUEPRINT (TOWERS OMITTED)',
                 fontsize=14, fontweight='heavy', y=0.98, color='#0f172a')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"Generated multi-view blueprint with cam arm: {output_path}")

if __name__ == '__main__':
    testing_dir = os.path.dirname(os.path.abspath(__file__))
    annotatable_path = os.path.join(testing_dir, 'plate_side_view_annotatable.png')
    midline_path = os.path.join(testing_dir, 'plate_midline_section.png')
    blueprint_path = os.path.join(testing_dir, 'plate_side_view_blueprint.png')

    generate_annotatable_side_view(annotatable_path)
    generate_midline_cross_section(midline_path)
    generate_multi_view_blueprint(blueprint_path)

    # Also copy to artifacts directory
    artifact_dir = r"C:\Users\Elliot\.gemini\antigravity\brain\7212ff75-8778-49e0-80c7-8fc918b90fc4"
    if os.path.exists(artifact_dir):
        shutil.copy2(annotatable_path, os.path.join(artifact_dir, 'plate_side_view_annotatable.png'))
        shutil.copy2(midline_path, os.path.join(artifact_dir, 'plate_midline_section.png'))
        shutil.copy2(blueprint_path, os.path.join(artifact_dir, 'plate_side_view_blueprint.png'))
        print(f"Copied all diagrams with cam arm to artifact directory: {artifact_dir}")
