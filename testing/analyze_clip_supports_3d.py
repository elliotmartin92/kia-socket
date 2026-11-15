"""
Inspect the 3D geometry of the bottom clips and their supports.
Check:
1. Contact / release gap between support top and hook shelf.
2. Radial coverage: does the support cover the full radial overhang of the shelf?
3. Machine-orientation overhangs: what parts of the hook are unsupported?
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh

from build_part import (
    get_exact_base_polygon, build_bottom_clip_45deg_supports_mesh,
    find_boundary_point_and_normal, CLIP_ANGLES, CLIP_HOOK_DEPTH_BY_ANGLE,
    CLIP_HOOK_DEPTH, CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT,
    OUTER_WALL_HEIGHT, CLIP_CROWN_EASE, CLIP_BLUNT_HEIGHT
)

def analyze_clip_support_interaction():
    base_poly, outer_poly, _ = get_exact_base_polygon()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    
    # Load or build part
    print("Building bottom clip supports...")
    supports = build_bottom_clip_45deg_supports_mesh(base_poly)
    
    # Let's check the bounds and vertices of the support around 327.5 deg
    # Support mesh contains 2 pairs of prongs (one pair for 211.3, one pair for 327.5)
    # Let's split connected components
    comps = supports.split()
    print(f"Total support components: {len(comps)}")
    
    for c in comps:
        center = c.centroid
        angle_c = (np.degrees(np.arctan2(center[1], center[0])) + 360) % 360
        print(f"Component at {center}, angle ~ {angle_c:.1f}°, bounds: X[{c.bounds[0,0]:.2f}, {c.bounds[1,0]:.2f}], Y[{c.bounds[0,1]:.2f}, {c.bounds[1,1]:.2f}], Z[{c.bounds[0,2]:.2f}, {c.bounds[1,2]:.2f}]")

if __name__ == '__main__':
    analyze_clip_support_interaction()
