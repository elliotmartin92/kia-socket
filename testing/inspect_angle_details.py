"""
testing/inspect_angle_details.py
Detailed inspection of angles 198.6, 205.0, etc.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

for ang in [198.6, 205.0, 210.0, 215.0, 220.0, 225.0, 230.0]:
    m = build_shaft_rocker_mesh(in_assembly_coords=True)
    rot = trimesh.transformations.rotation_matrix(np.radians(ang), [1, 0, 0])
    m.apply_transform(rot)
    b = m.bounds
    m.apply_translation([
        -(b[0, 0] + b[1, 0])/2.0,
        -(b[0, 1] + b[1, 1])/2.0,
        -b[0, 2]
    ])
    
    # Subpart Z mins
    v = m.vertices
    # Pins: |X| > 3.75
    v_pins = v[np.abs(v[:, 0]) > 3.75]
    z_pins = np.min(v_pins[:, 2]) if len(v_pins) > 0 else 999
    
    # Hub: |X| <= 3.75 and |Y| < 2.0 (approx)
    # Cam: X in [-3.75, -1.05]
    # Plunger: Y < -1.0
    v_plunger = v[v[:, 1] < -2.0]
    z_plunger = np.min(v_plunger[:, 2]) if len(v_plunger) > 0 else 999
    
    # What touches Z=0?
    v_bed = v[v[:, 2] < 0.05]
    
    print(f"Angle {ang:5.1f}°:")
    print(f"  Pin Z_min: {z_pins:.2f} mm")
    print(f"  Plunger Z_min: {z_plunger:.2f} mm")
    print(f"  Bed contact X span: [{np.min(v_bed[:, 0]):.2f}, {np.max(v_bed[:, 0]):.2f}]")
    print(f"  Bed contact Y span: [{np.min(v_bed[:, 1]):.2f}, {np.max(v_bed[:, 1]):.2f}]")
    print(f"  Total mesh Z height: {m.bounds[1, 2]:.2f} mm")
    print()
