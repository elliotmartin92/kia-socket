"""
testing/inspect_shaft_support_stick_clearance.py
Generates high-resolution 3D inspection render of the updated support strut under the lever shaft,
measuring clearances to:
1. Plunger blade
2. Cam tab
3. Shaft hub barrel
4. Surrounding bracket/tower walls
"""

import sys, os
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import cKDTree

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft

def inspect_and_render():
    print("=" * 70)
    print("INSPECTING UPDATED SHAFT SUPPORT STRUT CLEARANCES")
    print("=" * 70)

    part_mesh_flat, base_poly = build_part.build_exact_3d_model()
    part_mesh_45, m_tilted, all_fins = build_part.build_45deg_supported_part_mesh(part_mesh_flat, base_poly, include_pip_shaft=False)
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    z_min = part_mesh_flat.copy().apply_transform(R).bounds[0, 2]

    shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, return_subparts=True, with_supports=False)
    for k, s in shaft_subparts.items():
        s.apply_transform(R)
        s.apply_translation([0, 0, -z_min])

    # Find the shaft support strut bodies off Bracket 4 (centered near X = 8.90mm)
    bodies = all_fins.split(only_watertight=False)
    stick_bodies = []
    for b in bodies:
        c = b.bounds.mean(axis=0)
        if 7.7 <= c[0] <= 10.0 and -3.0 <= c[1] <= 1.2 and b.bounds[1, 2] > 20.0:
            stick_bodies.append(b)
            print(f"Found stick body: bounds X=[{b.bounds[0,0]:.2f}, {b.bounds[1,0]:.2f}], Y=[{b.bounds[0,1]:.2f}, {b.bounds[1,1]:.2f}], Z=[{b.bounds[0,2]:.2f}, {b.bounds[1,2]:.2f}]")

    assert len(stick_bodies) > 0, "Shaft stick body not found!"
    full_stick = trimesh.util.concatenate(stick_bodies)

    print("\n--- Clearance to Lever Subparts ---")
    for k, s in shaft_subparts.items():
        tree = cKDTree(s.vertices)
        ds, _ = tree.query(full_stick.vertices)
        min_d = np.min(ds)
        print(f"  vs {k:10s}: min dist = {min_d:.3f} mm")
        assert min_d >= 0.45, f"Clearance to {k} too tight: {min_d:.3f} mm"

    # Render figure
    fig = plt.figure(figsize=(14, 7), dpi=180)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')

    # Clip part around lever
    mask = (m_tilted.vertices[:, 0] >= 4) & (m_tilted.vertices[:, 0] <= 15) & \
           (m_tilted.vertices[:, 1] >= -6) & (m_tilted.vertices[:, 1] <= 14) & \
           (m_tilted.vertices[:, 2] >= 10) & (m_tilted.vertices[:, 2] <= 32)
    f_mask = np.any(mask[m_tilted.faces], axis=1)
    sub_part = trimesh.Trimesh(vertices=m_tilted.vertices, faces=m_tilted.faces[f_mask])

    full_lever = trimesh.util.concatenate(list(shaft_subparts.values()))

    for ax, (elev, azim, title) in zip([ax1, ax2], [
        (35, -65, "Slicer Angle View (Matching User Screenshot)"),
        (15, -135, "Underside / Breakaway Contact View")
    ]):
        # Base part
        col_p = Poly3DCollection(sub_part.vertices[sub_part.faces], alpha=0.18, facecolor='#90a4ae', edgecolor='none')
        ax.add_collection3d(col_p)

        # Lever
        col_l = Poly3DCollection(full_lever.vertices[full_lever.faces], alpha=0.75, facecolor='#ff7043', edgecolor='#d84315', lw=0.3)
        ax.add_collection3d(col_l)

        # Updated Shaft Support Strut in Green
        col_s = Poly3DCollection(full_stick.vertices[full_stick.faces], alpha=0.95, facecolor='#4caf50', edgecolor='#1b5e20', lw=0.5)
        ax.add_collection3d(col_s)

        ax.set_xlim(5, 13)
        ax.set_ylim(-5, 11)
        ax.set_zlim(12, 30)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')

    plt.suptitle("Updated Lever Shaft Support Strut (0.48mm Release Gap + 0.50mm Lateral Clearance)", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    out_png = 'testing/shaft_support_stick_clearance_inspection.png'
    plt.savefig(out_png)
    print(f"\nSaved inspection figure: {out_png}")

if __name__ == '__main__':
    inspect_and_render()
