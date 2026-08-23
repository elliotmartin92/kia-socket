import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, CLIP_ARM_WIDTH, find_boundary_point_and_normal
import numpy as np
from shapely.geometry import Point, LineString

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

# Right curve from index 4 to 54
r_curve = LineString(coords[4:55])
# Left curve from index 111 to 61 (from ear to tab)
l_curve = LineString(list(reversed(coords[61:112])))

ear_r = coords[4]
tab_r = coords[54]
ear_l = coords[111]
tab_l = coords[61]

def evaluate_clip_angles(ang_r, ang_l):
    # Right
    p_r, _, t_r = find_boundary_point_and_normal(outer_poly, ang_r)
    dist_r_ctr = r_curve.project(Point(p_r))
    dist_r_tab_ctr = r_curve.length - dist_r_ctr
    
    # Near edge to ear (dist along arc minus half arm width)
    dist_r_ear_edge = max(0, dist_r_ctr - CLIP_ARM_WIDTH/2.0)
    dist_r_tab_edge = max(0, dist_r_tab_ctr - CLIP_ARM_WIDTH/2.0)
    
    # Left
    p_l, _, t_l = find_boundary_point_and_normal(outer_poly, ang_l)
    dist_l_ctr = l_curve.project(Point(p_l))
    dist_l_tab_ctr = l_curve.length - dist_l_ctr
    dist_l_ear_edge = max(0, dist_l_ctr - CLIP_ARM_WIDTH/2.0)
    dist_l_tab_edge = max(0, dist_l_tab_ctr - CLIP_ARM_WIDTH/2.0)
    
    print(f"\n--- Testing Angles: Right={ang_r:.1f}°, Left={ang_l:.1f}° ---")
    print(f"Right: Arc to Ear Ctr={dist_r_ctr:.2f}mm, Near Edge={dist_r_ear_edge:.2f}mm | Arc to Tab Ctr={dist_r_tab_ctr:.2f}mm, Far Edge={dist_r_tab_edge:.2f}mm")
    print(f"Left:  Arc to Ear Ctr={dist_l_ctr:.2f}mm, Near Edge={dist_l_ear_edge:.2f}mm | Arc to Tab Ctr={dist_l_tab_ctr:.2f}mm, Far Edge={dist_l_tab_edge:.2f}mm")

# 1. Option 1: Edge-to-edge spacing: 4.42mm gap from ear, 8.47mm gap to tab -> Right ~327.5°, Left ~211.0°
evaluate_clip_angles(327.5, 211.0)

# 2. Option 2: Center-to-Ear 4.42mm -> Right ~334.0°, Left ~205.0°
evaluate_clip_angles(334.0, 205.0)

# 3. Option 3: Proportional ratio (34.3% along span) -> Right ~331.5°, Left ~207.0°
evaluate_clip_angles(331.5, 207.0)

# 4. Old Centered -> Right 325.5°, Left 214.5°
evaluate_clip_angles(325.5, 214.5)
