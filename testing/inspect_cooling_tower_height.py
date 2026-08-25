"""
testing/inspect_cooling_tower_height.py
Inspect heights of all printed components on build plate to determine cooling tower height.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
from build_part import build_exact_3d_model, build_slit_insert_mesh
from build_shaft import build_shaft_rocker_mesh

part_mesh, _ = build_exact_3d_model()
shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
slit_insert = build_slit_insert_mesh()

print("=== Part Heights on Build Plate (Z_min = 0.00mm) ===")
print(f"Main Baseplate Part: Z_max = {part_mesh.bounds[1,2]:.3f} mm (Height: {part_mesh.bounds[1,2] - part_mesh.bounds[0,2]:.3f} mm)")
print(f"Slit Insert:         Z_max = {slit_insert.bounds[1,2]:.3f} mm (Height: {slit_insert.bounds[1,2] - slit_insert.bounds[0,2]:.3f} mm)")
print(f"Shaft Rocker:        Z_max = {shaft_printable.bounds[1,2]:.3f} mm (Height: {shaft_printable.bounds[1,2] - shaft_printable.bounds[0,2]:.3f} mm)")

# Target cooling tower height should match or slightly exceed the tallest component
# e.g., 20.50mm or 20.00mm to cover shaft rocker (19.86mm) with a 0.5-1.0mm safety margin
recommended_height = 20.50
print(f"\nRecommended Cooling Tower Height: {recommended_height:.2f} mm (Diameter: Ø8.00 mm)")
print(f"Margin above Shaft Rocker tip: {recommended_height - shaft_printable.bounds[1,2]:.2f} mm")
print(f"Margin above Main Baseplate tower tips: {recommended_height - part_mesh.bounds[1,2]:.2f} mm")
