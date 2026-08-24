"""
testing/calc_main_angles.py
Calculate exact angles used on the main branch.
"""
import numpy as np

Y_AXLE = 10.200
Z_AXLE = 12.590

# Plunger (output arm)
p_tip = np.array([11.400, -6.500])
v_p = p_tip - np.array([Y_AXLE, Z_AXLE]) # [1.20, -19.09]
theta_p = np.degrees(np.arctan2(v_p[1], v_p[0])) # -86.40 deg

# Cam (input arm) on main
c_tip_upper = np.array([5.700, 9.190]) # [Y_AXLE - 4.50, Z_AXLE - 5.80 + 2.40]
c_tip_lower = np.array([5.700, 6.790]) # [Y_AXLE - 4.50, Z_AXLE - 5.80]
c_center = (c_tip_upper + c_tip_lower) / 2.0

v_c_center = c_center - np.array([Y_AXLE, Z_AXLE]) # [-4.50, -4.60]
theta_c = np.degrees(np.arctan2(v_c_center[1], v_c_center[0])) # -134.37 deg

v_c_upper = c_tip_upper - np.array([Y_AXLE, Z_AXLE])
theta_c_upper = np.degrees(np.arctan2(v_c_upper[1], v_c_upper[0]))

print(f"Plunger centerline vector: {v_p}, angle from +Y: {theta_p:.2f}°")
print(f"Cam centerline vector: {v_c_center}, angle from +Y: {theta_c:.2f}°")
print(f"Angle between Cam and Plunger centerlines (acute): {abs(theta_c - theta_p):.2f}°")
print(f"Angle of Plunger from vertical (-Z): {abs(-90.0 - theta_p):.2f}° (tilted slightly +Y)")
print(f"Angle of Cam from horizontal (-Y): {abs(-180.0 - theta_c):.2f}° (pointing 45.6° down from horizontal)")
print(f"Angle of Cam from vertical (-Z): {abs(-90.0 - theta_c):.2f}° (pointing 44.4° forward from vertical)")
