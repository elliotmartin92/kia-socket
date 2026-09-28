"""
testing/analyze_shaft_print_orientations.py
Comprehensive analysis of all print angles around X axis for shaft_rocker.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

# Get raw shaft rocker mesh in assembly coordinates
shaft_raw = build_shaft_rocker_mesh(in_assembly_coords=True)

# Test rotation angles around X axis in steps of 5 degrees
angles = np.arange(0, 360, 5)
results = []

for ang in angles:
    m = shaft_raw.copy()
    rot = trimesh.transformations.rotation_matrix(np.radians(ang), [1, 0, 0])
    m.apply_transform(rot)
    
    # Shift Z_min to 0
    b = m.bounds
    m.apply_translation([
        -(b[0, 0] + b[1, 0])/2.0,
        -(b[0, 1] + b[1, 1])/2.0,
        -b[0, 2]
    ])
    
    v = m.vertices
    f = m.faces
    normals = m.face_normals
    areas = m.area_faces
    
    # Bed contact: faces with all vertices Z < 0.08mm and normal[2] < -0.7
    bed_area = 0.0
    for i, face in enumerate(f):
        if np.all(v[face, 2] < 0.08) and normals[i, 2] < -0.7:
            bed_area += areas[i]
            
    # Overhang area requiring support: Z > 0.15mm, normal[2] < -0.707 (slope < 45 deg to horizontal)
    overhang_area = 0.0
    for i, face in enumerate(f):
        if np.min(v[face, 2]) > 0.15 and normals[i, 2] < -0.707:
            overhang_area += areas[i]
            
    # Pin Z min
    # Left pin is at X < -3.70
    v_lpin = v[v[:, 0] < -3.70]
    lpin_zmin = np.min(v_lpin[:, 2]) if len(v_lpin) > 0 else 0
    
    z_height = m.bounds[1, 2]
    y_span = m.bounds[1, 1] - m.bounds[0, 1]
    
    results.append({
        'angle': ang,
        'bed_area': bed_area,
        'overhang_area': overhang_area,
        'lpin_zmin': lpin_zmin,
        'z_height': z_height,
        'y_span': y_span
    })

# Sort by overhang area ascending, or filter where bed_area > 5
print(f"{'Angle':<6} | {'Bed Area':<10} | {'Overhang Area':<14} | {'Pin Z_min':<10} | {'Height':<8} | {'Y span':<8}")
print("-" * 65)

# Sort by bed area descending
top_bed = sorted(results, key=lambda r: r['bed_area'], reverse=True)[:10]
print("--- TOP 10 BY BED CONTACT AREA ---")
for r in top_bed:
    print(f"{r['angle']:4d}° | {r['bed_area']:8.2f} mm² | {r['overhang_area']:12.2f} mm² | {r['lpin_zmin']:8.2f} mm | {r['z_height']:6.2f}mm | {r['y_span']:6.2f}mm")

# Sort by lowest overhang area among those with bed_area >= 5.0
good_bed = [r for r in results if r['bed_area'] >= 5.0]
top_low_overhang = sorted(good_bed, key=lambda r: r['overhang_area'])[:10]
print("\n--- TOP 10 LOWEST OVERHANG (with Bed Area >= 5 mm²) ---")
for r in top_low_overhang:
    print(f"{r['angle']:4d}° | {r['bed_area']:8.2f} mm² | {r['overhang_area']:12.2f} mm² | {r['lpin_zmin']:8.2f} mm | {r['z_height']:6.2f}mm | {r['y_span']:6.2f}mm")

# Also check around 198.6° (current angle)
print("\n--- AROUND CURRENT ANGLE (195° - 205°) ---")
for r in results:
    if 190 <= r['angle'] <= 210:
        print(f"{r['angle']:4d}° | {r['bed_area']:8.2f} mm² | {r['overhang_area']:12.2f} mm² | {r['lpin_zmin']:8.2f} mm | {r['z_height']:6.2f}mm | {r['y_span']:6.2f}mm")
