import os, sys
import numpy as np
from shapely.geometry import Polygon, Point
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK

y_axle = 9.279
z_axle = 11.190

orig_pts = [
    (y_axle, z_axle),                          # Center of hub (9.279, 11.190)
    (y_axle, z_axle + 2.10),                  # (9.279, 13.290) - Flush tangent at hub top
    (6.80, 10.80),                             # Re-profiled blend from hub (was 12.20)
    (5.00, 9.20),                              # Re-profiled ramp knee (was 10.00)
    (1.50, 7.40),                              # Active contact tip inside belly cavity
    (1.80, 5.10),                              # Rounded nose bottom inside belly
    (4.50, 5.30),                              # Beam underside
    (y_axle - 1.50, z_axle - 2.50)             # (7.779, 8.690) - Smooth return into hub belly
]
orig_poly = Polygon(orig_pts)

front_pts, rear_pts, y_c = get_brass_contact_2d_profile()
t_half = SHEET_THICK / 2.0
r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
rear_poly = Polygon(r_poly_pts)

print("Original poly intersects rear brass?", orig_poly.intersects(rear_poly))
inter = orig_poly.intersection(rear_poly)
print("Original intersection:", inter)
