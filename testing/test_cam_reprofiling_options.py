import os, sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER

# Pivot: (Y_AXLE, Z_AXLE) = (9.279, 12.590)
# Brass contact rear boundary: Y = 3.85 mm
# Blade rear boundary: Y = 5.68 mm
# Blade center: Y = 2.50 mm

# Let's inspect a rear-blade cam profile:
# Starts at Hub (Y = 9.279, Z = 14.69 down to 10.49)
# Slopes downward-forward to Y = 3.90 mm (clearing Y = 3.85 mm with 0.05 - 0.20 mm margin)
# At Y = 3.90 mm, Z = 6.50 mm (reaches well below the top of the blade)
# Ramp runs from (Y=6.00, Z=11.50) to (Y=3.90, Z=6.50)
# Blade enters from Z=16 down to Z=3.0 mm.
# Blade overlaps the ramp from Y = 3.90 to Y = 5.68 mm (1.78 mm engagement span in Y!)

print('Ramp length in Y:', 5.68 - 3.90, 'mm')
dz_blade_stroke = 11.50 - 6.50
print('Available cam vertical stroke:', dz_blade_stroke, 'mm')
