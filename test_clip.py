"""
Test sharp-top triangular snap clip with 1.59mm radial overhang.
"""
import numpy as np
import matplotlib.pyplot as plt
import trimesh

# Clip parameters
CLIP_ARM_THICK = 1.00
CLIP_ARM_WIDTH = 3.00
OVERHANG = 1.59
WALL_HEIGHT = 6.77

# Let's test two vertical apex heights:
# Option 1: Flush with outer wall (Z_top = 6.77mm)
# Option 2: Slightly proud (Z_top = 7.20mm)
# Option 3: User's 7.87mm measurement but sharp

fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=150)

for idx, (title, z_top, hook_h) in enumerate([
    ("A: Flush with Wall (Apex Z = 6.77mm)", 6.77, 2.0),
    ("B: Moderately Proud (Apex Z = 7.20mm)", 7.20, 2.0),
    ("C: Total Height 7.87mm with Sharp Apex", 7.87, 2.5),
]):
    ax = axes[idx]
    # Wall reference line
    ax.axhline(WALL_HEIGHT, color='gray', linestyle='--', label=f'Wall Rim ({WALL_HEIGHT}mm)')
    ax.axhline(WALL_HEIGHT - 3.70, color='brown', linestyle=':', label='Flex Slot Bottom (3.07mm)')
    
    # Stem polygon: from X=0 to X=CLIP_ARM_THICK, Z=0 to Z_top - hook_h
    # Hook vertices:
    # (0, 0) -> bottom of stem
    # (CLIP_ARM_THICK, 0)
    # (CLIP_ARM_THICK, z_top - hook_h) -> start of outward wedge
    # (CLIP_ARM_THICK + OVERHANG, z_top - hook_h/2) -> maximum outward barb point (1.59mm overhang)
    # (CLIP_ARM_THICK, z_top) -> sharp top apex
    # (0, z_top) -> inner top
    # (0, 0)
    
    xs = [0, CLIP_ARM_THICK, CLIP_ARM_THICK, CLIP_ARM_THICK + OVERHANG, 0, 0]
    ys = [0, 0, z_top - hook_h, z_top - hook_h*0.4, z_top, 0]
    
    ax.fill(xs, ys, color='#4A90E2', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Annotate sharp apex and overhang
    ax.plot([CLIP_ARM_THICK + OVERHANG], [z_top - hook_h*0.4], 'ro')
    ax.annotate(f'Overhang:\n+{OVERHANG}mm', 
                xy=(CLIP_ARM_THICK + OVERHANG, z_top - hook_h*0.4),
                xytext=(CLIP_ARM_THICK + OVERHANG + 0.3, z_top - hook_h*0.4 - 0.5),
                fontsize=8, fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red'))
                
    ax.annotate('Sharp Apex', xy=(0.5, z_top), xytext=(0.5, z_top + 0.6),
                fontsize=8, fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', color='black'))

    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xlim(-1, 4)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlabel('Radial Thickness X (mm)')
    ax.set_ylabel('Height Z (mm)')
    if idx == 0:
        ax.legend(loc='lower left', fontsize=7)

plt.tight_layout()
plt.savefig('clip_apex_options.png', dpi=150)
print("Saved clip_apex_options.png")
