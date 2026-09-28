"""
testing/check_brass_clearance_at_rest.py
Tests clearance between seated brass insert and candidate cam profiles at theta = 0°.
"""
import os, sys
import numpy as np
from shapely.geometry import Polygon, box, Point

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
import build_part as bp

print("=" * 80)
print("TESTING BRASS CLEARANCE AT REST (THETA = 0°)")
print("=" * 80)

# Seating height of brass:
# Floor is at Z = 1.00 mm. Seating ribs are 1.15 mm tall (Z in [1.00, 2.15] mm).
# Brass insert base sits at Z = 2.15 mm.
# From testing/model_exact_brass_part.py and testing/inspect_brass_geometry_in_bracket.py:
# Brass part features:
# Stamped brass piece in Brackets 3 & 4:
# - Seating foot at Z = 2.15 mm
# - Rear bridge at Y = -6.0 mm to -4.3 mm
# - Two vertical spring fingers rising in Z
# - Pinching throat between fingers:
#   At the bottom, belly cavity width in Y is 5.00mm (from Y = -2.50 to +2.50 or Y = -2.20 to +2.80)
#   At Z = 9.40mm (measured relative to floor: 2.15 + 7.25 = 9.40mm), the fingers pinch together
#   forming a throat at Y in [0.0, 3.5]
#   Wait! Where is the brass bridge / crossbar?
# Let's inspect testing/model_exact_brass_part.py!
