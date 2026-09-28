"""
testing/inspect_cantilever_rotation.py
Diagnostic script to investigate why the cantilever doesn't move smoothly
and feels biphasic between positions.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box, LineString

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_shaft as bs
import build_part as bp
import build_clamp as bc

def inspect_rotation():
    print("=" * 70)
    print("DIAGNOSTIC AUDIT: CANTILEVER / ROCKER ROTATION & CLEARANCES")
    print("=" * 70)
    
    # 1. Check cradle geometry vs pin geometry
    y_axle = bs.Y_AXLE  # 9.279
    z_axle = bs.Z_AXLE  # 12.590
    pin_r = bs.PIN_DIAMETER / 2.0  # 1.40 mm (Ø2.80)
    cradle_r = 1.50                # 1.50 mm (Ø3.00)
    throat_w = bp.TOWER_THROAT_W   # 2.60 mm
    
    print(f"Axle Pin: Diameter = {bs.PIN_DIAMETER:.2f} mm (Radius = {pin_r:.2f} mm)")
    print(f"Tower Cradle: Diameter = {cradle_r*2:.2f} mm (Radius = {cradle_r:.2f} mm)")
    print(f"Tower Cradle Throat Opening: {throat_w:.2f} mm")
    print(f"Throat Interference with Pin: {bs.PIN_DIAMETER - throat_w:.2f} mm (snap-fit interference)")
    
    # 2. Plunger vs Through-Hole across rotation angles
    # Baseplate floor is at Z in [0.00, 1.00]
    # Through-hole bounds:
    # X in [7.608, 12.960] (width 5.352 mm, centered at 10.284)
    # Y in [8.570, 13.082] (length 4.512 mm, centered at 10.826)
    
    hole_y_min = 8.570
    hole_y_max = 13.082
    hole_x_min = 7.608
    hole_x_max = 12.960
    
    # Let's inspect the plunger polygon at rest and as it rotates
    # Plunger in build_shaft.py:
    plunger_mesh = bs.build_shaft_rocker_mesh(in_assembly_coords=True)
    
    # Slice the plunger mesh at Z = 1.00 mm (top of floor hole) and Z = 0.00 mm (bottom of floor hole)
    for angle_deg in np.linspace(-5, 15, 21):
        rad = np.radians(angle_deg)
        # Rotate around axle axis (parallel to X axis at Y=y_axle, Z=z_axle)
        # Note: rotation around X axis:
        # [x, y, z] -> [x, y_axle + cos*(y-y_axle) - sin*(z-z_axle), z_axle + sin*(y-y_axle) + cos*(z-z_axle)]
        # For plug insertion, cam is pushed DOWN (-Z), which corresponds to positive/CCW or negative angle:
        rot_mat = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[bs.X_TOWER_CENTER, y_axle, z_axle])
        rotated_mesh = plunger_mesh.copy()
        rotated_mesh.apply_transform(rot_mat)
        
        # Check slice at Z = 1.00 mm and Z = 0.50 mm and Z = 0.00 mm
        for z_slice in [1.00, 0.50, 0.00]:
            slice_section = rotated_mesh.section(plane_origin=[bs.X_TOWER_CENTER, y_axle, z_slice], plane_normal=[0, 0, 1])
            if slice_section is not None:
                verts = slice_section.vertices
                # Only check vertices within the hole X range
                hole_verts = verts[(verts[:, 0] >= hole_x_min - 1) & (verts[:, 0] <= hole_x_max + 1)]
                if len(hole_verts) > 0:
                    y_min_plunger = hole_verts[:, 1].min()
                    y_max_plunger = hole_verts[:, 1].max()
                    
                    gap_front = y_min_plunger - hole_y_min
                    gap_rear = hole_y_max - y_max_plunger
                    
                    if gap_front < 0 or gap_rear < 0:
                        print(f"COLLISION at angle {angle_deg:+5.1f} deg, Z = {z_slice:.2f}: Plunger Y [{y_min_plunger:.2f}, {y_max_plunger:.2f}], Hole Y [{hole_y_min:.2f}, {hole_y_max:.2f}] -> Gap Front: {gap_front:+.2f} mm, Gap Rear: {gap_rear:+.2f} mm")

if __name__ == '__main__':
    inspect_rotation()
