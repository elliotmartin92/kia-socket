import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from shapely.geometry import Point, box
import build_part as bp
import build_clamp as bc

base_poly, outer_body_poly, _ = bp.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-bp.OUTER_WALL_THICK)
inner_cavity_poly = outer_body_poly.buffer(-(bp.OUTER_WALL_THICK + 0.25))

# Check where the Right Tower rear prong is: X in [13.10, 14.60], Y = 12.180
# A rear clamping jaw needs to sit behind Y = 12.360 (e.g., Y in [12.36, 13.55]) at X in [13.10, 14.60]!
print("=== RIGHT TOWER REAR JAW GEOMETRY CHECK ===")
for x_test in [13.10, 13.50, 14.00, 14.60]:
    # Find max Y inside outer_body_poly, inner_wall_poly, and inner_cavity_poly at this X
    from shapely.geometry import LineString
    line = LineString([(x_test, 8.0), (x_test, 18.0)])
    y_outer = outer_body_poly.intersection(line).bounds[3]
    y_inner_wall = inner_wall_poly.intersection(line).bounds[3]
    y_inner_cav = inner_cavity_poly.intersection(line).bounds[3]
    print(f"At X = {x_test:5.2f}mm (Right Tower is 13.10..14.60, Rear Prong edge is Y=12.18):")
    print(f"  Outer Perimeter Y_max         = {y_outer:.3f} mm (jaw thickness available = {y_outer - 12.36:.3f} mm)")
    print(f"  Inner Rim Wall (Z<=6.77) Y_max = {y_inner_wall:.3f} mm (jaw thickness available = {y_inner_wall - 12.36:.3f} mm)")
    print(f"  Inner Cavity (-0.25mm) Y_max   = {y_inner_cav:.3f} mm (jaw thickness available = {y_inner_cav - 12.36:.3f} mm)")
