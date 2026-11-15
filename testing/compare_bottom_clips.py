"""
Deep comparison between Clip 211.3° (bottom left) and Clip 327.5° (bottom right).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_HOOK_DEPTH_BY_ANGLE, CLIP_HOOK_DEPTH,
    CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_CROWN_EASE,
    CLIP_STEM_OUTER_RECESS_BY_ANGLE
)

def compare_bottom_clips():
    base_poly, outer_poly, _ = get_exact_base_polygon()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    
    print("=== DETAILED COMPARISON: 211.3° vs 327.5° ===")
    for angle_deg in [211.3, 327.5]:
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        recess = CLIP_STEM_OUTER_RECESS_BY_ANGLE.get(angle_deg, 0.0)
        
        print(f"\nClip {angle_deg}°:")
        print(f"  Boundary Point (X, Y): ({p[0]:.3f}, {p[1]:.3f})")
        print(f"  Outward Normal: ({norm[0]:.3f}, {norm[1]:.3f})")
        print(f"  Tangent: ({tang[0]:.3f}, {tang[1]:.3f})")
        print(f"  Hook depth: {depth:.3f} mm")
        print(f"  Stem outer recess: {recess:.3f} mm")
        
        # Check angle of norm relative to radial vector p / norm(p)
        p_unit = p / np.linalg.norm(p)
        dot_pn = np.dot(p_unit, norm)
        print(f"  Angle between radial vector and surface normal: {math.degrees(math.acos(dot_pn)):.2f}°")
        
        # In machine coordinates:
        p_mach = R[:3, :3] @ np.array([p[0], p[1], 4.72])
        norm_mach = R[:3, :3] @ np.array([norm[0], norm[1], 0.0])
        print(f"  Machine coords of shelf center: ({p_mach[0]:.2f}, {p_mach[1]:.2f}, {p_mach[2]:.2f})")
        print(f"  Machine normal: ({norm_mach[0]:.3f}, {norm_mach[1]:.3f}, {norm_mach[2]:.3f})")
        print(f"  Normal Z_mach (overhang): {norm_mach[2]:.3f}")
        
        # Check direction of tang in machine coords
        tang_mach = R[:3, :3] @ np.array([tang[0], tang[1], 0.0])
        print(f"  Machine tangent: ({tang_mach[0]:.3f}, {tang_mach[1]:.3f}, {tang_mach[2]:.3f})")
        print(f"  Tangent slope in machine coords: Z'/sqrt(X'^2 + Y'^2) = {tang_mach[2] / np.linalg.norm(tang_mach[:2]):.3f}")

if __name__ == '__main__':
    compare_bottom_clips()
