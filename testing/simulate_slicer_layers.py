"""
testing/simulate_slicer_layers.py
Layer-by-layer slicer simulation to find floating islands and steep overhangs.
"""

import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

mesh = trimesh.load('shaft_rocker_clean.stl')

layer_height = 0.20
z_levels = np.arange(0.10, mesh.bounds[1, 2] + layer_height, layer_height)

prev_poly = None

print("=" * 80)
print(f"SLICER LAYER-BY-LAYER SIMULATION (Layer Height = {layer_height} mm)")
print("=" * 80)

islands = []
steep_overhangs = []

for i, z in enumerate(z_levels):
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None or len(sec.discrete) == 0:
        continue
    
    polys = []
    for d in sec.discrete:
        if len(d) >= 3:
            p = Polygon(d[:, :2])
            if p.is_valid and p.area > 0.01:
                polys.append(p)
            elif not p.is_valid:
                p_fixed = p.buffer(0)
                if p_fixed.area > 0.01:
                    polys.append(p_fixed)
                    
    if len(polys) == 0:
        continue
    curr_union = unary_union(polys)
    
    if prev_poly is not None:
        if hasattr(curr_union, 'geoms'):
            curr_geoms = list(curr_union.geoms)
        else:
            curr_geoms = [curr_union]
            
        for g in curr_geoms:
            if not g.intersects(prev_poly):
                islands.append((z, g.area, g.bounds))
                print(f"!!! FLOATING MID-AIR ISLAND at Z = {z:.2f} mm: Area = {g.area:.2f} mm², Bounds = [X: {g.bounds[0]:.2f}..{g.bounds[2]:.2f}, Y: {g.bounds[1]:.2f}..{g.bounds[3]:.2f}]")
        
        # Check unsupported overhang (dilation by 0.20 mm = 45°)
        prev_dilated = prev_poly.buffer(layer_height * 1.0)
        unsupported = curr_union.difference(prev_dilated)
        if unsupported.area > 0.8:
            steep_overhangs.append((z, unsupported.area, unsupported.bounds))
            print(f"    Steep overhang (>45°) at Z = {z:.2f} mm: Area = {unsupported.area:.2f} mm², Bounds = [X: {unsupported.bounds[0]:.2f}..{unsupported.bounds[2]:.2f}, Y: {unsupported.bounds[1]:.2f}..{unsupported.bounds[3]:.2f}]")
            
    prev_poly = curr_union

print("=" * 80)
print(f"Total floating islands found: {len(islands)}")
print(f"Total steep overhang layers found: {len(steep_overhangs)}")
