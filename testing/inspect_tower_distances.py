import os, sys
import trimesh
import numpy as np
from scipy.spatial.distance import cdist

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, build_slit_insert_mesh, build_cooling_tower_mesh
from build_shaft import build_shaft_rocker_mesh

part_mesh, _ = build_exact_3d_model()
ins_left = build_slit_insert_mesh(is_right=False)
ins_left.apply_translation([27.50, -5.00, 0.00])

ins_right = build_slit_insert_mesh(is_right=True)
ins_right.apply_translation([27.50, 5.00, 0.00])

shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
shaft_plate = shaft_printable.copy()
shaft_plate.apply_translation([27.50, 16.00, 0.00])

print("Part bounds:")
print("  Main Part:   X in [%.2f, %.2f], Y in [%.2f, %.2f]" % (part_mesh.bounds[0,0], part_mesh.bounds[1,0], part_mesh.bounds[0,1], part_mesh.bounds[1,1]))
print("  Slit Left:   X in [%.2f, %.2f], Y in [%.2f, %.2f]" % (ins_left.bounds[0,0], ins_left.bounds[1,0], ins_left.bounds[0,1], ins_left.bounds[1,1]))
print("  Shaft Rocker:X in [%.2f, %.2f], Y in [%.2f, %.2f]" % (shaft_plate.bounds[0,0], shaft_plate.bounds[1,0], shaft_plate.bounds[0,1], shaft_plate.bounds[1,1]))

for r in [4.0, 3.0, 2.5, 2.0, 1.5]:
    for pos_x, pos_y in [(27.50, -16.00), (27.50, -20.00), (32.00, -16.00), (32.00, -20.00), (30.00, -22.00), (35.00, -15.00)]:
        cool_tower = build_cooling_tower_mesh(radius=r, height=20.50)
        cool_tower.apply_translation([pos_x, pos_y, 0.00])
        
        # Subsample vertices for fast distance estimation
        v_tower = cool_tower.vertices
        d_main = np.min(cdist(part_mesh.vertices[::5], v_tower))
        d_ins_left = np.min(cdist(ins_left.vertices, v_tower))
        d_shaft = np.min(cdist(shaft_plate.vertices[::5], v_tower))
        print(f"r={r:.1f} (dia {r*2:.1f}mm) at [{pos_x:.1f}, {pos_y:.1f}]:")
        print(f"  dist Main Part: {d_main:.2f} mm | dist Slit Left: {d_ins_left:.2f} mm | dist Shaft: {d_shaft:.2f} mm")
