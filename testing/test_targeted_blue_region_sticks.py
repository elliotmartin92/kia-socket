"""
testing/test_targeted_blue_region_sticks.py
Build and test the targeted support sticks holding up the exact blue regions
identified by the user in the slicer preview:
1. Cam Ramp Underhang (Z up to 7.61mm)
2. Plunger Belly Underhang (Z up to 6.75mm)
"""

import sys, os
import trimesh
import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

def build_targeted_sticks_cradle(release_gap=0.14, bed_thickness=0.35):
    # 1. Base footprint:
    # Main central brim: X in [-6.40, 6.40], Y in [-2.60, 3.80]
    # Central open window: X in [-3.85, 3.85], Y in [-0.80, 2.80]
    # Cam runner foot: X in [-3.20, -1.60], Y in [3.50, 6.40]
    # Plunger runner foot: X in [0.30, 1.80], Y in [-4.40, -2.50]
    # Rear pry tab: X in [-2.0, 2.0], Y in [-3.30, -2.60]
    
    poly_main = box(-6.40, -2.60, 6.40, 3.80)
    poly_cam_foot = box(-3.20, 3.50, -1.60, 6.40)
    poly_plung_foot = box(0.30, -4.40, 1.80, -2.50)
    poly_pry = box(-2.00, -3.30, 2.00, -2.60)
    
    poly_outer = unary_union([poly_main, poly_cam_foot, poly_plung_foot, poly_pry])
    poly_window = box(-3.85, -0.80, 3.85, 2.80)
    
    poly_bed_plate = poly_outer.difference(poly_window)
    frame_mesh = trimesh.creation.extrude_polygon(poly_bed_plate, height=bed_thickness)
    
    # 2. Saddles under axle pins
    z_saddle_top = 0.70 - release_gap
    h_saddle = z_saddle_top - bed_thickness
    saddle_l = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_l.apply_translation([-4.75, 1.05, bed_thickness + h_saddle / 2.0])
    saddle_r = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_r.apply_translation([4.75, 1.05, bed_thickness + h_saddle / 2.0])
    
    # 3. Micro anchor tabs at hub shoulders
    tab_l = trimesh.creation.box(extents=[0.30, 0.50, 0.20])
    tab_l.apply_translation([-3.75, 1.05, 0.10])
    tab_r = trimesh.creation.box(extents=[0.30, 0.50, 0.20])
    tab_r.apply_translation([3.75, 1.05, 0.10])
    
    # 4. Support Stick #1: Cam Ramp Pillar (holding up the blue cam overhang)
    # Cam underside at Y = 5.60 mm is at Z = 7.75 mm.
    # Top of stick reaches Z = 7.61 mm (0.14mm release gap).
    stick_cam_top_z = 7.61
    h_cam_stick = stick_cam_top_z - bed_thickness
    stick_cam = trimesh.creation.box([1.20, 1.20, h_cam_stick])
    stick_cam.apply_translation([-2.40, 5.60, bed_thickness + h_cam_stick / 2.0])
    
    # 5. Support Stick #2: Plunger Belly Pillar (holding up the blue plunger overhang)
    # Plunger belly underside at Y = -3.60 mm is at Z = 6.93 mm.
    # Top of stick reaches Z = 6.78 mm (0.15mm release gap).
    stick_p_top_z = 6.78
    h_p_stick = stick_p_top_z - bed_thickness
    stick_plung = trimesh.creation.box([1.20, 1.20, h_p_stick])
    stick_plung.apply_translation([1.03, -3.60, bed_thickness + h_p_stick / 2.0])
    
    cradle_mesh = trimesh.util.concatenate([
        frame_mesh, saddle_l, saddle_r, tab_l, tab_r,
        stick_cam, stick_plung
    ])
    return cradle_mesh

rocker = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
cradle = build_targeted_sticks_cradle()
combined = trimesh.util.concatenate([rocker, cradle])

print("=" * 80)
print(f"Rocker Bare: is_watertight={rocker.is_watertight}, vol={rocker.volume:.2f} mm³")
print(f"Cradle:      is_watertight={cradle.is_watertight}, vol={cradle.volume:.2f} mm³")
print(f"Combined:    is_watertight={combined.is_watertight}, vol={combined.volume:.2f} mm³")
print("=" * 80)

# Render verification figure comparing with user screenshot
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(15, 6))

ax1 = fig.add_subplot(1, 2, 1)
# Side view Y-Z
for f in rocker.faces[::2]:
    v = rocker.vertices[f]
    ax1.plot(v[[0,1,2,0], 1], v[[0,1,2,0], 2], color='darkorange', alpha=0.4, linewidth=0.5)

for f in cradle.faces[::2]:
    v = cradle.vertices[f]
    ax1.plot(v[[0,1,2,0], 1], v[[0,1,2,0], 2], color='green', alpha=0.7, linewidth=0.8)

ax1.annotate('Stick #1: Cam Ramp Pillar\n(Z = 7.61 mm, Y = 5.60 mm)\nHolds up Blue Cam Overhang',
             xy=(5.60, 7.61), xytext=(7.0, 10.0),
             arrowprops=dict(facecolor='darkgreen', shrink=0.05, width=2, headwidth=6),
             fontweight='bold', color='darkgreen')

ax1.annotate('Stick #2: Plunger Belly Pillar\n(Z = 6.78 mm, Y = -3.60 mm)\nHolds up Blue Plunger Overhang',
             xy=(-3.60, 6.78), xytext=(-8.0, 9.0),
             arrowprops=dict(facecolor='darkgreen', shrink=0.05, width=2, headwidth=6),
             fontweight='bold', color='darkgreen')

ax1.set_xlabel('Y (mm)')
ax1.set_ylabel('Z (mm)')
ax1.set_title('Side View: Rocker with Targeted Breakaway Sticks\nDirectly Supporting the Slicer "Overhang Wall" Regions')
ax1.grid(True)
ax1.axis('equal')

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
rocker_tris = [rocker.vertices[f] for f in rocker.faces[::3]]
cradle_tris = [cradle.vertices[f] for f in cradle.faces[::2]]
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
coll_r = Poly3DCollection(rocker_tris, facecolors=(0.9, 0.5, 0.1, 0.6), edgecolors='none')
coll_c = Poly3DCollection(cradle_tris, facecolors=(0.1, 0.8, 0.2, 0.8), edgecolors='none')
ax2.add_collection3d(coll_r)
ax2.add_collection3d(coll_c)
ax2.set_xlim(-8, 8)
ax2.set_ylim(-8, 8)
ax2.set_zlim(0, 20)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
ax2.view_init(elev=22, azim=-50)
ax2.set_title('3D View Matching User Slicer Orientation')

plt.tight_layout()
plt.savefig('testing/targeted_sticks_preview.png', dpi=150)
print("Saved testing/targeted_sticks_preview.png")
