import os
import sys
import trimesh
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, build_slit_insert_mesh, build_cooling_tower_mesh
from build_shaft import build_shaft_rocker_mesh

def main():
    part_mesh, _ = build_exact_3d_model()
    ins_left = build_slit_insert_mesh(is_right=False)
    ins_left.apply_translation([27.50, -5.00, 0.00])
    
    ins_right = build_slit_insert_mesh(is_right=True)
    ins_right.apply_translation([27.50, 5.00, 0.00])
    
    shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
    shaft_plate = shaft_printable.copy()
    shaft_plate.apply_translation([27.50, 16.00, 0.00])
    
    cool_tower = build_cooling_tower_mesh(radius=4.0, height=20.50)
    cool_tower.apply_translation([27.50, -16.00, 0.00])
    
    print("=== Current Component Bounding Boxes ===")
    print("Main Part bounds:")
    print("  X:", part_mesh.bounds[:, 0])
    print("  Y:", part_mesh.bounds[:, 1])
    print("  Z:", part_mesh.bounds[:, 2])
    
    print("Slit Left bounds:")
    print("  X:", ins_left.bounds[:, 0])
    print("  Y:", ins_left.bounds[:, 1])
    print("  Z:", ins_left.bounds[:, 2])
    
    print("Slit Right bounds:")
    print("  X:", ins_right.bounds[:, 0])
    print("  Y:", ins_right.bounds[:, 1])
    print("  Z:", ins_right.bounds[:, 2])
    
    print("Shaft Rocker bounds:")
    print("  X:", shaft_plate.bounds[:, 0])
    print("  Y:", shaft_plate.bounds[:, 1])
    print("  Z:", shaft_plate.bounds[:, 2])
    
    print("Cooling Tower bounds:")
    print("  X:", cool_tower.bounds[:, 0])
    print("  Y:", cool_tower.bounds[:, 1])
    print("  Z:", cool_tower.bounds[:, 2])

if __name__ == '__main__':
    main()
