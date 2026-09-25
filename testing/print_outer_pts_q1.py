import sys
sys.path.insert(0, '.')
import numpy as np
from build_part import outer_pts

pts = outer_pts[(outer_pts[:, 0] > 0) & (outer_pts[:, 1] > 0)]
pts = pts[np.argsort(np.arctan2(pts[:, 1], pts[:, 0]))]

print(f"{'X (mm)':<10} | {'Y (mm)':<10} | {'R (mm)':<10} | {'Angle (deg)':<10}")
print("-" * 45)
for p in pts:
    r = np.sqrt(p[0]**2 + p[1]**2)
    ang = np.degrees(np.arctan2(p[1], p[0]))
    print(f"{p[0]:8.3f}   | {p[1]:8.3f}   | {r:8.3f}   | {ang:8.2f}")
