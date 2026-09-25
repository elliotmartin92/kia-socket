"""
testing/inspect_brass_geometry_in_bracket.py
Inspects the exact geometry of the brass stamping in Brackets 3 & 4:
- Horizontal U-bridge at the bottom
- Seating Rib 4
- Two vertical upright legs
- Slit and terminal pin
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, Point, box

import build_part as bp

# Bracket 3 & 4
b3 = bp.to_mm_poly(bp.bracket_3_raw_pts)
b4 = bp.to_mm_poly(bp.bracket_4_raw_pts)

print("Bracket 3 bounds:", b3.bounds) # (minx, miny, maxx, maxy)
print("Bracket 4 bounds:", b4.bounds)

# Seating ribs
for i, y_c in enumerate(bp.BRACKET_SEATING_RIB_Y):
    print(f"Rib {i+1}: Y = {y_c:.2f} mm, span [{y_c - 0.3:.2f}, {y_c + 0.3:.2f}] mm")

# In build_part.py, the right slit for the brass terminal tail:
b4_leftmost_x = min(p[0] for p in bp.bracket_4_raw_pts)  # 7.853 mm
slit_y_bot = -18.539 + bp.OUTER_WALL_THICK + bp.SLIT_OFFSET_FROM_WALL  # -15.339 mm
slit_y_top = slit_y_bot + bp.SLIT_LEN_Y                                 # -11.989 mm
print(f"Right Slit hole: X in [{b4_leftmost_x:.3f}, {b4_leftmost_x + bp.SLIT_W_X:.3f}], Y in [{slit_y_bot:.3f}, {slit_y_top:.3f}]")

# Let's inspect where the brass contact stamping sits:
# In testing/model_exact_brass_part.py and testing/visualize_photo_matched_assembly.py:
# The brass stamping has:
# - Tail: X ~ 8.45 mm, Y from -14 to -6 mm
# - Horizontal bridge: spans from X ~ 3.70 to 8.85 mm, sitting across Rib 4 (Y ~ -4.65 mm)
# - Vertical upright spring leaves:
#   Left leaf: X ~ 3.70 to 4.70 mm, Y from -6.0 to +6.0 mm (inside Bracket 3)
#   Right leaf: X ~ 7.85 to 8.85 mm, Y from -6.0 to +6.0 mm (inside Bracket 4)
#   The leaves stand vertically in Z up to Z ~ 15.4 mm.
#   Between the leaves, the central space is:
#   X from ~4.70 mm to ~7.85 mm!
#   And in Y:
#   Above the bridge (Y > -4.35 mm), between the leaves (X in [4.70, 7.85]),
#   what is in that space?
#   THE PLUG BLADE AND THE HALF MOON!

print("\nChannel between leaves in X: ~4.70 mm to ~7.85 mm (Width = ~3.15 mm)")
print("Current Half Moon X: 4.129 to 8.429 mm (Width = 4.30 mm)")
print("Wait! Is current Half Moon wider than the gap between the leaves?")
print("Notice in the photo: the half moon sits behind the leaves or the leaves have retention tabs!")
