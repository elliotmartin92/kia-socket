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

all_other_vertices = np.vstack([
    part_mesh.vertices[::5],
    ins_left.vertices,
    ins_right.vertices,
    shaft_plate.vertices[::5]
])

print("Current tower: r=4.0 at [27.50, -16.00]:")
t_curr = build_cooling_tower_mesh(radius=4.0, height=20.50)
t_curr.apply_translation([27.50, -16.00, 0.00])
d_curr = np.min(cdist(all_other_vertices, t_curr.vertices))
print(f"  Min clearance to any other part: {d_curr:.2f} mm")

print("\nTesting positions for r=2.0 (dia 4.0mm) and r=2.5 (dia 5.0mm):")
candidates = [
    (27.50, -22.00),
    (27.50, -25.00),
    (27.50, -28.00),
    (32.00, -22.00),
    (32.00, -25.00),
    (35.00, -20.00),
    (35.00, -25.00),
    (38.00, -16.00),
    (38.00, -20.00),
    (40.00, 0.00),
    (30.00, -26.00),
]

for r in [2.5, 2.0, 1.5]:
    print(f"\n--- Radius {r:.1f}mm (Dia {r*2:.1f}mm) ---")
    for x, y in candidates:
        t = build_cooling_tower_mesh(radius=r, height=20.50)
        t.apply_translation([x, y, 0.00])
        d_min = np.min(cdist(all_other_vertices, t.vertices))
        d_main = np.min(cdist(part_mesh.vertices[::5], t.vertices))
        d_slit = np.min(cdist(ins_left.vertices, t.vertices))
        d_shaft = np.min(cdist(shaft_plate.vertices[::5], t.vertices))
        
        # Plate overall bounding box if we place it here
        x_min = min(part_mesh.bounds[0,0], t.bounds[0,0])
        x_max = max(shaft_plate.bounds[1,0], t.bounds[1,0])
        y_min = min(part_mesh.bounds[0,1], t.bounds[0,1])
        y_max = max(shaft_plate.bounds[1,1], t.bounds[1,1])
        w = x_max - x_min
        h = y_max - y_min
        print(f"Pos [{x:5.1f}, {y:5.1f}] -> Min Clr: {d_min:5.2f} mm (Main:{d_main:5.1f}, Slit:{d_slit:5.1f}, Shaft:{d_shaft:5.1f}) | Plate BBox: {w:5.1f} x {h:5.1f} mm")
