import sys
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import Point
from build_part import get_exact_base_polygon, OUTER_WALL_THICK
import build_clamp

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

clamp_l = build_clamp.build_tower_clamp_mesh('left', in_assembly_coords=True)
clamp_r = build_clamp.build_tower_clamp_mesh('right', in_assembly_coords=True)
clamp_bridge = build_clamp.build_unified_clamp_mesh(in_assembly_coords=True)

for name, mesh in [('Left Clamp', clamp_l), ('Right Clamp', clamp_r), ('Unified Bridge Clamp', clamp_bridge)]:
    v = mesh.vertices
    out_ext = []
    in_wall = []
    in_int = []
    for pt in v:
        p = Point(pt[0], pt[1])
        if not outer_body_poly.contains(p):
            out_ext.append(pt)
        elif not inner_poly.contains(p):
            in_wall.append(pt)
        else:
            in_int.append(pt)
            
    print(f"\n=== {name} ===")
    print(f"Total vertices: {len(v)}")
    print(f"Vertices outside EXTERIOR wall: {len(out_ext)}")
    if len(out_ext) > 0:
        oe = np.array(out_ext)
        print(f"  Outside Ext: X in [{oe[:,0].min():.2f}, {oe[:,0].max():.2f}], Y in [{oe[:,1].min():.2f}, {oe[:,1].max():.2f}], Z in [{oe[:,2].min():.2f}, {oe[:,2].max():.2f}]")
        # max protrusion distance
        dists = [outer_body_poly.exterior.distance(Point(p[0], p[1])) for p in oe]
        print(f"  Max protrusion beyond exterior: {max(dists):.3f} mm")
    print(f"Vertices inside WALL body (between inner & outer faces): {len(in_wall)}")
    if len(in_wall) > 0:
        iw = np.array(in_wall)
        print(f"  In Wall: X in [{iw[:,0].min():.2f}, {iw[:,0].max():.2f}], Y in [{iw[:,1].min():.2f}, {iw[:,1].max():.2f}], Z in [{iw[:,2].min():.2f}, {iw[:,2].max():.2f}]")
    print(f"Vertices inside INTERIOR cavity: {len(in_int)}")
