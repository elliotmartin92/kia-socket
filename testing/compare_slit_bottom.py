"""
Compare slit bottom positions: 1mm from inner wall vs 1mm from outer wall.
"""
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from build_part import outer_pts, get_exact_bottom_arch_poly, OUTER_WALL_THICK, create_all_brackets_poly

poly = Polygon(outer_pts).difference(get_exact_bottom_arch_poly())
inner_poly = poly.buffer(-OUTER_WALL_THICK)
brackets = create_all_brackets_poly()

fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

# Option 1: 1mm from inner wall (Y_bot = -16.34mm, Y_top = -13.34mm)
# Option 2: 1mm from outer wall (Y_bot = -17.54mm, Y_top = -14.54mm)

for idx, (title, y_bot) in enumerate([
    ("1.0mm from Inner Wall Face (Y_bot = -16.34mm)", -17.339 + 1.0),
    ("1.0mm from Outer Wall Bottom (Y_bot = -17.54mm)", -18.539 + 1.0)
]):
    ax = axes[idx]
    y_top = y_bot + 3.0
    
    # Outer poly
    x, y = poly.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Outer Wall')
    
    # Inner poly
    ix, iy = inner_poly.exterior.xy
    ax.plot(ix, iy, 'b--', alpha=0.6, label='Inner Wall Face')
    
    # Brackets
    for geom in (brackets.geoms if hasattr(brackets, 'geoms') else [brackets]):
        bx, by = geom.exterior.xy
        ax.plot(bx, by, 'g-', linewidth=1.5)
        
    # Slits
    s_l = box(-8.953, y_bot, -7.853, y_top)
    s_r = box(7.853, y_bot, 8.953, y_top)
    for s in [s_l, s_r]:
        sx, sy = s.exterior.xy
        ax.fill(sx, sy, 'r', alpha=0.9, edgecolor='k')
        
    ax.annotate(f'Slit Bottom: Y = {y_bot:.2f}mm\nSlit Top: Y = {y_top:.2f}mm\n(Length = 3.0mm)',
                xy=(8.4, y_bot), xytext=(10.5, y_bot - 1.0),
                fontsize=8, fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red'))
                
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(-22, 22)
    ax.set_ylim(-22, 22)
    ax.set_title(title, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('slit_bottom_compare.png', dpi=150)
print("Saved slit_bottom_compare.png")
