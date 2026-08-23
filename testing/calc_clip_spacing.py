import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, CLIP_ANGLES, find_boundary_point_and_normal
import numpy as np
from shapely.geometry import LineString, Point

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

# Right side curve from index 4 (18.206, -4.100) to index 54 (9.812, -15.950)
r_curve_pts = coords[4:55]
r_line = LineString(r_curve_pts)
total_r_arc_len = r_line.length
print(f"Right perimeter curve length (Ear bottom to Tab top): {total_r_arc_len:.3f} mm")

# Left side curve from index 61 (-10.686, -15.950) to index 111 (-19.081, -4.100)
l_curve_pts = coords[61:112]
l_line = LineString(l_curve_pts)
total_l_arc_len = l_line.length
print(f"Left perimeter curve length (Tab top to Ear bottom): {total_l_arc_len:.3f} mm")

print(f"\nSum of distances given by user: 4.42mm + 8.47mm = {4.42 + 8.47:.3f} mm")
print(f"Compare with total perimeter curve: Right={total_r_arc_len:.3f}mm, Left={total_l_arc_len:.3f}mm (with 4.20mm clip width? Or 4.42 + 8.47 + 4.20 = {4.42 + 8.47 + 4.20:.3f} mm)")

# Let's check both interpretations:
# Interpretation A: Gap from ear to clip = 4.42mm, Gap from clip to tab = 8.47mm.
#   Total distance = 4.42 + clip_w (4.20) + 8.47 = 17.09mm.
# Interpretation B: Distance from ear to clip CENTER = 4.42mm, and clip center to tab = 8.47mm -> 4.42 + 8.47 = 12.89mm!
#   Notice: total curve length = 17.08mm!
#   Look: 17.085mm vs 17.090mm (4.42 + 4.20 + 8.47 = 17.09mm)!
