"""
testing/check_cradle_clearances.py
Check clearances for a unified U-frame breakaway support cradle.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

shaft_print = build_shaft_rocker_mesh(in_assembly_coords=False)

v = shaft_print.vertices
f = shaft_print.faces

# Check lowest Z of shaft_print at various Y stations in the central span (|X| <= 3.65)
print("=" * 60)
print("LOWEST Z IN CENTRAL SPAN (|X| <= 3.65mm)")
print("=" * 60)

for y_val in np.arange(-3.0, 5.0, 0.5):
    # Vertices within |X| <= 3.65 and Y in [y_val - 0.25, y_val + 0.25]
    mask = (np.abs(v[:, 0]) <= 3.65) & (np.abs(v[:, 1] - y_val) <= 0.25)
    if np.any(mask):
        z_min = np.min(v[mask, 2])
        print(f"Y = {y_val:+5.2f} mm: Lowest Z = {z_min:5.2f} mm")
    else:
        print(f"Y = {y_val:+5.2f} mm: No geometry")
