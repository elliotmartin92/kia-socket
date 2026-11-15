"""
Diagnostic script to inspect clip geometry, overhang angles in machine coordinates (tilted 45 deg around X),
and analyze the gap and retention issues reported by the user.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_HOOK_DEPTH_BY_ANGLE, CLIP_HOOK_DEPTH,
    CLIP_ARM_WIDTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_CROWN_EASE,
    OUTER_WALL_HEIGHT
)

def inspect():
    base_poly, outer_poly, _ = get_exact_base_polygon()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    
    print("=== CLIP POSITIONS & ORIENTATIONS IN PART AND MACHINE COORDS ===")
    for angle_deg in CLIP_ANGLES:
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_est = np.linalg.norm(p)
        depth = CLIP_HOOK_DEPTH_BY_ANGLE.get(angle_deg, CLIP_HOOK_DEPTH)
        
        # Shelf normal in part coordinates: points straight down in -Z: [0, 0, -1]
        shelf_normal_part = np.array([0.0, 0.0, -1.0])
        # Outer hook blunt face normal in part coordinates: points outward along norm: [norm[0], norm[1], 0]
        blunt_normal_part = np.array([norm[0], norm[1], 0.0])
        
        # Lead-in ramp normal: between outer normal and +Z
        # Ramp goes from (R_outer, Z=shelf+blunt) to (R_stem, Z=wall_top)
        # Vector along ramp: dR = -depth, dZ = CLIP_HOOK_HEIGHT - 0.53 = 2.05 - 0.53 = 1.52
        # Ramp normal in (R, Z): [1.52, depth] / norm
        ramp_n_r = 1.52 / math.sqrt(1.52**2 + depth**2)
        ramp_n_z = depth / math.sqrt(1.52**2 + depth**2)
        ramp_normal_part = np.array([norm[0] * ramp_n_r, norm[1] * ramp_n_r, ramp_n_z])
        
        # Transform normals to machine coords:
        shelf_normal_mach = R[:3, :3] @ shelf_normal_part
        blunt_normal_mach = R[:3, :3] @ blunt_normal_part
        ramp_normal_mach = R[:3, :3] @ ramp_normal_part
        
        # In machine coords, Z_mach is build direction [0, 0, 1].
        # An downward-facing overhang has normal with Z_mach < 0.
        # Overhang angle from vertical (0 = vertical wall, 90 = horizontal ceiling):
        # cos(angle from downward vertical -Z_mach) = -normal[2]
        
        # Point in 3D (at shelf elevation Z = 4.72)
        p3d_part = np.array([p[0], p[1], 4.72])
        p3d_mach = R[:3, :3] @ p3d_part
        
        print(f"\nClip {angle_deg:.1f}°:")
        print(f"  Part (X, Y): ({p[0]:.2f}, {p[1]:.2f}), R={r_est:.2f}mm")
        print(f"  Machine Position (X', Y', Z'): ({p3d_mach[0]:.2f}, {p3d_mach[1]:.2f}, {p3d_mach[2]:.2f})")
        print(f"  Shelf Normal in Machine coords: [{shelf_normal_mach[0]:.3f}, {shelf_normal_mach[1]:.3f}, {shelf_normal_mach[2]:.3f}]")
        print(f"  Blunt Normal in Machine coords: [{blunt_normal_mach[0]:.3f}, {blunt_normal_mach[1]:.3f}, {blunt_normal_mach[2]:.3f}]")
        
        # Angle of shelf from machine horizontal (build plate):
        # Build plate normal is [0, 0, 1].
        # Shelf normal is [0, -sin(45°), -cos(45°)] = [0, -0.707, -0.707]!
        # Notice shelf normal Z component is ALWAYS -0.707 regardless of angle_deg, because shelf is planar Z=constant in part coords!
        print(f"  Shelf inclination in machine space: points downward at 45° to build plate!")
        
        # But what about the hook overhang direction relative to machine vertical?
        # The hook projects radially outward by `depth` along `norm`.
        # Overhang vector from stem to hook apex:
        overhang_vec_part = np.array([norm[0] * depth, norm[1] * depth, 0.0])
        overhang_vec_mach = R[:3, :3] @ overhang_vec_part
        print(f"  Radial hook overhang in machine coords: [{overhang_vec_mach[0]:.3f}, {overhang_vec_mach[1]:.3f}, {overhang_vec_mach[2]:.3f}]")
        print(f"  -> Z'_mach component of overhang: {overhang_vec_mach[2]:.3f} mm")

if __name__ == '__main__':
    inspect()
