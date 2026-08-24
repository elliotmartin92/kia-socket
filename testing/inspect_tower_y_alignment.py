"""
testing/inspect_tower_y_alignment.py
Analyze Bracket 3 geometry and tower Y coordinates.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np

# Bracket 3 raw points:
# (1.766,  7.171), (4.705,  7.171), (4.705,  4.800), (3.708,  4.800),
# (3.708,  6.250), (2.851,  6.250), (2.851, -6.086), (4.565, -6.086),
# (4.565, -7.171), (1.766, -7.171), (1.766,  7.171)

print("=== Bracket 3 Segment Analysis ===")
print("1. Outer top wall: Y = 7.171 mm (X in [1.766, 4.705])")
print("2. Outer right wall: X = 4.705 mm (Y in [4.800, 7.171])")
print("3. Bottom of hook: Y = 4.800 mm (X in [3.708, 4.705])")
print("4. Hook inner vertical wall: X = 3.708 mm (Y in [4.800, 6.250])")
print("5. TOP INNER WALL OF BRACKET 3: Y = 6.250 mm (X in [2.851, 3.708])")
print("6. Inner vertical guide channel: X = 2.851 mm (Y in [-6.086, 6.250])")

# Left Tower currently:
# X in [3.900, 5.400]
# Y_base in [7.171, 13.771]
# Y_top in [7.471, 13.101]
# Y_shaft = 10.200
# Through-hole in baseplate: X in [7.608, 12.960], Y in [8.570, 13.082] (center Y = 10.826mm or 10.200mm)

print("\n=== Tower Shift Options ===")
delta_y = 6.250 - 7.171
print(f"Delta Y to align tower base with top inner wall of bracket 3: {delta_y:.3f} mm (-0.921 mm)")

# Option A: Shift the entire tower & shaft system by delta_y = -0.921mm:
# y_min_base = 6.250
# y_max_base = 13.771 - 0.921 = 12.850 mm
# y_min_top = 7.471 - 0.921 = 6.550 mm
# y_max_top = 13.101 - 0.921 = 12.180 mm
# y_shaft = 10.200 - 0.921 = 9.279 mm
# Through hole Y in [8.570 - 0.921, 13.082 - 0.921] = [7.649, 12.161] mm (center Y = 9.905mm)
# Left tower X: [3.900, 5.400]
# Bracket 3 hook tip is at X = 3.708 mm -> Clearance between Bracket 3 hook and Left Tower = 3.900 - 3.708 = 0.192 mm!
# And Bracket 3 outer right edge is X = 4.705 mm at Y in [4.800, 7.171].
# When Left Tower base is at Y = 6.250 mm, the tower spans X in [3.900, 5.400] at Y in [6.250, 12.850].
# Where X overlaps [3.900, 4.705] in Y [6.250, 7.171]:
# They merge seamlessly into a single solid wall!
