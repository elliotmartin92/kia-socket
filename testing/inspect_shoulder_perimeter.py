import os, sys
from shapely.geometry import Polygon, box
from shapely.affinity import translate, rotate

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from build_part import (
    get_exact_base_polygon, INSERT_BODY_W_X, INSERT_BODY_LEN_Y,
    INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_KEY_W_X, INSERT_KEY_LEN_Y
)

base_poly, outer_body_poly, _ = get_exact_base_polygon()
cx_right = 8.453
cy = -13.589

shroud_r_shoulder = box(cx_right - INSERT_BODY_W_X/2, cy - INSERT_BODY_LEN_Y/2,
                        cx_right + INSERT_BODY_W_X/2, cy + INSERT_BODY_LEN_Y/2)

print(f"Right Shroud Shoulder bounds: {shroud_r_shoulder.bounds}")
print(f"outer_body_poly contains shroud_r_shoulder? {outer_body_poly.contains(shroud_r_shoulder)}")
diff = shroud_r_shoulder.difference(outer_body_poly)
print(f"Difference area (sticking out): {diff.area:.6f} mm^2")
if diff.area > 0:
    print(f"Difference bounds: {diff.bounds}")
    # where does it stick out?
    print(f"Max X of shoulder: {shroud_r_shoulder.bounds[2]}")
    # let's find the outer perimeter X near cy
    coords = list(outer_body_poly.exterior.coords)
    # find coords near Y in [-16.5, -10.5]
    nearby = [p for p in coords if -17 <= p[1] <= -10 and p[0] > 0]
    print(f"Outer perimeter points near right slit: {nearby}")
