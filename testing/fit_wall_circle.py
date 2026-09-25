import sys
sys.path.insert(0, '.')
import numpy as np
from scipy.optimize import minimize
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Extract points from outer_body_poly that belong to the main cylindrical rim
# Exclude the 4 clips (angles near 45, 135, 211, 327), ears (Y in [-4, 4], |X| > 19), tabs
pts = np.array(outer_body_poly.exterior.coords)

cyl_pts = []
for p in pts:
    x, y = p
    r = np.sqrt(x**2 + y**2)
    th = np.degrees(np.arctan2(y, x)) % 360
    
    # Exclude side ears
    if abs(y) < 4.5 and abs(x) > 19.0:
        continue
    # Exclude top tab
    if y > 18.0 and abs(x) < 5.0:
        continue
    # Exclude bottom detents / flats
    if y < -16.0:
        continue
    # Exclude clip protrusions
    # Clip angles: 45, 135, 211.3, 327.5 (+/- 12 deg)
    is_clip = False
    for ca in [45.0, 135.0, 211.3, 327.5]:
        if abs((th - ca + 180) % 360 - 180) < 12.0:
            is_clip = True
            break
    if is_clip and r > 19.8:
        continue
    cyl_pts.append(p)

cyl_pts = np.array(cyl_pts)
print(f"Selected {len(cyl_pts)} cylindrical wall points")

# Fit circle (cx, cy, R)
def loss(params):
    cx, cy, R = params
    return np.sum((np.sqrt((cyl_pts[:, 0] - cx)**2 + (cyl_pts[:, 1] - cy)**2) - R)**2)

res = minimize(loss, [0.0, 0.0, 19.5])
cx, cy, R = res.x
print(f"Fitted circle to outer wall exterior: Center=({cx:.3f}, {cy:.3f}), Radius R = {R:.3f} mm")
print(f"Residual mean: {np.mean(np.abs(np.sqrt((cyl_pts[:,0]-cx)**2 + (cyl_pts[:,1]-cy)**2) - R)):.3f} mm")

# Wall interior circle:
R_int = R - OUTER_WALL_THICK
print(f"Wall interior radius: R_int = {R_int:.3f} mm")
