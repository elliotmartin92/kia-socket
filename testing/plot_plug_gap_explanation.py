"""
testing/plot_plug_gap_explanation.py
Illustrates the exact physical standoff gap measurement between plug body and outlet faceplate.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_gap():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1a1a1a', dpi=180)
    ax.set_facecolor('#222222')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#555555')
        
    ax.set_title("How to Measure Check 2: The Exposed Blade Standoff Gap", color='white', fontsize=13, weight='bold', pad=15)
    
    # Outlet Bezel Front Face (Vertical line at X = 0)
    ax.add_patch(patches.Rectangle((-2, -6), 2, 12, facecolor='#34495e', edgecolor='#2c3e50', lw=2, label='Outlet Bezel / Faceplate'))
    
    # Plug Body (Rectangle on the right)
    gap = 4.5  # 4.5 mm gap
    ax.add_patch(patches.Rectangle((gap, -5), 8, 10, facecolor='#e67e22', edgecolor='#d35400', lw=2, label='Plug Body / Plastic Housing'))
    
    # Metal Blades (Prongs)
    blade_len = 16.5
    ax.add_patch(patches.Rectangle((gap - blade_len, 2.0), blade_len, 1.5, facecolor='#bdc3c7', edgecolor='white', lw=1.5, label='Plug Metal Blade (Prong)'))
    ax.add_patch(patches.Rectangle((gap - blade_len, -3.5), blade_len, 1.5, facecolor='#bdc3c7', edgecolor='white', lw=1.5))
    
    # Internal Obstruction (Locked Rocker Cam at X = -12.0)
    ax.add_patch(patches.Rectangle((-14, 1.5), 3, 2.5, facecolor='#e74c3c', alpha=0.8, edgecolor='#c0392b', lw=2, label='Locked Cam Obstruction'))
    
    # Gap dimension arrow [M1]
    ax.annotate('', xy=(0, -0.5), xytext=(gap, -0.5),
                 arrowprops=dict(arrowstyle='<->', color='#00d2ff', lw=3))
    ax.text(gap / 2.0, 0.2, f"Remaining Gap\n({gap:.1f} mm)", color='#00d2ff', fontsize=11, weight='bold', ha='center')
    
    # Annotation
    ax.annotate('Blade Tip hits\nlocked Cam inside', xy=(gap - blade_len, 2.75), xytext=(-16, 4.5),
                arrowprops=dict(facecolor='#ff7675', edgecolor='#d63031', width=2, headwidth=6),
                color='#ff7675', fontsize=10, weight='bold', bbox=dict(boxstyle='round,pad=0.3', fc='#2d3436', ec='#ff7675'))
                
    ax.annotate('Plug Body cannot\npush in all the way', xy=(gap, 4.0), xytext=(gap + 2.0, 6.0),
                arrowprops=dict(facecolor='#f39c12', edgecolor='#e67e22', width=2, headwidth=6),
                color='#f39c12', fontsize=10, weight='bold', bbox=dict(boxstyle='round,pad=0.3', fc='#2d3436', ec='#f39c12'))
    
    ax.set_xlim(-18, 15)
    ax.set_ylim(-7, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='lower left', fontsize=9, facecolor='#333333', edgecolor='#555555', labelcolor='white')
    
    plt.tight_layout()
    plt.savefig('testing/plug_gap_check2_diagram.png', dpi=200)
    print("Saved testing/plug_gap_check2_diagram.png")

if __name__ == '__main__':
    plot_gap()
