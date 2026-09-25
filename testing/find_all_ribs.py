"""
testing/find_all_ribs.py
Finds all ribs across the entire part.svg and build_part.py.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import xml.etree.ElementTree as ET

import build_part as bp

print("=== CHECKING ALL RIBS IN BUILD_PART.PY ===")
print("BRACKET_SEATING_RIB_Y:", bp.BRACKET_SEATING_RIB_Y)
print("BRACKET_SEATING_RIB_HEIGHT:", bp.BRACKET_SEATING_RIB_HEIGHT)
print("BRACKET_SEATING_RIB_THICK:", bp.BRACKET_SEATING_RIB_THICK)
print("BRACKET_SEATING_RIB_EXT:", bp.BRACKET_SEATING_RIB_EXT)

print("\n=== CHECKING FLOOR GRID RIBS ===")
print("RIB_GRID_X:", bp.RIB_GRID_X)
print("RIB_GRID_Y:", bp.RIB_GRID_Y)
print("RIB_THICK:", bp.RIB_THICK)
print("RIB_HEIGHT:", bp.RIB_HEIGHT)

# Let's inspect where grid ribs are near the brackets:
# Grid ribs Y steps: np.arange(-20, 20, 3.20)
y_grid_steps = np.concatenate([
    np.arange(0, 25, bp.RIB_GRID_Y),
    np.arange(-bp.RIB_GRID_Y, -25, -bp.RIB_GRID_Y)
])
print("Grid rib Y stations:", sorted(y_grid_steps))

# But grid ribs are excluded inside bracket_exclusions:
# right_pair_bbox = box(min(b3) - 0.1, min(b3) - 0.1, max(b4) + 0.1, max(b4) + 0.1)
# which covers X in [1.66, 10.89], Y in [-7.27, 7.27]!
# So inside the brackets, the ONLY ribs that exist are the 4 seating ribs!
