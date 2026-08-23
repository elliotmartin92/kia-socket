import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE
import trimesh
import numpy as np

part_mesh = trimesh.load('part.stl')
shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)

print("Part bounds:")
print(" X:", part_mesh.bounds[:, 0])
print(" Y:", part_mesh.bounds[:, 1])
print(" Z:", part_mesh.bounds[:, 2])

print("\nShaft bounds:")
print(" X:", shaft_mesh.bounds[:, 0])
print(" Y:", shaft_mesh.bounds[:, 1])
print(" Z:", shaft_mesh.bounds[:, 2])

# Check collision/overlap between part and shaft at rest
# Note: The shaft rests in the cradle at Y=Y_AXLE, Z=Z_AXLE.
# The cradle has radius 1.00mm, axle has radius 0.95mm (0.05mm gap/clearance).
# Let us check any overlapping volume or minimum distance.
print(f"\nAxle max X = {shaft_mesh.bounds[1, 0]:.3f} mm")
print(f"Plunger X range = [{10.284 - 3.80/2:.3f}, {10.284 + 3.80/2:.3f}] mm")

# Let us check where the right tower and cradle are:
# Right tower inner face: X = 13.360mm, outer face: X = 14.610mm
# Right collar is at X = 14.610 + 0.40 = 15.01mm, thickness = 0.80mm (to 15.81mm)
# Axle tip is at X = 15.81mm.

# Let us test widening to the right:
# If the rocker / plunger / trunk / collar is widened by ~2mm to the right:
# What does "shaft rocker, can be ~2mm wider to the right" mean?
# Let us check:
# 1. Could the entire axle extend further right? (From 15.81 to 17.81mm? Inner wall is at 16.24mm, so extending the axle tip to 17.81mm would hit the inner wall unless the tower moves or collar shifts!).
# 2. Could the plunger / trunk / gusset web be wider to the right?
#    - Inside the towers: X extends up to X = 13.36mm (right tower inner face).
#    - The plunger currently ends at X = 12.184mm.
#    - If plunger is widened by 2mm or extends to the right tower inner wall (X = 13.26mm):
#      Wait! If plunger extends 2mm to the right from current right edge (12.184mm -> 14.184mm), it would collide with the right tower (X=13.36mm) and through hole (X=12.96mm)!
#      Wait! What if the through hole, right tower, or input cam is wider?
#      Let us check all features!
