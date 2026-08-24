"""
testing/inspect_shaft_tower_alignment.py
Inspect current alignment between build_shaft.py and build_part.py towers.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE, PIN_DIAMETER, HUB_DIAMETER
from build_part import build_clean_shaft_towers_mesh, build_exact_3d_model, TOWER_HEIGHT, TOWER_WALL_THICK, TOWER_THROAT_W

print(f"build_shaft.py constants:")
print(f"  Y_AXLE: {Y_AXLE}")
print(f"  Z_AXLE: {Z_AXLE}")
print(f"  PIN_DIAMETER: {PIN_DIAMETER}")
print(f"  HUB_DIAMETER: {HUB_DIAMETER}")

print(f"\nbuild_part.py tower constants:")
print(f"  TOWER_HEIGHT: {TOWER_HEIGHT}")
print(f"  TOWER_WALL_THICK: {TOWER_WALL_THICK}")
print(f"  TOWER_THROAT_W: {TOWER_THROAT_W}")

# Build both meshes
towers_mesh = build_clean_shaft_towers_mesh()
shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)

print(f"\nTowers mesh bounds:")
print(f"  X: [{towers_mesh.bounds[0,0]:.3f}, {towers_mesh.bounds[1,0]:.3f}] (width: {towers_mesh.bounds[1,0]-towers_mesh.bounds[0,0]:.3f})")
print(f"  Y: [{towers_mesh.bounds[0,1]:.3f}, {towers_mesh.bounds[1,1]:.3f}] (depth: {towers_mesh.bounds[1,1]-towers_mesh.bounds[0,1]:.3f})")
print(f"  Z: [{towers_mesh.bounds[0,2]:.3f}, {towers_mesh.bounds[1,2]:.3f}] (height: {towers_mesh.bounds[1,2]-towers_mesh.bounds[0,2]:.3f})")

print(f"\nShaft mesh bounds:")
print(f"  X: [{shaft_mesh.bounds[0,0]:.3f}, {shaft_mesh.bounds[1,0]:.3f}] (width: {shaft_mesh.bounds[1,0]-shaft_mesh.bounds[0,0]:.3f})")
print(f"  Y: [{shaft_mesh.bounds[0,1]:.3f}, {shaft_mesh.bounds[1,1]:.3f}] (depth: {shaft_mesh.bounds[1,1]-shaft_mesh.bounds[0,1]:.3f})")
print(f"  Z: [{shaft_mesh.bounds[0,2]:.3f}, {shaft_mesh.bounds[1,2]:.3f}] (height: {shaft_mesh.bounds[1,2]-shaft_mesh.bounds[0,2]:.3f})")
