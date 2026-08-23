"""
Test boolean union or direct lofting for 100% watertight manifold mesh.
"""
import trimesh
from shapely.geometry import box
from build_part import extrude_shapely_geom, SLIT_BOSS_HEIGHT

def build_watertight_insert():
    inner_w, inner_l = 0.60, 2.40
    outer_body = box(-3.50/2, -5.40/2, 3.50/2, 5.40/2)
    inner_hole = box(-inner_w/2, -inner_l/2, inner_w/2, inner_l/2)
    poly_body = outer_body.difference(inner_hole)
    m_body = extrude_shapely_geom(poly_body, height=SLIT_BOSS_HEIGHT)
    
    outer_key = box(-0.95/2, -2.85/2, 0.95/2, 2.85/2)
    poly_key = outer_key.difference(inner_hole)
    m_key = extrude_shapely_geom(poly_key, height=0.85 + 0.10) # 0.10 overlap for clean boolean
    m_key.apply_translation([0, 0, SLIT_BOSS_HEIGHT - 0.10])
    
    m_union = m_body.union(m_key, engine='manifold')
    return m_union

m_clean = build_watertight_insert()
print(f"Is watertight: {m_clean.is_watertight}")
print(f"Euler number: {m_clean.euler_number}")
print(f"Bounds: {m_clean.bounds}")
