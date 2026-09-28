"""
testing/test_cam_options_for_10_5mm_blade.py
Tests different cam profile optimizations to guarantee full lever actuation
when blade penetrates 10.5mm (Z_tip in [7.0, 7.5] mm).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER

r_hub = HUB_DIAMETER / 2.0
dy_p = 10.479 - Y_AXLE
dz_p = -6.50 - Z_AXLE
Y_SWITCH_THRESHOLD = 12.40

# Blade bounds: 6.35mm wide blade centered at Y = 0.30mm (span [-2.875, 3.475])
# and Y = 1.00mm (span [-2.175, 4.175])
y_b_min = 0.30 - 3.175
y_b_max = 0.30 + 3.175

# Profile 1: Current lowered cam (DZ_CAM = 0.90)
p1 = np.array([
    (Y_AXLE, Z_AXLE), (Y_AXLE, Z_AXLE + r_hub), (6.80, 11.50),
    (5.00, 8.90), (1.50, 6.30), (1.80, 4.10), (4.50, 4.30),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
])

# Profile 2: Restored original height (DZ_CAM = 0.00)
p2 = np.array([
    (Y_AXLE, Z_AXLE), (Y_AXLE, Z_AXLE + r_hub), (6.80, 12.20),
    (5.00, 9.80), (1.50, 7.20), (1.80, 5.00), (4.50, 5.20),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
])

# Profile 3: Crowned / Raised Ramp (+0.50mm higher contact ramp in the blade engagement zone)
# Top ramp from (5.00, 10.20) down to (1.50, 7.50)
p3 = np.array([
    (Y_AXLE, Z_AXLE), (Y_AXLE, Z_AXLE + r_hub), (6.80, 12.40),
    (5.00, 10.20), (1.50, 7.50), (1.80, 5.20), (4.50, 5.40),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
])

# Profile 4: Extended High-Sensitivity Cam (starts engagement at Z=10.50, tip at (1.20, 7.60))
p4 = np.array([
    (Y_AXLE, Z_AXLE), (Y_AXLE, Z_AXLE + r_hub), (6.80, 12.50),
    (4.80, 10.50), (1.20, 7.60), (1.60, 5.20), (4.50, 5.40),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
])

options = [
    ("Option 1: Current Lowered (DZ=0.90)", p1),
    ("Option 2: Restored Original (DZ=0.00)", p2),
    ("Option 3: Crowned/Raised Ramp", p3),
    ("Option 4: Extended High-Sensitivity", p4)
]

def eval_cam(cam_pts, z_tip):
    # Sample top profile
    p_seq = [cam_pts[4], cam_pts[3], cam_pts[2], cam_pts[1]]
    prof_pts = []
    for i in range(len(p_seq)-1):
        for f in np.linspace(0, 1, 30):
            prof_pts.append(p_seq[i] + f * (p_seq[i+1] - p_seq[i]))
    prof_pts = np.array(prof_pts)
    
    for th in np.linspace(0, 15, 1500):
        rad = np.radians(th)
        c, s = np.cos(rad), np.sin(rad)
        dy = prof_pts[:, 0] - Y_AXLE
        dz = prof_pts[:, 1] - Z_AXLE
        yr = Y_AXLE + c * dy - s * dz
        zr = Z_AXLE + s * dy + c * dz
        
        in_blade = (yr >= y_b_min) & (yr <= y_b_max)
        if not np.any(in_blade): continue
        if np.max(zr[in_blade]) <= z_tip:
            yp = Y_AXLE + c * dy_p - s * dz_p
            return th, yp
    return 15.0, 999.0

print("=" * 80)
print(f"KINEMATIC COMPARISON FOR BLADE CENTERED AT Y = 0.30 mm")
print(f"Switch Trips at Y_plunger >= {Y_SWITCH_THRESHOLD:.2f} mm (requires theta >= 5.79°)")
print("=" * 80)

for name, pts in options:
    print(f"\n{name}:")
    print(f"  Ramp bounds: Y in [{pts[4,0]:.2f}, {pts[3,0]:.2f}], Z in [{pts[4,1]:.2f}, {pts[3,1]:.2f}]")
    for zt in [7.50, 7.20, 7.00, 6.70]:
        th, yp = eval_cam(pts, zt)
        status = ">> FULL TRIP <<" if yp >= Y_SWITCH_THRESHOLD else f"NO TRIP (short by {Y_SWITCH_THRESHOLD - yp:.2f}mm)"
        print(f"    Z_tip = {zt:.2f} mm -> theta = {th:5.2f}°, Y_plunger = {yp:5.2f} mm -> {status}")
