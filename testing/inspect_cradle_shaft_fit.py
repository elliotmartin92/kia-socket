"""
testing/inspect_cradle_shaft_fit.py
Inspect the exact cradle center, shaft pin center, and tower socket geometry.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE, PIN_DIAMETER
from build_part import build_clean_shaft_towers_mesh, build_exact_3d_model

# Let's inspect build_clean_shaft_towers_mesh in detail
# The cradle arc in build_part.py:
# y_shaft = 10.200, z_cradle_center = 12.590, r_shaft = 1.000
# Meanwhile, in build_shaft.py:
# Y_AXLE = 7.666, Z_AXLE = 12.590, PIN_DIAMETER = 1.900 (r_pin = 0.950)

print(f"Cradle Axis in build_part.py: Y = 10.200 mm, Z = 12.590 mm")
print(f"Shaft Axis in build_shaft.py: Y = {Y_AXLE:.3f} mm, Z = {Z_AXLE:.3f} mm")
print(f"Y mismatch = {10.200 - Y_AXLE:.3f} mm!")

# Also let's check the size of the shaft:
# Pin diameter: 1.90mm (radius 0.95mm).
# What is the size/strength of a 1.90mm FDM printed pin?
# In FDM 3D printing (0.4mm nozzle, layer height 0.12-0.20mm), a Ø1.90mm or Ø2.00mm horizontal pin is only ~5-10 layers thick and has very little layer adhesion strength if printed vertically, or is tiny if printed horizontally.
# The user says:
# "the shaft is causing issues, I think making it larger along with making the corresponding changes in the towers may help given that the current shaft is so small"
