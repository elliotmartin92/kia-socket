"""
testing/test_105_bellcrank_direct.py
Test the 105 degree bellcrank angle where input arm extends directly off the shaft cylinder.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import matplotlib.pyplot as plt

Y_AXLE = 10.200
Z_AXLE = 12.590
HUB_D = 4.20
R_HUB = HUB_D / 2.0

# Plunger (output arm)
v_p = np.array([11.40 - Y_AXLE, -6.50 - Z_AXLE]) # [1.20, -19.09]
theta_p = np.degrees(np.arctan2(v_p[1], v_p[0])) # -86.40 deg

# 105 degree bellcrank:
# If bellcrank angle is 105° between the forward face / arm and the downward plunger:
# theta_cam = theta_p - (180 - 105) = -86.40 - 75.0 = -161.40 deg
# Or if angle between centerlines = 105 deg obtuse:
theta_cam_75 = theta_p - 75.0 # -161.40 deg

# Construct arm coming DIRECTLY off the shaft cylinder:
# We create a solid rectangular beam with width/thickness = 2.80mm that merges tangentially into the shaft hub
arm_len = 6.80
arm_thick = 2.80
half_t = arm_thick / 2.0

rad_75 = np.radians(theta_cam_75)
dir_cam = np.array([np.cos(rad_75), np.sin(rad_75)])
norm_cam = np.array([-dir_cam[1], dir_cam[0]])

p_tip = np.array([Y_AXLE, Z_AXLE]) + dir_cam * arm_len

# 4 corners of arm merging directly into the shaft center
p1 = np.array([Y_AXLE, Z_AXLE]) + norm_cam * half_t
p2 = p_tip + norm_cam * half_t
p3 = p_tip - norm_cam * half_t
p4 = np.array([Y_AXLE, Z_AXLE]) - norm_cam * half_t

# Tip rounded contact face
tip_pts = []
for a in np.linspace(np.pi/2, -np.pi/2, 17):
    pt = p_tip + dir_cam * (half_t * np.cos(a)) + norm_cam * (half_t * np.sin(a))
    tip_pts.append((pt[0], pt[1]))

poly_arm = Polygon([p1] + tip_pts + [p4, p1])
poly_hub = Point(Y_AXLE, Z_AXLE).buffer(R_HUB)
poly_cam = unary_union([poly_hub, poly_arm])

print(f"Cam tip center: ({p_tip[0]:.3f}, {p_tip[1]:.3f})")
print(f"Angle from horizontal (-Y): {abs(-180 - theta_cam_75):.2f}°")
print(f"Angle from vertical (-Z): {abs(-90 - theta_cam_75):.2f}°")
print(f"Angle between plunger and cam centerlines: {abs(theta_cam_75 - theta_p):.2f}° (Supplementary bellcrank angle: {180 - abs(theta_cam_75 - theta_p):.2f}°)")
