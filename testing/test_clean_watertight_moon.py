"""
testing/test_clean_watertight_moon.py
Tests single solid extrusion of the calibrated half moon + top lead-in chamfer.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon

import build_part as bp

cx = 6.279
w_x = 4.20     # 4.20mm wide (anchors into bracket walls, perfectly clear of brass)
base_y = -4.30 # Extended down in -Y (0.05mm clearance to Rib 4 & brass bridge)
apex_y = -3.00 # Calibrated to 6.35mm blade in pinch throat

rx = w_x / 2.0
ry = apex_y - base_y  # 1.30mm

angles = np.linspace(np.pi, 0, 32)
out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
moon_poly = Polygon(out_arc + [(cx - rx, base_y)])

# Extrude from Z=1.00 to 10.50mm
moon_mesh = bp.extrude_shapely_geom(moon_poly, height=10.50 - bp.BASE_THICK)
moon_mesh.apply_translation([0, 0, bp.BASE_THICK])

print(f"Extruded Moon Mesh: Watertight = {moon_mesh.is_watertight}, Volume = {moon_mesh.volume:.2f} mm^3")

# Top Lead-in chamfer:
# We want to shave off 0.25mm from the front face between Z = 8.50mm and Z = 10.52mm
# Slanted cutter box:
chamfer_cutter = trimesh.creation.box([w_x + 2.0, 1.0, 3.0])
# Rotate cutter around X axis by angle
# dx = 0.25mm over dz = 2.0mm -> angle = arctan(0.25/2.0) = 7.125 deg
rot_chamfer = trimesh.transformations.rotation_matrix(np.radians(-7.125), [1, 0, 0])
chamfer_cutter.apply_transform(rot_chamfer)
# Center cutter at apex:
# At Z=10.50: cutter face should be at Y = apex_y - 0.25 = -3.25mm
# At Z=8.50: cutter face should be at Y = apex_y = -3.00mm
chamfer_cutter.apply_translation([cx, apex_y + 0.50, 9.50])

try:
    cut_moon = moon_mesh.difference(chamfer_cutter, engine='manifold')
    print(f"Chamfered Moon Mesh: Watertight = {cut_moon.is_watertight}, Volume = {cut_moon.volume:.2f} mm^3")
except Exception as e:
    print("Chamfer cut error:", e)
