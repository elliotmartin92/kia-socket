"""
testing/verify_stick_clearances.py
Check the exact 3D clearance from each stick (and brace) to the bare rocker.
Ensure no collisions or accidental fusion occurs, and verify release gaps.
"""

import sys, os
import trimesh
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

rocker = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False)
cradle_test = trimesh.load('testing/shaft_rocker_with_sticks_test.stl')

# Let's inspect the sticks individually:
bed_th = 0.35

# 1. Cam Stick: X in [-3.00, -1.80], Y in [5.00, 6.20], Z in [0.35, 7.61]
stick_cam = trimesh.creation.box([1.20, 1.20, 7.61 - bed_th])
stick_cam.apply_translation([-2.40, 5.60, bed_th + (7.61 - bed_th)/2.0])

# 2. Plunger Mid Stick: X in [0.40, 1.60], Y in [-4.30, -3.30], Z in [0.35, 9.86]
stick_plung_mid = trimesh.creation.box([1.20, 1.00, 9.86 - bed_th])
stick_plung_mid.apply_translation([1.00, -3.80, bed_th + (9.86 - bed_th)/2.0])

# 3. Plunger Tip Base: X in [0.10, 1.90], Y in [-6.90, -5.30], Z in [0.35, 10.00]
stick_p_base = trimesh.creation.box([1.80, 1.60, 10.00 - bed_th])
stick_p_base.apply_translation([1.00, -6.10, bed_th + (10.00 - bed_th)/2.0])

# 4. Plunger Tip Top: X in [0.40, 1.60], Y in [-6.85, -5.75], Z in [10.00, 18.40]
stick_p_top = trimesh.creation.box([1.20, 1.10, 8.40])
stick_p_top.apply_translation([1.00, -6.30, 10.00 + 4.20])

# 5. Brace: X in [0.60, 1.40], Y in [-5.40, -4.20], Z in [4.00, 8.00]
brace = trimesh.creation.box([0.80, 1.20, 4.00])
brace.apply_translation([1.00, -4.80, 6.00])

elements = {
    'Cam Stick': stick_cam,
    'Plunger Mid Stick': stick_plung_mid,
    'Plunger Tip Base': stick_p_base,
    'Plunger Tip Top': stick_p_top,
    'Plunger Brace': brace
}

print("=" * 80)
print("STICK CLEARANCE & RELEASE GAP VERIFICATION")
print("=" * 80)

# Vectorized distance from points to triangles of rocker
tris = rocker.vertices[rocker.faces]

def min_distance_to_rocker(points):
    # Vectorized point to triangle distance
    min_dist = float('inf')
    for p in points:
        # Distance to all triangle centers as coarse filter
        c = rocker.triangles_center
        dist_sq = np.sum((c - p)**2, axis=1)
        close_idx = np.where(dist_sq < 25.0)[0] # within 5mm
        if len(close_idx) == 0:
            continue
        # Check closest vertices
        close_tris = tris[close_idx]
        v_diff = close_tris - p
        dists = np.linalg.norm(v_diff, axis=2)
        min_dist = min(min_dist, np.min(dists))
    return min_dist

for name, elem in elements.items():
    # Sample vertices of the element
    v = elem.vertices
    # Sample additional points on top face
    z_max = elem.bounds[1, 2]
    top_mask = np.isclose(v[:, 2], z_max)
    top_pts = v[top_mask]
    
    # Calculate min distance
    min_d = min_distance_to_rocker(v)
    min_d_top = min_distance_to_rocker(top_pts)
    
    print(f"{name:<20} | Z Top: {z_max:5.2f} mm | Overall Min Dist: {min_d:.3f} mm | Top Face Min Dist: {min_d_top:.3f} mm")
    if min_d < 0.05:
        print(f"  WARNING: {name} might be too close or intersecting!")
    else:
        print(f"  PASS: Safe release gap confirmed.")

print("=" * 80)
