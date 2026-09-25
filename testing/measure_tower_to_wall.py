import sys
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import Point, box, Polygon
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Right Tower bounds:
# X in [13.10, 14.60]
# Top Y in [6.55, 12.18]
# Pivot axle at Y = 9.279mm
# Throat width = 2.60mm -> front prong top Y in [6.55, 7.98], rear prong top Y in [10.58, 12.18]

print(f"{'Feature':<30} | {'X':<6} | {'Y':<6} | {'X_int_wall':<10} | {'Margin to Int Wall'}")
print("-" * 75)

for y in [6.55, 7.10, 8.00, 9.28, 10.58, 11.55, 12.18]:
    # Find X of inner_poly at this Y for X > 10
    # Ray from (10, y) to (20, y)
    from shapely.geometry import LineString
    line = LineString([(10, y), (20, y)])
    inter = inner_poly.exterior.intersection(line)
    if inter.geom_type == 'Point':
        x_int = inter.x
    elif hasattr(inter, 'geoms') and len(inter.geoms) > 0:
        x_int = inter.geoms[-1].x
    else:
        x_int = np.nan
        
    line_ext = outer_body_poly.exterior.intersection(line)
    if line_ext.geom_type == 'Point':
        x_ext = line_ext.x
    elif hasattr(line_ext, 'geoms') and len(line_ext.geoms) > 0:
        x_ext = line_ext.geoms[-1].x
    else:
        x_ext = np.nan
        
    margin_tower_int = x_int - 14.60
    margin_tower_ext = x_ext - 14.60
    print(f"Y = {y:5.2f} mm                   | 14.60  | {y:5.2f}  | {x_int:6.2f} mm   | {margin_tower_int:6.2f} mm (to ext: {margin_tower_ext:6.2f} mm)")
