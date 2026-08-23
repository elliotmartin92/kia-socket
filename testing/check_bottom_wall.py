"""
Check exact Y coordinates of the bottommost wall at the slit X positions.
"""
from shapely.geometry import Polygon, LineString, Point
from build_part import outer_pts, get_exact_bottom_arch_poly, OUTER_WALL_THICK

poly = Polygon(outer_pts).difference(get_exact_bottom_arch_poly())
inner_poly = poly.buffer(-OUTER_WALL_THICK)

# Let's inspect the bottom edge at X = -8.4 and +8.4 (center of slits)
for x in [-8.4, -7.853, -8.953, 7.853, 8.4, 8.953]:
    # Vertical ray going down
    ray = LineString([(x, 0), (x, -25)])
    
    inter_outer = poly.exterior.intersection(ray)
    inter_inner = inner_poly.exterior.intersection(ray) if hasattr(inner_poly, 'exterior') else None
    
    y_outer = inter_outer.y if hasattr(inter_outer, 'y') else [p.y for p in inter_outer.geoms][-1]
    
    print(f"At X = {x:+.3f} mm:")
    print(f"  Outer Bottom Wall Y: {y_outer:.3f} mm")
    if inter_inner:
        y_inner = inter_inner.y if hasattr(inter_inner, 'y') else ([p.y for p in inter_inner.geoms][-1] if hasattr(inter_inner, 'geoms') else 'N/A')
        print(f"  Inner Bottom Wall Y: {y_inner:.3f} mm")
