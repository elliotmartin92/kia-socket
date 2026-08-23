import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, CLIP_ARM_WIDTH, find_boundary_point_and_normal
import numpy as np
from shapely.geometry import Point, LineString

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

r_curve = LineString(coords[4:55])
l_curve = LineString(list(reversed(coords[61:112])))

# Target: Near Edge to Ear = 4.42mm
target_ear_gap = 4.42
target_ctr_r = target_ear_gap + CLIP_ARM_WIDTH / 2.0 # 4.42 + 2.10 = 6.52mm
target_ctr_l = target_ear_gap + CLIP_ARM_WIDTH / 2.0 # 6.52mm

pt_r = r_curve.interpolate(target_ctr_r)
ang_r = np.degrees(np.arctan2(pt_r.y, pt_r.x)) % 360

pt_l = l_curve.interpolate(target_ctr_l)
ang_l = np.degrees(np.arctan2(pt_l.y, pt_l.x)) % 360

print(f"Exact Right Angle for 4.42mm ear gap: {ang_r:.2f}° (round to {round(ang_r, 1)}°)")
print(f"Exact Left Angle for 4.42mm ear gap: {ang_l:.2f}° (round to {round(ang_l, 1)}°)")

# Verify distances with rounded angles:
r_ang_final = 327.5
l_ang_final = 211.0

p_r, _, _ = find_boundary_point_and_normal(outer_poly, r_ang_final)
d_r_ctr = r_curve.project(Point(p_r))
d_r_near = d_r_ctr - CLIP_ARM_WIDTH / 2.0
d_r_tab = r_curve.length - d_r_ctr

p_l, _, _ = find_boundary_point_and_normal(outer_poly, l_ang_final)
d_l_ctr = l_curve.project(Point(p_l))
d_l_near = d_l_ctr - CLIP_ARM_WIDTH / 2.0
d_l_tab = l_curve.length - d_l_ctr

print(f"\nFinal Verification at Right = {r_ang_final}°, Left = {l_ang_final}°:")
print(f"Right: Ear gap = {d_r_near:.3f} mm (target: 4.42mm), Tab distance = {d_r_tab:.3f} mm (target: ~8.47mm)")
print(f"Left:  Ear gap = {d_l_near:.3f} mm (target: 4.42mm), Tab distance = {d_l_tab:.3f} mm (target: ~8.47mm)")
