import sys
sys.path.insert(0, '.')
import numpy as np
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

ext_pts = np.array(outer_body_poly.exterior.coords)

# Wall sector points between Y=4 and Y=15 with X > 10
wall_sector = ext_pts[(ext_pts[:, 0] > 10) & (ext_pts[:, 1] >= 4.0) & (ext_pts[:, 1] <= 15.0)]
wall_sector = wall_sector[np.argsort(wall_sector[:, 1])]

print(f"Wall Exterior Face (total {len(wall_sector)} points):")
for pt in wall_sector[::max(1, len(wall_sector)//15)]:
    r = np.sqrt(pt[0]**2 + pt[1]**2)
    print(f"Y = {pt[1]:6.2f} mm -> X_ext = {pt[0]:6.2f} mm | R = {r:5.2f} mm")

int_pts = np.array(inner_poly.exterior.coords)
int_sector = int_pts[(int_pts[:, 0] > 10) & (int_pts[:, 1] >= 4.0) & (int_pts[:, 1] <= 15.0)]
int_sector = int_sector[np.argsort(int_sector[:, 1])]

print(f"\nWall Interior Face (total {len(int_sector)} points):")
for pt in int_sector[::max(1, len(int_sector)//15)]:
    r = np.sqrt(pt[0]**2 + pt[1]**2)
    print(f"Y = {pt[1]:6.2f} mm -> X_int = {pt[0]:6.2f} mm | R = {r:5.2f} mm")
