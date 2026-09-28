"""
testing/analyze_bracket_4_collision_details.py
Detailed analysis of the collision with Bracket 4:
1. Exact coordinates where Cam hits Bracket 4.
2. Does the Plunger arm or Web also have close clearance to Bracket 4?
3. What is the optimal X-trimming or thinning for Cam and Plunger to give
   ample (+0.5mm to +1.0mm) free running clearance to Bracket 4?
"""

import sys, os
import trimesh
import numpy as np
from shapely.geometry import Polygon, Point, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import bracket_4_raw_pts, BASE_THICK, BRACKET_HEIGHT
from build_shaft import (
    build_shaft_rocker_mesh,
    Y_AXLE, Z_AXLE,
    HOLE_X_CENTER, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER,
    HUB_WIDTH, X_TOWER_CENTER
)

poly_b4 = Polygon(bracket_4_raw_pts)
m_b4 = trimesh.creation.extrude_polygon(poly_b4, height=BRACKET_HEIGHT)
m_b4.apply_translation([0, 0, BASE_THICK])

# Look at Bracket 4 top wall geometry in detail
# The top wall of Bracket 4 has X in [8.000, 10.791], Y in [4.950, 7.171], Z in [1.000, 5.600]
print("Bracket 4 top-left corner vertices (closest to rocker):")
for p in bracket_4_raw_pts:
    if p[0] <= 9.0 and p[1] >= 4.0:
        print(f"  ({p[0]:.3f}, {p[1]:.3f})")

# Look at Cam in build_shaft.py:
# CAM_WIDTH_X = 2.70
# CAM_X_CENTER = 6.28
# x_cam_start = max(x_c - hub_w/2.0, cam_x_c - cam_w_x/2.0)
# actual_cam_w = min(cam_w_x, (x_c + hub_w/2.0) - x_cam_start)
# x_cam_start = max(9.25 - 3.75, 6.28 - 1.35) = max(5.50, 4.93) = 5.50 mm!
# actual_cam_w = 2.70 mm!
# So Cam X is [5.50, 5.50 + 2.70] = [5.50, 8.20] mm!

print(f"\nCurrent Cam bounds in X: [5.500, 8.200] mm (Width = 2.70 mm)")
print(f"Bracket 4 innermost X:   8.000 mm")
print(f">>> Direct X interference: {8.200 - 8.000:.3f} mm overlap with Bracket 4!")

# Now check Plunger:
# HOLE_X_CENTER = 10.284
# PLUNGER_WIDTH_X = 4.40
# X span: [10.284 - 2.20, 10.284 + 2.20] = [8.084, 12.484] mm!
print(f"\nCurrent Plunger bounds in X: [8.084, 12.484] mm (Width = 4.40 mm)")
print(f"Plunger clearance to Bracket 4 (at X=8.000): {8.084 - 8.000:.3f} mm")

# Where is the through hole in the baseplate?
# From build_part.py: hole_info = (10.284, 10.826, 5.352, 4.512)
# Hole X span: [10.284 - 5.352/2, 10.284 + 5.352/2] = [7.608, 12.960] mm!
# Hole Y span: [8.570, 13.750] mm!
print(f"\nThrough-hole X span: [7.608, 12.960] mm (Width = 5.352 mm)")

# Check what happens during rotation:
# When rocker rotates by theta, does plunger hit the front/top of bracket 4?
print("\n" + "=" * 80)
print("TESTING DIFFERENT CAM & PLUNGER WIDTHS")
print("=" * 80)

for cam_w in [2.70, 2.40, 2.20, 2.00, 1.80]:
    for plung_w in [4.40, 4.00, 3.80, 3.60, 3.20]:
        # Test collision across 0 to 12 degrees
        has_collision = False
        min_clearance = float('inf')
        
        # Build test rocker with these dimensions
        subparts = build_shaft_rocker_mesh(
            cam_w_x=cam_w,
            plunger_w_x=plung_w,
            in_assembly_coords=True,
            return_subparts=True
        )
        
        for angle in np.linspace(0, 12, 13):
            rad = np.radians(angle)
            rot_mat = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
            
            for name in ['cam', 'plunger']:
                p = subparts[name].copy()
                p.apply_transform(rot_mat)
                
                # Check points in Z range of Bracket 4 [1.0, 5.6] and Y range [4.0, 7.5]
                mask = (p.vertices[:, 2] >= 1.0) & (p.vertices[:, 2] <= 5.6) & (p.vertices[:, 1] >= 4.0) & (p.vertices[:, 1] <= 7.5)
                pts = p.vertices[mask]
                if len(pts) > 0:
                    for pt in pts:
                        p_2d = Point(pt[0], pt[1])
                        if poly_b4.contains(p_2d):
                            has_collision = True
                            break
                        d = poly_b4.distance(p_2d)
                        min_clearance = min(min_clearance, d)
                if has_collision:
                    break
            if has_collision:
                break
                
        status = f"COLLISION" if has_collision else f"CLEAR (min dist = {min_clearance:.3f} mm)"
        if not has_collision and min_clearance > 0.30:
            print(f"Cam W = {cam_w:.2f} mm, Plunger W = {plung_w:.2f} mm -> {status}")
