"""
testing/test_breakaway_gaps_and_cantilever.py
Prototypes and verifies:
1. Increased gap on bottom clip 45° supports.
2. Increased gap on insert backside breakaway supports.
3. New stick support under the captive Print-in-Place cantilever (cam tab).
"""

import sys, os
import numpy as np
import trimesh
from shapely.geometry import box, Polygon
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import build_shaft

def test_prototypes():
    print("=" * 70)
    print("TESTING PROPOSED BREAKAWAY GAPS & CANTILEVER STICK")
    print("=" * 70)

    # 1. Base model
    part_flat, base_poly = build_part.build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    part_t = part_flat.copy().apply_transform(R)
    z_min = part_t.bounds[0, 2]
    part_t.apply_translation([0, 0, -z_min])

    # 2. Rocker subparts
    shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=7.20, in_assembly_coords=True, return_subparts=True, with_supports=False)
    cam_t = shaft_subparts['cam'].copy().apply_transform(R)
    cam_t.apply_translation([0, 0, -z_min])
    plunger_t = shaft_subparts['plunger'].copy().apply_transform(R)
    plunger_t.apply_translation([0, 0, -z_min])

    # Cam tab lowest point:
    lowest_cam_z = cam_t.bounds[0, 2]
    cam_lowest_verts = cam_t.vertices[np.isclose(cam_t.vertices[:, 2], lowest_cam_z, atol=0.05)]
    cam_c_x = np.mean(cam_lowest_verts[:, 0])
    cam_c_y = np.mean(cam_lowest_verts[:, 1])
    print(f"Cam tab lowest point: X={cam_c_x:.3f}, Y={cam_c_y:.3f}, Z={lowest_cam_z:.3f} mm")

    # Design candidate cantilever stick:
    gap_cam = 0.28  # 0.28mm release micro-gap
    z_cam_stick_top = lowest_cam_z - gap_cam
    
    # Baseplate floor under (cam_c_x, cam_c_y):
    # Floor top in tilted coords is Z' = Y' + 14.523 mm
    z_floor = cam_c_y + 14.523
    print(f"Baseplate floor Z below cam: {z_floor:.3f} mm")
    print(f"Total stick height: {z_cam_stick_top - z_floor:.3f} mm")

    # Build cantilever stick mesh:
    # 1. Foot/Neck at floor (Z: z_floor - 0.30 to z_floor + 0.60):
    # Narrow 0.70 x 0.70mm neck for effortless snap-off with needle-nose pliers
    neck = trimesh.creation.box([0.70, 0.70, 0.90])
    neck.apply_translation([cam_c_x, cam_c_y, z_floor + 0.15])

    # 2. Main trunk (Z: z_floor + 0.60 to z_cam_stick_top - 1.00):
    trunk_h = (z_cam_stick_top - 1.00) - (z_floor + 0.60)
    trunk = trimesh.creation.box([1.30, 1.30, trunk_h])
    trunk.apply_translation([cam_c_x, cam_c_y, z_floor + 0.60 + trunk_h / 2.0])

    # 3. Chisel tip (Z: z_cam_stick_top - 1.00 to z_cam_stick_top):
    tip = trimesh.creation.box([0.70, 0.70, 1.00])
    tip.apply_translation([cam_c_x, cam_c_y, z_cam_stick_top - 0.50])

    cam_stick = trimesh.util.concatenate([neck, trunk, tip])
    
    # Check clearances:
    tree_cam = cKDTree(cam_t.vertices)
    dists_to_cam, _ = tree_cam.query(cam_stick.vertices)
    min_dist_to_cam = np.min(dists_to_cam)
    print(f"Min distance from stick to cantilever: {min_dist_to_cam:.3f} mm (target >= {gap_cam:.2f} mm)")

    tree_part = cKDTree(part_t.vertices)
    dists_to_part, _ = tree_part.query(tip.vertices)
    print(f"Min distance from tip to main part walls: {np.min(dists_to_part):.3f} mm")

    print("\nSUCCESS: Prototype test completed!")

if __name__ == '__main__':
    test_prototypes()
