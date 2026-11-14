"""
testing/build_depth_gauge.py
Parametric CAD generator for a 3D-printable Plastic US 2-Prong Plug Depth Gauge.

Purpose:
- Diagnostic & troubleshooting tool to measure plug insertion depth into the
  in-cabin 120V AC outlet receptacle/sub-housing.
- Measures the exact depth at which the safety interlock rocker actuates the tactile button.
- Strictly for unpowered testing & troubleshooting.

Geometric Specifications (Standard US NEMA 1-15 2-Prong Plug):
- Blade width: 6.35 mm (1/4")
- Blade thickness: 1.52 mm (0.060")
- Blade spacing (center-to-center): 12.70 mm (0.500")
- Standard US plug blade nominal length: 16.50 mm (~5/8")
- Gauge extended blade length: 30.00 mm (allowing measurement beyond standard insertion)
- Gauge handle: Ergonomic grip block (30.0 mm wide x 12.0 mm thick x 25.0 mm long)
- Depth graduations:
  * 1.0 mm minor graduation notches
  * 5.0 mm major graduation notches
  * Clear numerical millimeter markings (5, 10, 15, 20, 25, 30 mm) from blade tip
- Deliverables generated:
  * testing/plug_depth_gauge.stl
  * testing/plug_depth_gauge.obj
  * testing/plug_depth_gauge_preview.png
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import matplotlib.textpath as tp

# ==============================================================================
# PARAMETRIC SPECIFICATIONS (ANSI / NEMA WD 6 & UL 498 GROUND TRUTH)
# ==============================================================================
# Standard US NEMA 1-15P / 5-15P Specification:
# - Center-to-center blade pitch: 0.500" (12.70 mm)
# - Blade thickness: 0.058" - 0.062" (1.47 - 1.57 mm, nominal 0.060" / 1.52 mm)
# - Hot (narrow) blade width: 0.250" ± 0.005" (6.22 - 6.48 mm, nominal 6.35 mm)
# - Polarized Neutral (wide) blade width: 0.312" ± 0.005" (7.80 - 8.05 mm, nominal 7.92 mm)
# - Non-polarized neutral width: same as hot blade 0.250" (6.35 mm)
# - Standard exposed blade length: 0.625" - 0.718" (15.88 - 18.24 mm, nominal 16.50 mm)
# - Bullet nose lead-in tip chamfer: 0.031" (0.80 mm) x 45°
BLADE_SPACING = 12.70           # 0.500" (12.70 mm) center-to-center pitch
BLADE_THICKNESS = 1.52          # 0.060" (1.52 mm) nominal thickness
BLADE_WIDTH_HOT = 6.35          # 0.250" (6.35 mm) hot blade width (actuates interlock)
BLADE_WIDTH_NEUTRAL_POL = 7.92  # 0.312" (7.92 mm) polarized neutral blade width
BLADE_WIDTH_NEUTRAL_NON = 6.35  # 0.250" (6.35 mm) non-polarized neutral blade width
STANDARD_LENGTH = 16.50         # ~5/8" (16.50 mm) standard plug length
EXTENDED_LENGTH = 32.00         # Extended length for deep diagnostic reach

# Default configuration: Non-polarized (fits all 2-prong outlets and reversible insertion)
# Set POLARIZED = True if testing dedicated polarized neutral slot width
POLARIZED = False
BLADE_WIDTH_NEUTRAL = BLADE_WIDTH_NEUTRAL_POL if POLARIZED else BLADE_WIDTH_NEUTRAL_NON

# Handle Dimensions
HANDLE_WIDTH_X = 28.00     # Grip width across both prongs
HANDLE_HEIGHT_Y = 14.00    # Grip height in blade plane
HANDLE_LENGTH_Z = 28.00    # Grip block length

# Graduations
NOTCH_MINOR_DEPTH = 0.40   # 0.40mm deep V-notch for 1mm marks
NOTCH_MAJOR_DEPTH = 0.80   # 0.80mm deep V-notch for 5mm marks
NOTCH_WIDTH_Z = 0.50       # Longitudinal width of notch

# Nominal Actuation Reference Depth
# Kinematic simulation confirms contact at ~8.0mm penetration and button trip at ~9.5mm penetration.
NOMINAL_TRIP_DEPTH = 9.50


def text_to_shapely(text, size=3.5, x0=0.0, y0=0.0):
    """Converts text string to Shapely polygon(s) with inner hole support."""
    path = tp.TextPath((x0, y0), text, size=size)
    polys = [Polygon(p) for p in path.to_polygons()]
    polys = sorted(polys, key=lambda p: p.area, reverse=True)
    res = []
    used = set()
    for i, p1 in enumerate(polys):
        if i in used:
            continue
        holes = []
        for j, p2 in enumerate(polys[i+1:], start=i+1):
            if j not in used and p1.contains(p2):
                holes.append(p2.exterior.coords)
                used.add(j)
        res.append(Polygon(p1.exterior.coords, holes))
    return unary_union(res)


def extrude_any_shapely(geom, height):
    """Extrudes any Shapely geometry (Polygon or MultiPolygon) into a watertight Trimesh."""
    geoms = geom.geoms if hasattr(geom, 'geoms') else [geom]
    meshes = []
    for g in geoms:
        if not g.is_empty and g.area > 0:
            meshes.append(trimesh.creation.extrude_polygon(g, height=height))
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.util.concatenate(meshes)


def create_graduated_blade_polygon(width=BLADE_WIDTH_HOT):
    """
    Creates the 2D polygon profile (in Y-Z plane) of the extended prong blade
    with built-in lead-in bullet chamfer and graduation notches.
    Y axis: blade width (centered at 0, span [-width/2, +width/2])
    Z axis: blade length (0 = tip, +32.00 = root at handle shoulder)
    """
    half_w = width / 2.0
    c = 0.80 # 0.80mm bullet nose lead-in chamfer
    # Right root extended into handle by 2.0mm for solid union
    BLADE_ROOT_EMBED = 2.0
    right_pts = [(half_w, EXTENDED_LENGTH + BLADE_ROOT_EMBED)]
    
    # Left edge (Y = -half_w) points going from tip (Z = 0) to root (Z = EXTENDED_LENGTH + EMBED)
    left_pts = []

    # Insert notches on right edge from Z = EXTENDED_LENGTH down to Z = 1.0mm
    for z_station in np.arange(EXTENDED_LENGTH - 1.0, 0.5, -1.0):
        is_major = (round(z_station) % 5 == 0)
        depth = NOTCH_MAJOR_DEPTH if is_major else NOTCH_MINOR_DEPTH
        w_half = NOTCH_WIDTH_Z / 2.0
        
        right_pts.append((half_w, z_station + w_half))
        right_pts.append((half_w - depth, z_station))
        right_pts.append((half_w, z_station - w_half))

    # Right tip chamfer
    right_pts.append((half_w, c))
    right_pts.append((half_w - c, 0.0))
    
    # Left tip chamfer
    left_pts.append((-half_w + c, 0.0))
    left_pts.append((-half_w, c))

    # Insert notches on left edge from Z = 1.0mm up to root
    for z_station in np.arange(1.0, EXTENDED_LENGTH, 1.0):
        is_major = (round(z_station) % 5 == 0)
        depth = NOTCH_MAJOR_DEPTH if is_major else NOTCH_MINOR_DEPTH
        w_half = NOTCH_WIDTH_Z / 2.0
        
        left_pts.append((-half_w, z_station - w_half))
        left_pts.append((-half_w + depth, z_station))
        left_pts.append((-half_w, z_station + w_half))

    left_pts.append((-half_w, EXTENDED_LENGTH + BLADE_ROOT_EMBED))

    all_pts = right_pts + left_pts
    return Polygon(all_pts)


def build_single_blade_mesh(width=BLADE_WIDTH_HOT):
    """Builds a single 3D blade mesh with graduations and lead-in chamfer."""
    blade_poly = create_graduated_blade_polygon(width=width)
    blade_raw = trimesh.creation.extrude_polygon(blade_poly, height=BLADE_THICKNESS)
    
    vertices_orig = blade_raw.vertices.copy()
    new_vertices = np.zeros_like(vertices_orig)
    new_vertices[:, 0] = vertices_orig[:, 2] - BLADE_THICKNESS / 2.0  # X: centered around 0
    new_vertices[:, 1] = vertices_orig[:, 0]                          # Y: width [-width/2, +width/2]
    new_vertices[:, 2] = vertices_orig[:, 1]                          # Z: length [0, 32.0]
    
    return trimesh.Trimesh(vertices=new_vertices, faces=blade_raw.faces, process=True)


def build_gauge_mesh(polarized=POLARIZED):
    """
    Constructs the complete 3D mesh of the 2-prong plug depth gauge.
    Coordinate System:
    - X: Across plug width (neutral blade at X = -BLADE_SPACING/2, hot blade at X = +BLADE_SPACING/2)
    - Y: Blade width direction (in-plane)
    - Z: Insertion axis (0 = blade tips, +32 = handle face, +60 = handle rear)
    """
    w_neutral = BLADE_WIDTH_NEUTRAL_POL if polarized else BLADE_WIDTH_NEUTRAL_NON
    
    hot_blade = build_single_blade_mesh(width=BLADE_WIDTH_HOT)
    hot_blade.apply_translation([BLADE_SPACING / 2.0, 0, 0])
    
    neutral_blade = build_single_blade_mesh(width=w_neutral)
    neutral_blade.apply_translation([-BLADE_SPACING / 2.0, 0, 0])

    # -------------------------------------------------------------------------
    # Ergonomic Handle / Base Block
    # -------------------------------------------------------------------------
    # Handle sits from Z = EXTENDED_LENGTH (32mm) to Z = EXTENDED_LENGTH + HANDLE_LENGTH_Z (60mm)
    z_handle_start = EXTENDED_LENGTH
    z_handle_center = z_handle_start + HANDLE_LENGTH_Z / 2.0
    
    # Base block with finger grip recesses
    handle_box = trimesh.creation.box([HANDLE_WIDTH_X, HANDLE_HEIGHT_Y, HANDLE_LENGTH_Z])
    handle_box.apply_translation([0, 0, z_handle_center])
    
    # Finger grip fillets / indentations on both sides (+Y and -Y)
    grip_cyl_r = 16.0
    grip_cyl_1 = trimesh.creation.cylinder(radius=grip_cyl_r, height=HANDLE_WIDTH_X + 4.0)
    # Rotate cylinder along X
    rot_x = trimesh.transformations.rotation_matrix(np.radians(90.0), [0, 1, 0])
    grip_cyl_1.apply_transform(rot_x)
    grip_cyl_1.apply_translation([0, HANDLE_HEIGHT_Y / 2.0 + grip_cyl_r - 2.0, z_handle_center])
    
    grip_cyl_2 = grip_cyl_1.copy()
    grip_cyl_2.apply_translation([0, -(HANDLE_HEIGHT_Y + 2.0 * grip_cyl_r - 4.0), 0])

    try:
        handle_sculpted = trimesh.boolean.difference([handle_box, grip_cyl_1, grip_cyl_2], engine='manifold')
    except Exception:
        handle_sculpted = handle_box

    # Union the solid handle and both prongs together into ONE monolithic body:
    gauge_body = trimesh.boolean.union([handle_sculpted, hot_blade, neutral_blade], engine='manifold')

    # -------------------------------------------------------------------------
    # True Boolean Debossing into Handle & Blade (Zero Floating Bodies, Un-Mirrored)
    # -------------------------------------------------------------------------
    deboss_cutters = []

    # 1. Handle Top Face Deboss Cutters (Face is at Y = +HANDLE_HEIGHT_Y / 2 = 7.00)
    # Text in (u, v): u is horizontal right (+X), v is vertical up (+Z), w cuts into -Y.
    t1 = text_to_shapely("DEPTH GAUGE", size=2.8, x0=-9.0, y0=4.0)
    t2 = text_to_shapely("UNPOWERED ONLY", size=2.2, x0=-10.5, y0=-1.0)
    t3 = text_to_shapely("ACTUATION ~9.5mm", size=2.0, x0=-10.0, y0=-6.0)
    
    labels_poly = unary_union([t1, t2, t3])
    m_handle_text = extrude_any_shapely(labels_poly, height=0.80)
    
    # 4x4 rigid transform (det = +1): u -> +X, v -> +Z, w -> -Y
    T_h = np.eye(4)
    T_h[:3, :3] = np.column_stack([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    T_h[:3, 3] = [0, (HANDLE_HEIGHT_Y / 2.0) + 0.10, z_handle_center]
    m_handle_text.apply_transform(T_h)
    deboss_cutters.append(m_handle_text)

    # 2. Millimeter Number Deboss Cutters on Outer Face of Hot Blade (+X face at X = +7.11)
    # Text in (u, v): u is horizontal right (-Y), v is vertical up (+Z), w cuts into -X.
    x_blade_face = BLADE_SPACING / 2.0 + BLADE_THICKNESS / 2.0  # +7.11mm
    for mark_z in [5, 10, 15, 20, 25, 30]:
        num_str = str(mark_z)
        t_num = text_to_shapely(num_str, size=2.0, x0=0, y0=0)
        m_num = extrude_any_shapely(t_num, height=0.50)
        
        # Center number in 2D before transform
        bounds = m_num.bounds
        cx = (bounds[0, 0] + bounds[1, 0]) / 2.0
        cy = (bounds[0, 1] + bounds[1, 1]) / 2.0
        m_num.apply_translation([-cx, -cy, 0])
        
        # 4x4 rigid transform (det = +1): u -> -Y, v -> +Z, w -> -X
        T_b = np.eye(4)
        T_b[:3, :3] = np.column_stack([[0, -1, 0], [0, 0, 1], [-1, 0, 0]])
        T_b[:3, 3] = [x_blade_face + 0.10, 0.0, mark_z]
        m_num.apply_transform(T_b)
        deboss_cutters.append(m_num)

    # Perform clean boolean difference
    try:
        combined_cutters = trimesh.util.concatenate(deboss_cutters)
        gauge_mesh = trimesh.boolean.difference([gauge_body, combined_cutters], engine='manifold')
        # Ensure single solid body
        bodies = [b for b in gauge_mesh.split(only_watertight=False) if b.volume > 10.0]
        if len(bodies) == 1:
            gauge_mesh = bodies[0]
    except Exception as e:
        print(f"Warning during deboss boolean: {e}, falling back to solid body")
        gauge_mesh = gauge_body

    return gauge_mesh, (hot_blade, neutral_blade, handle_sculpted)


def render_preview(gauge_mesh, out_path="testing/plug_depth_gauge_preview.png"):
    """Generates a high-resolution 3-panel technical preview diagram."""
    fig = plt.figure(figsize=(20, 10), dpi=160, facecolor='#ffffff')
    
    # Panel 1: Front Elevation & Graduations (Y-Z Plane)
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.set_title("Panel 1: Front Elevation & Graduations", fontsize=12, fontweight='bold', pad=10)
    
    poly_blade = create_graduated_blade_polygon()
    bx, bz = poly_blade.exterior.xy
    
    # Hot Blade (+X offset projected or single blade view)
    ax1.plot(bx, bz, color='#0288d1', linewidth=2.0, label='Prong Blade Contour')
    ax1.fill(bx, bz, color='#e1f5fe', alpha=0.7)
    
    # Reference Line for Standard Length
    ax1.axhline(STANDARD_LENGTH, color='#e65100', linestyle='--', linewidth=1.8,
                label=f'Standard Blade Length ({STANDARD_LENGTH:.1f}mm)')
    
    # Reference Line for Nominal Actuation Depth
    ax1.axhline(NOMINAL_TRIP_DEPTH, color='#d32f2f', linestyle=':', linewidth=2.0,
                label=f'Nominal Button Trip (~{NOMINAL_TRIP_DEPTH:.1f}mm)')
    
    # Annotate key stations
    for z in [5, 10, 15, 20, 25, 30]:
        ax1.annotate(f"{z}mm", (BLADE_WIDTH_HOT / 2.0 + 0.4, z), fontsize=9, fontweight='bold', color='#01579b',
                     verticalalignment='center')
    
    ax1.annotate(f"Standard US Plug Reach\n(16.5mm)", (0, STANDARD_LENGTH),
                 xytext=(-6.5, STANDARD_LENGTH + 2.5),
                 fontsize=9, fontweight='bold', color='#e65100',
                 arrowprops=dict(arrowstyle="->", color="#e65100", lw=1.2))

    ax1.annotate(f"Audible Trip Window\n(~9.0 - 9.5mm)", (0, NOMINAL_TRIP_DEPTH),
                 xytext=(-6.5, NOMINAL_TRIP_DEPTH - 3.5),
                 fontsize=9, fontweight='bold', color='#d32f2f',
                 arrowprops=dict(arrowstyle="->", color="#d32f2f", lw=1.2))

    ax1.set_xlim(-8.0, 8.0)
    ax1.set_ylim(-2.0, EXTENDED_LENGTH + 6.0)
    ax1.set_xlabel("Blade Width Y (mm)", fontsize=10)
    ax1.set_ylabel("Insertion Depth from Tip Z (mm)", fontsize=10)
    ax1.legend(loc='upper left', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Panel 2: End-On Pin Spacing & Cross-Section (X-Y Plane)
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.set_title("Panel 2: Plug Pin Pitch & Cross-Section (X-Y)", fontsize=12, fontweight='bold', pad=10)
    
    hw_hot = BLADE_WIDTH_HOT / 2.0
    hw_neu = BLADE_WIDTH_NEUTRAL / 2.0
    ht = BLADE_THICKNESS / 2.0
    
    # Neutral blade
    ax2.fill([-BLADE_SPACING/2 - ht, -BLADE_SPACING/2 + ht, -BLADE_SPACING/2 + ht, -BLADE_SPACING/2 - ht],
             [-hw_neu, -hw_neu, hw_neu, hw_neu], color='#90caf9', edgecolor='#0d47a1', linewidth=1.5,
             label=f'Neutral Prong ({BLADE_WIDTH_NEUTRAL:.2f}mm)')
             
    # Hot blade
    ax2.fill([BLADE_SPACING/2 - ht, BLADE_SPACING/2 + ht, BLADE_SPACING/2 + ht, BLADE_SPACING/2 - ht],
             [-hw_hot, -hw_hot, hw_hot, hw_hot], color='#ffab91', edgecolor='#bf360c', linewidth=1.5,
             label=f'Hot Prong ({BLADE_WIDTH_HOT:.2f}mm, Actuates Cam)')
             
    # Dimension arrows for spacing
    ax2.annotate("", xy=(-BLADE_SPACING/2, hw_hot + 2.0), xytext=(BLADE_SPACING/2, hw_hot + 2.0),
                 arrowprops=dict(arrowstyle="<->", color="black", lw=1.5))
    ax2.text(0, hw_hot + 2.5, f"Pitch = {BLADE_SPACING:.2f}mm (1/2\")", fontsize=10, fontweight='bold', ha='center')

    # Blade width dimension
    ax2.annotate("", xy=(BLADE_SPACING/2 + ht + 1.5, -hw_hot), xytext=(BLADE_SPACING/2 + ht + 1.5, hw_hot),
                 arrowprops=dict(arrowstyle="<->", color="#bf360c", lw=1.2))
    ax2.text(BLADE_SPACING/2 + ht + 2.0, 0, f"W = {BLADE_WIDTH_HOT:.2f}mm\n(1/4\")", fontsize=9, va='center')

    ax2.set_xlim(-16.0, 16.0)
    ax2.set_ylim(-10.0, 10.0)
    ax2.set_xlabel("X Position (mm)", fontsize=10)
    ax2.set_ylabel("Y Position (mm)", fontsize=10)
    ax2.legend(loc='lower center', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # Panel 3: 3D Isometric View
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    ax3.set_title("Panel 3: 3D Gauge Mesh Isometric", fontsize=12, fontweight='bold', pad=10)
    
    # Render with Matplotlib Poly3DCollection for a solid, shaded model
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    faces_to_render = gauge_mesh.faces[::max(1, len(gauge_mesh.faces) // 1800)]
    triangles = gauge_mesh.vertices[faces_to_render]
    mesh_poly = Poly3DCollection(triangles, facecolors='#00acc1', edgecolors='#006064', linewidths=0.1, alpha=0.92)
    ax3.add_collection3d(mesh_poly)
    
    ax3.set_xlim(gauge_mesh.bounds[0, 0] - 2, gauge_mesh.bounds[1, 0] + 2)
    ax3.set_ylim(gauge_mesh.bounds[0, 1] - 2, gauge_mesh.bounds[1, 1] + 2)
    ax3.set_zlim(gauge_mesh.bounds[0, 2] - 2, gauge_mesh.bounds[1, 2] + 2)
    ax3.view_init(elev=20, azim=-60)
    ax3.set_xlabel("X (mm)", fontsize=9)
    ax3.set_ylabel("Y (mm)", fontsize=9)
    ax3.set_zlabel("Z (mm)", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=160, bbox_inches='tight')
    plt.close()


def main():
    print("=" * 70)
    print("PLUG DEPTH GAUGE GENERATOR (UNPOWERED TROUBLESHOOTING)")
    print("=" * 70)
    print(f"Blade Thickness: {BLADE_THICKNESS:.2f}mm (0.060\")")
    print(f"Hot Blade Width: {BLADE_WIDTH_HOT:.2f}mm (0.250\")")
    print(f"Neutral Blade Width: {BLADE_WIDTH_NEUTRAL:.2f}mm ({'0.312\" Polarized' if POLARIZED else '0.250\" Non-polarized'})")
    print(f"Prong Center Pitch: {BLADE_SPACING:.2f}mm (0.500\" Standard US NEMA 1-15)")
    print(f"Extended Blade Length: {EXTENDED_LENGTH:.2f}mm (Standard: {STANDARD_LENGTH:.1f}mm)")
    print(f"Handle Grip: {HANDLE_WIDTH_X:.1f} x {HANDLE_HEIGHT_Y:.1f} x {HANDLE_LENGTH_Z:.1f}mm")
    
    mesh, _ = build_gauge_mesh()
    print(f"\nGenerated watertight mesh: {mesh.is_watertight}")
    print(f"Total Vertices: {len(mesh.vertices)}, Total Faces: {len(mesh.faces)}")
    print(f"Bounding Box: X in [{mesh.bounds[0,0]:.1f}, {mesh.bounds[1,0]:.1f}], "
          f"Y in [{mesh.bounds[0,1]:.1f}, {mesh.bounds[1,1]:.1f}], "
          f"Z in [{mesh.bounds[0,2]:.1f}, {mesh.bounds[1,2]:.1f}]")
    
    stl_out = os.path.join(os.path.dirname(__file__), 'plug_depth_gauge.stl')
    obj_out = os.path.join(os.path.dirname(__file__), 'plug_depth_gauge.obj')
    prev_out = os.path.join(os.path.dirname(__file__), 'plug_depth_gauge_preview.png')
    
    mesh.export(stl_out)
    mesh.export(obj_out)
    print(f"Exported: {stl_out}")
    print(f"Exported: {obj_out}")
    
    render_preview(mesh, prev_out)
    print(f"Rendered diagnostic blueprint: {prev_out}")
    print("=" * 70)


if __name__ == '__main__':
    main()
