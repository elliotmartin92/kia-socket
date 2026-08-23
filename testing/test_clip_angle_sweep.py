import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, CLIP_ARM_WIDTH, find_boundary_point_and_normal
import numpy as np
from shapely.geometry import Point, LineString

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

# Right Ear bottom corner:
ear_r_bottom = np.array([18.206, -4.100])
ear_r_tip = np.array([20.200, -4.100])
tab_r_top = np.array([9.812, -15.950])

# Left Ear bottom corner:
ear_l_bottom = np.array([-19.081, -4.100])
ear_l_tip = np.array([-21.075, -4.100])
tab_l_top = np.array([-10.686, -15.950])

print("--- Right Side Angle Sweep (angles 300 to 350 deg) ---")
print(f"{'Angle':>7s} | {'Clip Center (X,Y)':>18s} | {'Arc to Ear':>10s} | {'Arc to Tab':>10s} | {'Eucl(Ear-Ctr)':>13s} | {'Eucl(Tab-Ctr)':>13s} | {'Eucl(EarEdge)':>13s} | {'Eucl(TabEdge)':>13s}")
print("-" * 115)

r_curve = LineString(coords[4:55])

for ang in np.arange(315.0, 345.0, 1.0):
    pt_boundary, n, t = find_boundary_point_and_normal(outer_poly, ang)
    pt_shapely = Point(pt_boundary)
    
    # Distance along curve from ear (coords[4]) to pt_boundary:
    dist_along_r = r_curve.project(pt_shapely)
    dist_to_tab_r = r_curve.length - dist_along_r
    
    eucl_ear_ctr = np.linalg.norm(pt_boundary - ear_r_bottom)
    eucl_tab_ctr = np.linalg.norm(pt_boundary - tab_r_top)
    
    # Also calculate distance from ear to clip NEAR edge (offset by CLIP_ARM_WIDTH/2 = 2.1mm)
    pt_near_ear = pt_boundary - t * (CLIP_ARM_WIDTH / 2.0)
    pt_near_tab = pt_boundary + t * (CLIP_ARM_WIDTH / 2.0)
    
    eucl_ear_edge = np.linalg.norm(pt_near_ear - ear_r_bottom)
    eucl_tab_edge = np.linalg.norm(pt_near_tab - tab_r_top)
    
    print(f"{ang:7.1f} | ({pt_boundary[0]:5.2f}, {pt_boundary[1]:5.2f}) | {dist_along_r:10.3f} | {dist_to_tab_r:10.3f} | {eucl_ear_ctr:13.3f} | {eucl_tab_ctr:13.3f} | {eucl_ear_edge:13.3f} | {eucl_tab_edge:13.3f}")

