import numpy as np

# Tilted transform:
# Y' = Y*cos(45) - Z*sin(45)
# Z' = Y*sin(45) + Z*cos(45) - z_min
# If Y' = -1.351:
# Y*cos(45) - Z*sin(45) = -1.351
# => Y - Z = -1.351 / (sqrt(2)/2) = -1.351 * sqrt(2) = -1.9106 mm.
# So along any line where Y - Z = -1.911 mm, Y' is exactly -1.351 mm!
# For Bracket 4:
# If Z = 5.60 mm:
# Y = 5.60 - 1.911 = 3.689 mm.
# Is (X=8.16, Y=3.689) inside Bracket 4?
# Let's check bracket 4 polygon!
import os, sys
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
import build_part
from shapely.geometry import Point

b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
print("Is (8.16, 3.689) inside b4_poly?", b4_poly.contains(Point(8.16, 3.689)))
print("Distance from (8.16, 3.689) to b4_poly:", b4_poly.distance(Point(8.16, 3.689)))

# Where does Bracket 4 intersect Y - Z = -1.911?
# At X = 8.16:
# Bracket 4 has points (8.000, 4.950) to (8.000, 7.171).
# So at X = 8.16, Bracket 4's Y ranges from 4.950 to 7.171!
# At Y = 4.950, Z can be from 1.0 to 5.60 mm.
# When Y = 4.950:
# Y' = 4.950*cos(45) - Z*sin(45).
# For Z in [1.0, 5.60]:
# At Z = 5.60: Y' = -0.460 mm, Z' = 20.569 mm.
# If Y' = -1.351 at Y = 4.950:
# Z would need to be: 4.950 + 1.911 = 6.861 mm (which is above top of bracket).

# What about at other X positions in Bracket 4?
# In Bracket 4, where does Bracket 4 exist?
# Bracket 4 has the outer spine wall at X in [9.857, 10.791]!
# In the outer spine wall, Y extends from -7.136 to +7.171!
# So for X in [9.857, 10.791], Y = 3.689 IS inside Bracket 4!
# Let's check:
print("Is (10.0, 3.689) inside b4_poly?", b4_poly.contains(Point(10.0, 3.689)))
