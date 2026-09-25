import sys
sys.path.insert(0, '.')
import numpy as np
import matplotlib.pyplot as plt
from build_part import outer_pts, get_exact_base_polygon
import build_clamp

_, outer_body_poly, _ = get_exact_base_polygon()
clamp = build_clamp.build_tower_clamp_mesh('right', in_assembly_coords=True)

# Let's inspect points on the outer perimeter near the 45 deg clip (X > 10, Y > 5)
pts = np.array(outer_body_poly.exterior.coords)
clip_region = pts[(pts[:, 0] > 10) & (pts[:, 1] > 5)]

# Calculate radius from origin (0, 0)
radii = np.sqrt(pts[:, 0]**2 + pts[:, 1]**2)

print("Radius range around perimeter:")
print("Min radius:", radii.min())
print("Max radius:", radii.max())

# Let's find the cylindrical wall radius near 30 deg - 60 deg
# Excluding the clip protrusion
for angle_deg in [0, 15, 30, 45, 60, 75, 90]:
    rad = np.radians(angle_deg)
    # Find points near this angle
    angles = np.arctan2(pts[:, 1], pts[:, 0])
    mask = np.abs(angles - rad) < np.radians(2.0)
    if np.any(mask):
        print(f"Angle {angle_deg:2d} deg: R = {radii[mask].mean():.2f} mm (pts: {pts[mask][0]})")

# What is the inner face of the wall?
# The outer wall thickness is OUTER_WALL_THICK = 1.20mm.
# If the wall is at R_outer, the wall inner face is at R_inner = R_outer - 1.20mm.
