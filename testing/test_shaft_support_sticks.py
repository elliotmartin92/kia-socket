"""
testing/test_shaft_support_sticks.py
Prototype and verify CAD-modeled support sticks for the Cam tab and Plunger arm.
"""

import sys, os
import trimesh
import numpy as np
from shapely.geometry import box, Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

def build_extended_support_cradle(release_gap=0.14):
    """
    Builds the unified breakaway support structure containing:
    1. Outer perimeter bed adhesion frame (extended to cover stick footprints).
    2. Left & right axle pin saddles (Z = 0.58 mm, release gap = 0.12 mm).
    3. Sacrificial micro-anchor tabs at the hub shoulders.
    4. Support Stick #1: Cam Tab Pillar (Z: 0 to 7.70 mm) under the cam ramp knee.
    5. Support Stick #2: Plunger Tip Pillar (Z: 0 to 18.38 mm) under the plunger hook nose.
    6. Support Stick #3 (Optional/Tie): Plunger mid-arm stabilizer brace.
    """
    bed_th = 0.35
    
    # 1. Base footprint:
    # Existing central cradle: X in [-6.40, 6.40], Y in [-2.60, 3.80]
    # Central open window: X in [-3.85, 3.85], Y in [-0.80, 2.80]
    # Extended runner for Cam stick (X in [-3.20, -1.60], Y in [3.80, 6.60])
    # Extended runner for Plunger stick (X in [0.00, 2.20], Y in [-7.20, -2.60])
    
    poly_main_frame = box(-6.40, -2.60, 6.40, 3.80)
    poly_cam_foot = box(-3.30, 3.50, -1.50, 6.60)
    poly_plung_foot = box(-0.20, -7.20, 2.20, -2.50)
    
    poly_outer = unary_union([poly_main_frame, poly_cam_foot, poly_plung_foot])
    poly_window = box(-3.85, -0.80, 3.85, 2.80)
    
    poly_bed_plate = poly_outer.difference(poly_window)
    m_base_raw = trimesh.creation.extrude_polygon(poly_bed_plate, height=bed_th)
    
    # 2. Saddles under pins (Z: 0.35 to 0.58 mm)
    z_saddle_top = 0.70 - release_gap
    h_saddle = z_saddle_top - bed_th
    saddle_l = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_l.apply_translation([-4.75, 1.05, bed_th + h_saddle / 2.0])
    saddle_r = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_r.apply_translation([4.75, 1.05, bed_th + h_saddle / 2.0])
    
    # 3. Micro anchor tabs at hub shoulders (Z: 0.00 to 0.20 mm)
    tab_l = trimesh.creation.box(extents=[0.30, 0.50, 0.20])
    tab_l.apply_translation([-3.75, 1.05, 0.10])
    tab_r = trimesh.creation.box(extents=[0.30, 0.50, 0.20])
    tab_r.apply_translation([3.75, 1.05, 0.10])
    
    # 4. Support Stick #1: Cam Tab Support Pillar
    # Cam underside at Y = 5.60 mm is at Z = 7.75 mm.
    # With release_gap = 0.14 mm, top of stick reaches Z = 7.61 mm.
    # X span: Cam is at X in [-3.75, -1.05]. Center X = -2.40 mm.
    # Pillar dimensions: X width 1.20 mm, Y depth 1.20 mm.
    stick_cam_top_z = 7.61
    h_cam_stick = stick_cam_top_z - bed_th
    m_cam_stick = trimesh.creation.box([1.20, 1.20, h_cam_stick])
    m_cam_stick.apply_translation([-2.40, 5.60, bed_th + h_cam_stick / 2.0])
    
    # 5. Support Stick #2: Plunger Tip Support Pillar
    # Plunger tip nose at Y = -6.76 mm is at Z = 18.54 mm.
    # With release_gap = 0.14 mm, top of stick reaches Z = 18.40 mm.
    # X span: Plunger is centered around X = 1.03 mm.
    # Reinforced base: Z in [0.35, 10.0]
    h_p_base = 10.00 - bed_th
    m_plung_base = trimesh.creation.box([1.80, 1.60, h_p_base])
    m_plung_base.apply_translation([1.00, -6.10, bed_th + h_p_base / 2.0])
    
    # Upper stick: Z in [10.0, 18.40]
    h_p_top = 18.40 - 10.00
    m_plung_top = trimesh.creation.box([1.20, 1.10, h_p_top])
    m_plung_top.apply_translation([1.00, -6.30, 10.00 + h_p_top / 2.0])
    
    # 6. Support Stick #3: Plunger Mid-Span Stabilizer
    # Mid-span underside at Y = -3.80 mm is at Z = 10.00 mm.
    # With release_gap = 0.14 mm, top reaches Z = 9.86 mm.
    h_p_mid = 9.86 - bed_th
    m_plung_mid = trimesh.creation.box([1.20, 1.00, h_p_mid])
    m_plung_mid.apply_translation([1.00, -3.80, bed_th + h_p_mid / 2.0])
    
    # Diagonal brace linking Plunger Mid Stick and Plunger Tip Base (Z: 4.0 to 8.0 mm)
    m_brace = trimesh.creation.box([0.80, 1.20, 4.00])
    m_brace.apply_translation([1.00, -4.80, 6.00])
    
    # Combine all cradle elements
    cradle_mesh = trimesh.util.concatenate([
        m_base_raw, saddle_l, saddle_r, tab_l, tab_r,
        m_cam_stick, m_plung_base, m_plung_top, m_plung_mid, m_brace
    ])
    
    return cradle_mesh

rocker_bare = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
cradle = build_extended_support_cradle()

print("=" * 80)
print("EXTENDED SUPPORT CRADLE VERIFICATION")
print("=" * 80)
print(f"Rocker Bare: is_watertight={rocker_bare.is_watertight}, volume={rocker_bare.volume:.2f} mm³")
print(f"Cradle:      is_watertight={cradle.is_watertight}, volume={cradle.volume:.2f} mm³")

combined = trimesh.util.concatenate([rocker_bare, cradle])
print(f"Combined:    is_watertight={combined.is_watertight}, volume={combined.volume:.2f} mm³")

# Save prototype for visual inspection
combined.export('testing/shaft_rocker_with_sticks_test.stl')
print("Saved testing/shaft_rocker_with_sticks_test.stl")

# Check exact vertical clearance at each stick's contact center:
# 1. Cam stick at X = -2.40, Y = 5.60
# 2. Plunger tip stick at X = 1.00, Y = -6.30
# 3. Plunger mid stick at X = 1.00, Y = -3.80

# Render 3D multi-angle view of the rocker with sticks
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure(figsize=(18, 7))

# Subplot 1: Side view (Y-Z)
ax1 = fig.add_subplot(1, 3, 1)
# Rocker faces in blue/gray
for f in rocker_bare.faces[::2]:
    v = rocker_bare.vertices[f]
    ax1.plot(v[[0,1,2,0], 1], v[[0,1,2,0], 2], color='darkblue', alpha=0.3, linewidth=0.5)

# Cradle faces in green
for f in cradle.faces[::2]:
    v = cradle.vertices[f]
    ax1.plot(v[[0,1,2,0], 1], v[[0,1,2,0], 2], color='forestgreen', alpha=0.6, linewidth=0.8)

ax1.set_xlabel('Y (mm)')
ax1.set_ylabel('Z (mm)')
ax1.set_title('Side View (Y vs Z)\nBlue: Lever | Green: Built-in Support Sticks')
ax1.grid(True)
ax1.axis('equal')

# Subplot 2: Perspective 3D
ax2 = fig.add_subplot(1, 3, 2, projection='3d')
# Subsample for rendering
rocker_tris = [rocker_bare.vertices[f] for f in rocker_bare.faces[::3]]
cradle_tris = [cradle.vertices[f] for f in cradle.faces[::2]]

coll_r = Poly3DCollection(rocker_tris, facecolors=(0.2, 0.4, 0.8, 0.5), edgecolors='none')
coll_c = Poly3DCollection(cradle_tris, facecolors=(0.1, 0.8, 0.2, 0.8), edgecolors='none')

ax2.add_collection3d(coll_r)
ax2.add_collection3d(coll_c)
ax2.set_xlim(-8, 8)
ax2.set_ylim(-8, 8)
ax2.set_zlim(0, 21)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
ax2.view_init(elev=20, azim=-55)
ax2.set_title('3D Perspective View')

# Subplot 3: Front View (X-Z)
ax3 = fig.add_subplot(1, 3, 3)
for f in rocker_bare.faces[::2]:
    v = rocker_bare.vertices[f]
    ax3.plot(v[[0,1,2,0], 0], v[[0,1,2,0], 2], color='darkblue', alpha=0.3, linewidth=0.5)

for f in cradle.faces[::2]:
    v = cradle.vertices[f]
    ax3.plot(v[[0,1,2,0], 0], v[[0,1,2,0], 2], color='forestgreen', alpha=0.6, linewidth=0.8)

ax3.set_xlabel('X (mm)')
ax3.set_ylabel('Z (mm)')
ax3.set_title('Front View (X vs Z)')
ax3.grid(True)
ax3.axis('equal')

plt.tight_layout()
plt.savefig('testing/shaft_support_sticks_render.png', dpi=150)
print("Saved testing/shaft_support_sticks_render.png")

