"""
testing/inspect_slider_engagement.py
Inspect slider channel Y bounds, bracket landmarks, and cam engagement reach.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, to_mm_poly
)

b3 = to_mm_poly(bracket_3_raw_pts)
print(f"Bracket 3 bounds in (X, Y):")
print(f"  X: [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}] (width = {b3.bounds[2]-b3.bounds[0]:.3f} mm)")
print(f"  Y: [{b3.bounds[1]:.3f}, {b3.bounds[3]:.3f}] (length = {b3.bounds[3]-b3.bounds[1]:.3f} mm)")
print(f"Bracket 3 top edge is at Y = {b3.bounds[3]:.3f} mm")

# In the enclosure, the slider bar slides along +Y in the Bracket 3 / 4 channel (X in [1.77, 10.79])
# When the physical key blade is inserted into the socket:
# It pushes the slider in +Y towards the shaft towers.
# The slider's rear push bar meets the input cam tab of the shaft rocker!
# Pivot axis is at Y = 10.200 mm, Z = 12.590 mm.
# If cam tip reaches Y = 3.47 mm (which is inside the bracket channel, 3.70mm below top edge Y=7.171mm):
# Relative reach in -Y from axle: Delta_Y = 10.200 - 3.470 = 6.73 mm!
# If Delta_Y = 4.50 mm (as currently on main): Cam tip is at Y = 5.70 mm.
# If Delta_Y = 6.73 mm (reaching Y = 3.47 mm): The angle between plunger and cam is much wider!

v_plunger = np.array([11.40 - 10.200, -6.50 - 12.590]) # [1.20, -19.09]

for delta_y, delta_z in [(4.50, 5.80), (5.50, 5.80), (6.73, 5.80), (7.00, 6.00)]:
    y_tip = 10.200 - delta_y
    z_tip = 12.590 - delta_z
    v_cam = np.array([-delta_y, -delta_z])
    angle = np.degrees(np.arccos(np.dot(v_cam, v_plunger) / (np.linalg.norm(v_cam) * np.linalg.norm(v_plunger))))
    print(f"\nDelta_Y = {delta_y:.2f}mm -> Cam Tip at (Y = {y_tip:.2f}mm, Z = {z_tip:.2f}mm):")
    print(f"  Angle between Plunger and Cam = {angle:.1f}°")
    print(f"  Reach into Bracket 3 channel (below Y=7.17mm): {7.171 - y_tip:.2f} mm")
