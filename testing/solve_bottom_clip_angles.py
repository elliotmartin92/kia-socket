import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, CLIP_ARM_WIDTH, find_boundary_point_and_normal
import numpy as np
from shapely.geometry import Point, LineString

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

# 1. Right Side Analysis
# Curve from index 4 (18.206, -4.100) to index 54 (9.812, -15.950)
r_curve = LineString(coords[4:55])
total_r_len = r_curve.length

print(f"Total Right Curve Length = {total_r_len:.3f} mm")

# If arc distance from ear = 4.42mm:
pt_r_442 = r_curve.interpolate(4.42)
# Angle of this point from origin:
ang_r_442 = np.degrees(np.arctan2(pt_r_442.y, pt_r_442.x)) % 360
print(f"\n[Right Option 1: Arc dist from ear = 4.42mm]")
print(f"  Point: ({pt_r_442.x:.3f}, {pt_r_442.y:.3f})")
print(f"  Angle: {ang_r_442:.2f}° (or {ang_r_442 - 360:.2f}°)")
print(f"  Arc to Ear: 4.420 mm, Arc to Tab: {total_r_len - 4.42:.3f} mm")

# If arc distance from tab = 8.47mm:
pt_r_847 = r_curve.interpolate(total_r_len - 8.47)
ang_r_847 = np.degrees(np.arctan2(pt_r_847.y, pt_r_847.x)) % 360
print(f"\n[Right Option 2: Arc dist from tab = 8.47mm]")
print(f"  Point: ({pt_r_847.x:.3f}, {pt_r_847.y:.3f})")
print(f"  Angle: {ang_r_847:.2f}° (or {ang_r_847 - 360:.2f}°)")
print(f"  Arc to Ear: {total_r_len - 8.47:.3f} mm, Arc to Tab: 8.470 mm")

# If ratio 4.42 / (4.42 + 8.47) is used:
ratio = 4.42 / (4.42 + 8.47)
pt_r_ratio = r_curve.interpolate(total_r_len * ratio)
ang_r_ratio = np.degrees(np.arctan2(pt_r_ratio.y, pt_r_ratio.x)) % 360
print(f"\n[Right Option 3: Proportional ratio {ratio*100:.1f}% along total curve]")
print(f"  Point: ({pt_r_ratio.x:.3f}, {pt_r_ratio.y:.3f})")
print(f"  Angle: {ang_r_ratio:.2f}° (or {ang_r_ratio - 360:.2f}°)")
print(f"  Arc to Ear: {total_r_len * ratio:.3f} mm, Arc to Tab: {total_r_len * (1 - ratio):.3f} mm")

# 2. Left Side Analysis
# Curve from index 61 (-10.686, -15.950) to index 111 (-19.081, -4.100)
# Reversing so it goes from ear (111) to tab (61):
l_curve = LineString(list(reversed(coords[61:112])))
total_l_len = l_curve.length
print(f"\nTotal Left Curve Length = {total_l_len:.3f} mm")

pt_l_442 = l_curve.interpolate(4.42)
ang_l_442 = np.degrees(np.arctan2(pt_l_442.y, pt_l_442.x)) % 360
print(f"\n[Left Option 1: Arc dist from ear = 4.42mm]")
print(f"  Point: ({pt_l_442.x:.3f}, {pt_l_442.y:.3f})")
print(f"  Angle: {ang_l_442:.2f}°")

pt_l_847 = l_curve.interpolate(total_l_len - 8.47)
ang_l_847 = np.degrees(np.arctan2(pt_l_847.y, pt_l_847.x)) % 360
print(f"\n[Left Option 2: Arc dist from tab = 8.47mm]")
print(f"  Point: ({pt_l_847.x:.3f}, {pt_l_847.y:.3f})")
print(f"  Angle: {ang_l_847:.2f}°")

pt_l_ratio = l_curve.interpolate(total_l_len * ratio)
ang_l_ratio = np.degrees(np.arctan2(pt_l_ratio.y, pt_l_ratio.x)) % 360
print(f"\n[Left Option 3: Proportional ratio {ratio*100:.1f}% along total curve]")
print(f"  Point: ({pt_l_ratio.x:.3f}, {pt_l_ratio.y:.3f})")
print(f"  Angle: {ang_l_ratio:.2f}°")
