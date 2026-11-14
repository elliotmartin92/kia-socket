import numpy as np
import trimesh
import os, sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft

# Let's inspect the exact dimensions and clearances in both flat and tilted coordinates.
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
print("Bracket 4 flat points:")
for p in build_part.bracket_4_raw_pts:
    print(p)

# In flat coords:
# Plunger: X in [8.484, 12.084] (width 3.60, center 10.284)
# Hub: X in [5.80, 12.70] (width 6.90, center 9.250)
# Cam: X in [5.80, 7.70] (width 1.90, center 6.75)
# Bracket 4:
# Top face of Bracket 4 is at Z = 5.60 mm (BASE_THICK 1.00 + BRACKET_HEIGHT 4.60 = 5.60 mm).
# Points of Bracket 4 at top:
# (10.791,  7.171) -> outer top corner
# (8.000,  7.171)  -> inner top corner
# (8.000,  4.950)  -> inner hook corner
# (8.900,  4.950)  -> hook recess step
# (8.900,  6.400)  -> pocket ceiling
# (9.857,  6.400)  -> outer pocket corner
# (9.857, -6.200)  -> spine inner face
# (8.150, -6.200)  -> bottom hook corner
# (8.150, -7.136)  -> bottom step
# (10.791, -7.136) -> bottom outer corner

# Where is the hub relative to Bracket 4?
# Hub spans X in [5.80, 12.70].
# So Bracket 4 spans X in [8.000, 10.791].
# Overlap in X between Bracket 4 and Hub is [8.000, 10.791]!
# But what about the Plunger blade?
# Plunger blade is at X in [8.484, 12.084]!
# So in X:
# [8.000, 8.484] is Bracket 4 AND Hub, but NOT Plunger! That is a 0.484mm strip between X=8.000 and X=8.484!
# Wait! What about Rib 3? Rib 3 is at X in [11.60, 12.60] (Rib 3 is outside Bracket 4, X > 10.791).
# What about between Plunger and Right Tower?
# Right tower is at X in [13.10, 14.60].
# Right Flank Rib (Rib 3) is at X in [11.60, 12.60].
# Plunger is at X in [8.484, 12.084].
# Wait, Plunger is 3.60mm wide from 8.484 to 12.084!
# Wait! Where does Plunger connect to Hub?
# In flat coords:
# Plunger connects to Hub at Y=9.279, Z=11.190!
# But plunger blade extends down through the baseplate through-hole!
# Where does the through-hole go?
# Through-hole is at Y in [8.57, 13.75].
# But Bracket 4 is at Y <= 7.171!
