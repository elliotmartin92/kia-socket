"""
testing/check_bracket_4_collision.py
Simulate the 3D interaction between the rocker mechanism and Bracket 4
at rest and across the full rotation stroke (theta = 0° to 12°).
Find the exact location and magnitude of interference or close clearance.
"""

import sys, os
import trimesh
import numpy as np
from shapely.geometry import Polygon, Point

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import bracket_4_raw_pts, BASE_THICK, BRACKET_HEIGHT
from build_shaft import (
    build_shaft_rocker_mesh,
    Y_AXLE, Z_AXLE,
    HOLE_X_CENTER, PLUNGER_WIDTH_X,
    HUB_WIDTH, X_TOWER_CENTER
)

# 1. Build Bracket 4 3D mesh
poly_b4 = Polygon(bracket_4_raw_pts)
m_b4 = trimesh.creation.extrude_polygon(poly_b4, height=BRACKET_HEIGHT)
m_b4.apply_translation([0, 0, BASE_THICK])

print("=" * 80)
print("BRACKET 4 GEOMETRY & BOUNDS")
print("=" * 80)
b4_bounds = m_b4.bounds
print(f"Bracket 4 X span: [{b4_bounds[0,0]:.3f}, {b4_bounds[1,0]:.3f}]")
print(f"Bracket 4 Y span: [{b4_bounds[0,1]:.3f}, {b4_bounds[1,1]:.3f}]")
print(f"Bracket 4 Z span: [{b4_bounds[0,2]:.3f}, {b4_bounds[1,2]:.3f}]")

# Check rocker subparts
subparts = build_shaft_rocker_mesh(in_assembly_coords=True, return_subparts=True)

print("\nROCKER SUBPARTS X BOUNDS:")
for name, p in subparts.items():
    print(f"  {name:<10}: X in [{p.bounds[0,0]:.3f}, {p.bounds[1,0]:.3f}], Y in [{p.bounds[0,1]:.3f}, {p.bounds[1,1]:.3f}], Z in [{p.bounds[0,2]:.3f}, {p.bounds[1,2]:.3f}]")

print("\n" + "=" * 80)
print("ROTATION STROKE CLEARANCE / INTERFERENCE CHECK")
print("=" * 80)

angles_deg = np.linspace(0.0, 12.0, 25)

for angle in [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0]:
    # Rotate rocker around axle (Y_AXLE, Z_AXLE)
    # Rotation matrix around X axis through axle center
    rad = np.radians(angle)
    # The rocker rotates counterclockwise or clockwise?
    # When hot blade pushes cam down: cam moves down in -Z, forward in +Y -> rotation angle is positive around X
    rot_mat = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
    
    # Check collision for each subpart against Bracket 4
    print(f"\n--- Rotation Angle: {angle:.1f}° ---")
    any_collision = False
    
    for name, p in subparts.items():
        p_rot = p.copy()
        p_rot.apply_transform(rot_mat)
        
        # Check bounding box overlap first
        b_p = p_rot.bounds
        overlap_x = max(0, min(b_p[1,0], b4_bounds[1,0]) - max(b_p[0,0], b4_bounds[0,0]))
        overlap_y = max(0, min(b_p[1,1], b4_bounds[1,1]) - max(b_p[0,1], b4_bounds[0,1]))
        overlap_z = max(0, min(b_p[1,2], b4_bounds[1,2]) - max(b_p[0,2], b4_bounds[0,2]))
        
        if overlap_x > 0 and overlap_y > 0 and overlap_z > 0:
            # Boxes overlap! Check minimum distance or boolean intersection
            # Sample points of p_rot that fall within b4_bounds expanded by 1mm
            mask = (
                (p_rot.vertices[:, 0] >= b4_bounds[0,0] - 0.5) & (p_rot.vertices[:, 0] <= b4_bounds[1,0] + 0.5) &
                (p_rot.vertices[:, 1] >= b4_bounds[0,1] - 0.5) & (p_rot.vertices[:, 1] <= b4_bounds[1,1] + 0.5) &
                (p_rot.vertices[:, 2] >= b4_bounds[0,2] - 0.5) & (p_rot.vertices[:, 2] <= b4_bounds[1,2] + 0.5)
            )
            pts_near = p_rot.vertices[mask]
            if len(pts_near) > 0:
                # Test inside polygon of bracket 4
                inside_xy = [poly_b4.contains(Point(pt[0], pt[1])) for pt in pts_near]
                if any(inside_xy):
                    print(f"  >>> COLLISION DETECTED with {name}!")
                    any_collision = True
                else:
                    # Find min distance to polygon
                    dists = [poly_b4.distance(Point(pt[0], pt[1])) for pt in pts_near]
                    min_d = min(dists)
                    print(f"  {name}: Close proximity! Min XY clearance to Bracket 4: {min_d:.3f} mm")
                    if min_d < 0.15:
                        print(f"    WARNING: Clearance is critically tight ({min_d:.3f} mm)!")
    if not any_collision:
        print("  No hard boolean intersection.")
