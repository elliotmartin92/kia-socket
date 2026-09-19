import os, sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER, PLUNGER_REACH_BELOW_Z

# Fulcrum: (Y_AXLE, Z_AXLE) = (9.279, 12.590)
# Plunger tip at rest: (10.479, -6.50)
# Vector from fulcrum to plunger tip:
r_p = np.array([10.479 - Y_AXLE, -6.50 - Z_AXLE]) # [1.20, -19.09]
len_p = np.linalg.norm(r_p) # ~19.13 mm

# Cam contact point at rest:
# If cam contact is at Y = 4.20 mm, Z = 8.50 mm:
r_cam = np.array([4.20 - Y_AXLE, 8.50 - Z_AXLE]) # [-5.079, -4.090]
len_cam = np.linalg.norm(r_cam) # ~6.52 mm

print(f'Lever arm ratio: Plunger {len_p:.2f} mm / Cam {len_cam:.2f} mm = {len_p / len_cam:.2f}x magnification!')

# When plug blade pushes cam down by dz_cam = -3.0 mm:
# Angle of rotation theta:
# At small angles, d_theta ~ dz_cam / (Y_AXLE - Y_cam) = 3.0 / 5.079 = 0.59 rad = ~33.8 deg?
# Let's compute exact kinematic rotation:
for theta_deg in [2, 4, 6, 8, 10]:
    rad = np.radians(theta_deg)
    # Rotation about fulcrum:
    # Clockwise rotation: dY > 0, dZ > 0 for cam? No, blade pushes DOWN (-Z):
    # Fulcrum is at Y = 9.28. Cam is at Y = 4.20 (< 9.28).
    # Downward motion of cam (-Z) corresponds to COUNTER-CLOCKWISE rotation about X-axis!
    # Let's verify:
    # Vector [-5.08, -4.09]. If rotated counter-clockwise by theta:
    # Y_rot = Y_AXLE + cos(theta)*r_cam[0] - sin(theta)*r_cam[1]
    # Z_rot = Z_AXLE + sin(theta)*r_cam[0] + cos(theta)*r_cam[1]
    # For small positive theta:
    # Z_rot - (Z_AXLE + r_cam[1]) ~ sin(theta)*r_cam[0] = theta * (-5.08) < 0 (moves DOWN!)
    # Plunger: r_p = [1.20, -19.09].
    # Z_p_rot - (Z_AXLE + r_p[1]) ~ sin(theta)*r_p[0] = theta * (1.20) > 0 (moves UP!)
    z_cam_new = Z_AXLE + np.sin(rad)*r_cam[0] + np.cos(rad)*r_cam[1]
    z_p_new = Z_AXLE + np.sin(rad)*r_p[0] + np.cos(rad)*r_p[1]
    dz_cam = z_cam_new - 8.50
    dz_p = z_p_new - (-6.50)
    print(f'Theta = {theta_deg:2d} deg: Cam dz = {dz_cam:+.2f} mm | Plunger dz = {dz_p:+.2f} mm (Z_plunger = {z_p_new:.2f} mm)')
