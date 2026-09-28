import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# Test tine range
y_start = -5.80
y_end = 12.30
y_tine_stations = np.arange(y_start + 1.5, y_end - 0.8, 3.1)
print("Tine stations:", [round(y, 2) for y in y_tine_stations])
print("Max tine station:", y_tine_stations[-1], "vs y_end:", y_end)
