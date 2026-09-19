import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import shapely.geometry as sg
from shapely.geometry import Point, Polygon
import build_part
from build_clamp import build_tower_clamp_mesh, build_unified_clamp_mesh

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

# In build_clamp.py:
# Right clamp has:
# m_saddle = extrude_yz(poly_saddle, height=14.60 - 13.20, x_offset=13.20)
# m_roof_bridge = extrude_yz(poly_roof_yz, height=15.30 - 14.60, x_offset=14.60)
# m_side_inner = extrude_yz(poly_side_arch, height=1.00, x_offset=15.30)
# m_side_outer = extrude_yz(poly_side_solid, height=0.60, x_offset=16.30)
#
# Notice: m_side_inner spans X in [15.30, 16.30], m_side_outer spans X in [16.30, 16.90]
# Total cheek plate width in X is 16.90 - 14.60 = 2.30mm!
# But the right pin ends at X = 15.00mm!
# The inner retention ledge ends at X = 15.30mm!
# If m_side_inner spans X in [14.65, 15.30] or [15.30, 15.80], and m_side_outer spans up to 16.10, or
# what if we intersect with an extruded outer_body_poly (with 0.15mm margin)?

clamp_r = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)

# Create an extrusion of outer_body_poly (buffered slightly inset by -0.10mm so clamp stays strictly within enclosure)
safe_envelope_2d = outer_body_poly.buffer(-0.10)
safe_envelope_3d = trimesh.creation.extrude_polygon(safe_envelope_2d, height=20.0)
safe_envelope_3d.apply_translation([0, 0, 0])

# Intersect clamp_r with safe_envelope_3d
clamp_trimmed = clamp_r.intersection(safe_envelope_3d, engine='manifold')
print(f"Trimmed right clamp watertight: {clamp_trimmed.is_watertight}, volume: {clamp_trimmed.volume:.2f} mm³")

# Check if any vertices are outside outer_body_poly now
outside_pts = [v for v in clamp_trimmed.vertices if not outer_body_poly.contains(Point(v[0], v[1]))]
print(f"Vertices outside baseplate after trimming: {len(outside_pts)}")

# Also test unified monolithic bridge clamp
u_clamp = build_unified_clamp_mesh(in_assembly_coords=True)
u_clamp_trimmed = u_clamp.intersection(safe_envelope_3d, engine='manifold')
print(f"Trimmed unified clamp watertight: {u_clamp_trimmed.is_watertight}, volume: {u_clamp_trimmed.volume:.2f} mm³")
outside_u = [v for v in u_clamp_trimmed.vertices if not outer_body_poly.contains(Point(v[0], v[1]))]
print(f"Unified clamp vertices outside baseplate: {len(outside_u)}")
