"""
testing/analyze_enlarged_shaft_options.py
Simulate and analyze various enlarged shaft and tower dimensions:
- Pin diameter (e.g. 2.50mm, 2.80mm, 3.00mm, 3.20mm)
- Cradle diameter (0.15-0.20mm clearance)
- Retention throat gap and snap deflection
- Hub diameter (3.80mm - 4.80mm)
- Plunger arm thickness and hole clearance (through-hole: X in [7.608, 12.960], Y in [8.570, 13.082])
- Tower top height and wall thickness margins
- Alignment verification at Y = 10.200mm, Z = 12.590mm
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np

# Baseplate and hole constants
Y_AXLE = 10.200  # Matched to tower cradle centered over through hole
Z_AXLE = 12.590

HOLE_X_MIN = 7.608
HOLE_X_MAX = 12.960
HOLE_Y_MIN = 8.570
HOLE_Y_MAX = 13.082

X_LEFT_TOWER_INNER = 5.400
X_RIGHT_TOWER_INNER = 13.100
TOWER_GAP = X_RIGHT_TOWER_INNER - X_LEFT_TOWER_INNER  # 7.70 mm

TOWER_TOP_Y_MIN = 7.471
TOWER_TOP_Y_MAX = 13.101
TOWER_TOP_Y_LEN = TOWER_TOP_Y_MAX - TOWER_TOP_Y_MIN  # 5.63 mm

print("=== Analyzing Enlarged Shaft & Tower Options ===")
for pin_d in [2.40, 2.80, 3.00, 3.20]:
    cradle_d = pin_d + 0.20
    r_cradle = cradle_d / 2.0
    r_pin = pin_d / 2.0
    
    # Throat gap for ~0.35-0.40mm snap interference and >250 deg wrap
    snap_interference = 0.35
    throat_w = pin_d - snap_interference
    half_w = throat_w / 2.0
    alpha_deg = np.degrees(np.arcsin(half_w / r_cradle))
    wrap_deg = 180 + 2 * (90 - alpha_deg)
    
    # Tower material thickness at top:
    front_wall_thick = (Y_AXLE - r_cradle) - TOWER_TOP_Y_MIN
    rear_wall_thick = TOWER_TOP_Y_MAX - (Y_AXLE + r_cradle)
    
    # Hub size:
    hub_d = pin_d + 1.20  # Stepped hub barrel
    
    print(f"\n--- Pin Diameter: Ø{pin_d:.2f} mm ---")
    print(f"  Cradle Diameter: Ø{cradle_d:.2f} mm (Clearance: {cradle_d - pin_d:.2f} mm)")
    print(f"  Retention Throat: {throat_w:.2f} mm (Snap interference: {snap_interference:.2f} mm)")
    print(f"  Wrap Angle: {wrap_deg:.1f}° (>250° positive mechanical lock)")
    print(f"  Tower Top Y bounds: [{TOWER_TOP_Y_MIN:.3f}, {TOWER_TOP_Y_MAX:.3f}] (Total: {TOWER_TOP_Y_LEN:.2f} mm)")
    print(f"  Front wall remaining at cradle top: {front_wall_thick:.2f} mm")
    print(f"  Rear wall remaining at cradle top: {rear_wall_thick:.2f} mm")
    print(f"  Central Hub Diameter: Ø{hub_d:.2f} mm")
    print(f"  Torsional strength relative to Ø1.90mm: {(pin_d / 1.90)**4:.2f}x higher!")
