import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER, CAM_WIDTH_X, CAM_X_CENTER, X_TOWER_CENTER, HUB_WIDTH
from build_part import BRACKET_SEATING_RIB_HEIGHT, BASE_THICK

# Current Cam:
poly_pts_cam_current = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0 + 0.5), # (9.28, 15.19)
    (5.00, 9.80),
    (1.50, 7.20),
    (1.80, 5.00),
    (4.50, 5.20),
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
]

# Lowered Cam (shifted down in Z by 1.0mm in the throat/belly region):
# We maintain the same reach into the throat (Y=1.50mm), same X span,
# but lower the top ramp and nose so it sits lower in the throat!
DELTA_Z = 1.00 # 1.0mm lower

poly_pts_cam_lowered = [
    (Y_AXLE, Z_AXLE),
    (Y_AXLE, Z_AXLE + HUB_DIAMETER/2.0),       # (9.28, 14.69) flush with hub top
    (7.00, 12.00),                             # Smooth tangent transition from hub
    (5.00, 9.80 - DELTA_Z),                    # (5.00, 8.80)
    (1.50, 7.20 - DELTA_Z),                    # (1.50, 6.20) sitting 1.0mm lower in throat
    (1.80, 5.00 - DELTA_Z),                    # (1.80, 4.00)
    (4.50, 5.20 - DELTA_Z),                    # (4.50, 4.20)
    (Y_AXLE - 1.50, Z_AXLE - 2.50)
]

print('Current cam Z range in throat (Y in [1.5, 5.0]):', [5.00, 9.80])
print('Lowered cam Z range in throat (Y in [1.5, 5.0]):', [5.00 - DELTA_Z, 9.80 - DELTA_Z])
print('Underside clearance to floor (Z=1.0mm):', 4.00 - 1.00, 'mm')
