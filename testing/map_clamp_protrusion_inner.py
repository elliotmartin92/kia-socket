import sys
sys.path.insert(0, '.')
import numpy as np
from shapely.geometry import LineString, Point
from build_part import get_exact_base_polygon, OUTER_WALL_THICK
import build_clamp

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
clamp_bridge = build_clamp.build_unified_clamp_mesh(in_assembly_coords=True)

print(f"{'X (mm)':<8} | {'Clamp Y_max':<12} | {'Wall Int Y_max':<15} | {'Margin to Int (+ is inside, - is in/past wall)'}")
print("-" * 75)

for x in np.arange(1.6, 17.0, 0.5):
    v_slice = clamp_bridge.vertices[np.abs(clamp_bridge.vertices[:, 0] - x) <= 0.25]
    if len(v_slice) == 0:
        continue
    clamp_y_max = v_slice[:, 1].max()
    
    # Intersect ray with inner_poly
    ray = LineString([(x, 0), (x, 25)])
    inter = inner_poly.exterior.intersection(ray)
    pts_y = []
    if inter.geom_type == 'Point':
        pts_y.append(inter.y)
    elif hasattr(inter, 'geoms'):
        for g in inter.geoms:
            if g.geom_type == 'Point':
                pts_y.append(g.y)
            elif g.geom_type == 'LineString':
                pts_y.extend(g.xy[1])
    if len(pts_y) > 0:
        wall_y = max(pts_y)
        margin = wall_y - clamp_y_max
        flag = " <-- IN WALL / STICKS OUT!" if margin < -0.01 else ""
        print(f"{x:6.2f}   | {clamp_y_max:8.2f} mm    | {wall_y:8.2f} mm       | {margin:8.2f} mm {flag}")
