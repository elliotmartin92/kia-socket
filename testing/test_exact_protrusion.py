import sys
sys.path.insert(0, '.')
import trimesh
from build_part import get_exact_base_polygon, OUTER_WALL_THICK, extrude_shapely_geom
import build_clamp

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

clamp_r = build_clamp.build_tower_clamp_mesh('right', in_assembly_coords=True)
clamp_bridge = build_clamp.build_unified_clamp_mesh(in_assembly_coords=True)

print("clamp_r watertight:", clamp_r.is_watertight, "volume:", clamp_r.volume)
print("clamp_bridge watertight:", clamp_bridge.is_watertight, "volume:", clamp_bridge.volume)

env_ext = extrude_shapely_geom(outer_body_poly, height=25.0)
print("env_ext watertight:", env_ext.is_watertight, "volume:", env_ext.volume)

env_int = extrude_shapely_geom(inner_poly, height=25.0)
print("env_int watertight:", env_int.is_watertight, "volume:", env_int.volume)
