import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trimesh
import numpy as np
import shapely.geometry as sg
from shapely.geometry import box
import matplotlib.pyplot as plt

# Test geometry values
y_shaft_new = 9.340
y_base_min_new = 6.311
y_base_max_new = 12.911
y_top_min_new = 6.611
y_top_max_new = 12.241

print(f"Testing Tower Repositioning:")
print(f"  y_shaft: {y_shaft_new:.3f}")
print(f"  y_base: [{y_base_min_new:.3f}, {y_base_max_new:.3f}]")
print(f"  y_top: [{y_top_min_new:.3f}, {y_top_max_new:.3f}]")
