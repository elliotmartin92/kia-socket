import sys, os
sys.path.insert(0, os.path.abspath('.'))
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import numpy as np

y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

# Original poly_pts_cam
orig_pts = [
    (y_axle, z_axle),                          # Center of hub (9.279, 11.190)
    (y_axle, z_axle + r_hub),                  # (9.279, 13.290) - Flush tangent at hub top
    (6.80, 10.80),                             # Re-profiled blend from hub (was 12.20)
    (5.00, 9.20),                              # Re-profiled ramp knee (was 10.00)
    (1.50, 7.40),                              # Active contact tip inside belly cavity
    (1.80, 5.10),                              # Rounded nose bottom inside belly
    (4.50, 5.30),                              # Beam underside
    (y_axle - 1.50, z_axle - 2.50)             # (7.779, 8.690) - Smooth return into hub belly
]

# Proposed reinforced profile:
# 1. Maintain (y_axle, z_axle + r_hub) = (9.279, 13.290)
# 2. Add an intermediate tangential / crowning point at (8.00, 12.90) or arch over the top of the hub,
#    so the top face ramps smoothly down to (6.80, 11.60) -> (5.00, 9.20)
# 3. For the underside return: extend deeper into the belly: (y_axle - 1.20, z_axle - 2.80) or follow the hub bottom!
# Let's test this in 2D:

hub_circle = Point(y_axle, z_axle).buffer(r_hub)

poly_orig = unary_union([Point(y_axle, z_axle).buffer(r_hub - 0.05), Polygon(orig_pts)])
inter_orig = poly_orig.intersection(hub_circle.boundary)
print(f"Original neck intersection arc length: {inter_orig.length:.3f} mm")

# Let's test a sequence of top blend points
for z_top_blend in [11.20, 11.60, 12.00, 12.40]:
    reinf_pts = [
        (y_axle, z_axle),
        (y_axle, z_axle + r_hub),
        (8.20, z_axle + r_hub - 0.20),   # Smooth tangential crown coming off the hub apex (8.20, 13.09)
        (6.80, z_top_blend),             # Robust neck blend
        (5.00, 9.20),                    # Exact operational ramp knee
        (1.50, 7.40),                    # Exact operational contact tip
        (1.80, 5.10),                    # Exact nose bottom
        (4.50, 5.30),                    # Exact underside
        (y_axle - 1.20, z_axle - 2.80),  # Deeper bottom root return
        (y_axle, z_axle - r_hub)         # Anchor right into bottom of hub!
    ]
    poly_reinf = unary_union([Point(y_axle, z_axle).buffer(r_hub), Polygon(reinf_pts)])
    inter_reinf = poly_reinf.intersection(hub_circle.boundary)
    print(f"z_top_blend = {z_top_blend:.2f}: intersection arc length = {inter_reinf.length:.3f} mm (Area = {poly_reinf.area:.2f} mm^2)")
