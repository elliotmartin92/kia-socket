from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import numpy as np

y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

hub_circle = Point(y_axle, z_axle).buffer(r_hub)

# Let's inspect where the arm emerges from the hub:
reinf_pts = [
    (y_axle, z_axle),
    (y_axle, z_axle + r_hub),
    (8.20, z_axle + r_hub - 0.20),   # (8.20, 13.090)
    (6.80, 11.60),                   # (6.80, 11.600)
    (5.00, 9.20),
    (1.50, 7.40),
    (1.80, 5.10),
    (4.50, 5.30),
    (7.50, 8.40),                    # (7.50, 8.40) - smooth underside return
    (y_axle, z_axle - r_hub)         # (9.279, 9.090)
]

poly_arm = Polygon(reinf_pts)
outside = poly_arm.difference(hub_circle)
print("Outside area:", outside.area)
print("Outside bounds:", outside.bounds)
crossings = poly_arm.boundary.intersection(hub_circle.boundary)
print("Boundary crossings with hub:", crossings)
