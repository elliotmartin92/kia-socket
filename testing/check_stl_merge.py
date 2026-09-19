import trimesh

m_stl = trimesh.load('part.stl')
print(f"STL: watertight={m_stl.is_watertight}")
m_stl.merge_vertices()
print(f"STL after merge_vertices: watertight={m_stl.is_watertight}")

m_obj = trimesh.load('part.obj')
print(f"OBJ: watertight={m_obj.is_watertight}")
m_obj.merge_vertices()
print(f"OBJ after merge_vertices: watertight={m_obj.is_watertight}")
