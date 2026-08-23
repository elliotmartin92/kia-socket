import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np

KEY_W = 1.85
KEY_L = 4.15

for clearance in [0.15, 0.20, 0.25, 0.28, 0.30, 0.35]:
    sock_w = KEY_W + clearance
    sock_l = KEY_L + clearance
    gap_per_side = clearance / 2.0
    print(f"Clearance = {clearance:.2f}mm -> Socket: {sock_w:.2f}mm x {sock_l:.2f}mm (Per side: {gap_per_side:.3f}mm / {gap_per_side*1000:.0f} um)")
