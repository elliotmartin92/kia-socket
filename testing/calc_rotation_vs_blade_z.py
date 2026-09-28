"""
testing/calc_rotation_vs_blade_z.py
Calculates exact rocker rotation angle theta achieved for each blade tip Z elevation.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER

r_hub = HUB_DIAMETER / 2.0
DZ_CAM = 0.90

# Current cam points
poly_pts_current = np.array([
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + r_hub),
    (6.80, 11.50),
    (5.00, 8.90),
    (1.50, 6.30),
    (1.80, 4.10),
    (4.50, 4.30),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
])

# Previous cam points (DZ_CAM = 0)
poly_pts_prev = np.array([
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + r_hub + 0.5),
    (5.00, 9.80),
    (1.50, 7.20),
    (1.80, 5.00),
    (4.50, 5.20),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
])

# Blade position in Y:
# Blade is 6.35mm wide.
# Let's test blade centered at Y = 0.30mm (span [-2.88, 3.47])
# and blade centered at Y = 1.00mm (span [-2.18, 4.18])
# and blade centered at Y = 2.00mm (span [-1.18, 5.18])

def get_rotation_for_z_tip(cam_pts, z_tip, y_blade_min, y_blade_max):
    thetas = np.linspace(0, 15, 1500)
    # The active ramp segment is between pts[3] and pts[4] in current, or pts[2] and pts[3] in prev
    # Sample 50 points along the top profile of the cam from throat tip to hub
    # For current: from (1.50, 6.30) -> (5.00, 8.90) -> (6.80, 11.50) -> (Y_axle, Z_axle + r_hub)
    # Let's create high-res profile
    prof_pts = []
    if len(cam_pts) == 8: # current
        p_seq = [cam_pts[4], cam_pts[3], cam_pts[2], cam_pts[1]]
    else: # prev
        p_seq = [cam_pts[3], cam_pts[2], cam_pts[1]]
    
    for i in range(len(p_seq)-1):
        p1 = p_seq[i]
        p2 = p_seq[i+1]
        for frac in np.linspace(0, 1, 30):
            prof_pts.append(p1 + frac * (p2 - p1))
    prof_pts = np.array(prof_pts)
    
    # Rotate prof_pts for each theta and find the minimum theta such that
    # the entire profile inside [y_blade_min, y_blade_max] is at or below z_tip
    for th in thetas:
        rad = np.radians(th)
        c, s = np.cos(rad), np.sin(rad)
        dy = prof_pts[:, 0] - Y_AXLE
        dz = prof_pts[:, 1] - Z_AXLE
        yr = Y_AXLE + c * dy - s * dz
        zr = Z_AXLE + s * dy + c * dz
        
        in_blade = (yr >= y_blade_min) & (yr <= y_blade_max)
        if not np.any(in_blade):
            continue
        max_z_in_blade = np.max(zr[in_blade])
        if max_z_in_blade <= z_tip:
            return th
    return 15.0

print(f"{'Z_tip (mm)':10s} | {'Current Cam (Y_c=0.30)':22s} | {'Current Cam (Y_c=1.00)':22s} | {'Prev Cam (Y_c=0.30)':20s} | {'Prev Cam (Y_c=1.00)':20s}")
print("-" * 105)

dy_p = 10.479 - Y_AXLE
dz_p = -6.50 - Z_AXLE

for z_tip in [9.5, 9.0, 8.5, 8.0, 7.5, 7.2, 7.0, 6.7, 6.5, 6.3, 6.0, 5.5, 5.0]:
    th_c03 = get_rotation_for_z_tip(poly_pts_current, z_tip, 0.30 - 3.175, 0.30 + 3.175)
    th_c10 = get_rotation_for_z_tip(poly_pts_current, z_tip, 1.00 - 3.175, 1.00 + 3.175)
    th_p03 = get_rotation_for_z_tip(poly_pts_prev, z_tip, 0.30 - 3.175, 0.30 + 3.175)
    th_p10 = get_rotation_for_z_tip(poly_pts_prev, z_tip, 1.00 - 3.175, 1.00 + 3.175)
    
    # Plunger Y for current at Y_c=0.30:
    rad = np.radians(th_c03)
    yp = Y_AXLE + np.cos(rad)*dy_p - np.sin(rad)*dz_p
    trip_str = "TRIPPED" if yp >= 12.40 else f"yp={yp:.2f}"
    
    print(f"{z_tip:10.2f} | {th_c03:5.2f}° ({trip_str:13s}) | {th_c10:5.2f}°                 | {th_p03:5.2f}°               | {th_p10:5.2f}°")
