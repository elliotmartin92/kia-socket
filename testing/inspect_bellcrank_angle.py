"""
testing/inspect_bellcrank_angle.py
Inspect and analyze the angle between input cam tab and output plunger arm (bellcrank angle)
across different branch versions and parameter settings.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np

# Let's inspect the angle calculation:
# Pivot axis: (Y_AXLE, Z_AXLE)

# 1. On main currently:
# Y_AXLE = 10.200, Z_AXLE = 12.590
# Plunger tip at rest: Y = 11.400, Z = -6.500
# Vector to plunger tip: v_plunger = (11.400 - 10.200, -6.500 - 12.590) = (1.200, -19.090)
# Angle of plunger vector from +Y axis:
# v_plunger angle = arctan2(-19.090, 1.200) = -86.4 deg (almost pointing straight down in -Z, slightly in +Y)

# Input Cam tip:
# y_cam_tip = Y_AXLE - 4.50 = 5.700, z_cam_tip = Z_AXLE - 5.80 = 6.790
# Vector to cam tip: v_cam = (5.700 - 10.200, 6.790 - 12.590) = (-4.500, -5.800)
# Angle of cam vector from +Y axis:
# v_cam angle = arctan2(-5.800, -4.500) = -127.8 deg

# Bellcrank angle between v_plunger and v_cam:
# angle_diff = |-127.8 - (-86.4)| = 41.4 deg ?? Or between the arm centerlines?

# Let's check the arm centerline vectors:
# Input cam contact face:
# Top face of cam extends towards (Y_AXLE - 4.50, Z_AXLE - 3.40) -> v_cam_top = (-4.50, -3.40) = angle -142.9 deg (pointing down and forward in -Y)
# Plunger body centerline: goes towards (Y=11.40, Z=-6.50) -> angle -86.4 deg

print("=== Bellcrank Geometry Analysis ===")
Y_AXLE = 10.200
Z_AXLE = 12.590

# Plunger vector
v_p = np.array([11.40 - Y_AXLE, -6.50 - Z_AXLE])
len_p = np.linalg.norm(v_p)
ang_p = np.degrees(np.arctan2(v_p[1], v_p[0]))

# Cam vectors:
# Cam tip
v_c_tip = np.array([-4.50, -5.80])
len_c_tip = np.linalg.norm(v_c_tip)
ang_c_tip = np.degrees(np.arctan2(v_c_tip[1], v_c_tip[0]))

# Cam arm main axis (midpoint of cam profile)
# cam_pts = [(Y_AXLE + 1.5, Z_AXLE + 1.5), (Y_AXLE - 4.5, Z_AXLE - 3.4), (Y_AXLE - 4.5, Z_AXLE - 5.8), (Y_AXLE - 1.5, Z_AXLE - 5.8), (Y_AXLE + 0.2, Z_AXLE - 2.8)]
cam_center_tip = np.array([-4.50, -4.60])
ang_c_center = np.degrees(np.arctan2(cam_center_tip[1], cam_center_tip[0]))

print(f"Pivot Axis: (Y={Y_AXLE:.3f}, Z={Z_AXLE:.3f})")
print(f"Plunger Tip: Vector={v_p}, Length={len_p:.2f}mm, Angle={ang_p:.1f}°")
print(f"Cam Tip: Vector={v_c_tip}, Length={len_c_tip:.2f}mm, Angle={ang_c_tip:.1f}°")
print(f"Cam Centerline: Vector={cam_center_tip}, Angle={ang_c_center:.1f}°")

# Angle between Plunger and Cam Centerline:
# In 2D plane (Y, Z):
# Plunger is at -86.4° (pointing mostly -Z, slightly +Y)
# Cam is at -134.4° (pointing -Y and -Z)
# Angle between them is:
acute_angle = abs(ang_c_center - ang_p)
obtuse_angle = 180 - acute_angle
print(f"Enclosed angle between Cam & Plunger = {acute_angle:.1f}°")
print(f"Opposite/Outer angle = {360 - acute_angle:.1f}°")
