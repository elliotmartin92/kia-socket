from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import numpy as np

y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

flank_collar = Point(y_axle, z_axle).buffer(r_hub - 0.05)
hub_circle = Point(y_axle, z_axle).buffer(r_hub)

for z_blend in [10.80, 11.50, 12.20, 12.80]:
    pts = [
        (y_axle, z_axle),
        (y_axle, z_axle + r_hub),
        (6.80, z_blend),
        (5.00, 9.20),
        (1.50, 7.40),
        (1.80, 5.10),
        (4.50, 5.30),
        (y_axle - 1.50, z_axle - 2.50)
    ]
    poly = unary_union([flank_collar, Polygon(pts)])
    inter = poly.intersection(hub_circle.boundary)
    print(f"z_blend = {z_blend:.2f}: intersection arc length along hub = {inter.length:.3f} mm")
