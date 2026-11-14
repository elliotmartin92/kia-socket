import sys, os
sys.path.insert(0, os.path.abspath('.'))
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import numpy as np

y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

flank_collar = Point(y_axle, z_axle).buffer(r_hub - 0.05)

poly_pts_cam = [
    (y_axle, z_axle),                          # Center of hub (9.279, 11.190)
    (y_axle, z_axle + r_hub),                  # (9.279, 13.290) - Flush tangent at hub top
    (6.80, 10.80),                             # Re-profiled blend from hub (was 12.20)
    (5.00, 9.20),                              # Re-profiled ramp knee (was 10.00)
    (1.50, 7.40),                              # Active contact tip inside belly cavity
    (1.80, 5.10),                              # Rounded nose bottom inside belly
    (4.50, 5.30),                              # Beam underside
    (y_axle - 1.50, z_axle - 2.50)             # (7.779, 8.690) - Smooth return into hub belly
]
poly_cam_arm = Polygon(poly_pts_cam)
poly_cam = unary_union([flank_collar, poly_cam_arm])

print("poly_cam exterior coords:")
for c in poly_cam.exterior.coords:
    print(f"  ({c[0]:.3f}, {c[1]:.3f})")
