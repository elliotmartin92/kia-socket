"""
Generate detailed close-up diagrams of snap clips and interior ribbing options.
"""
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=150)

# 1. Snap Hook Options
ax1 = axes[0]
# Option A: Outward Hook
stem_x = [0, 0, 1.0, 1.0]
stem_y = [0, 7.5, 7.5, 0]
hook_out_x = [1.0, 1.8, 1.0]
hook_out_y = [6.0, 7.5, 7.5]

ax1.fill(stem_x, stem_y, color='#4A90E2', alpha=0.7, label='Stem Arm (1.0mm)')
ax1.fill(hook_out_x, hook_out_y, color='#E74C3C', alpha=0.8, label='Outward Hook (Ramp)')

# Option B: Inward Hook (dashed line)
hook_in_x = [0.0, -0.8, 0.0]
hook_in_y = [6.0, 7.5, 7.5]
ax1.plot(hook_in_x + [0.0], hook_in_y + [6.0], 'k--', linewidth=2, label='Inward Hook Option')

ax1.set_xlim(-2, 3)
ax1.set_ylim(-0.5, 8.5)
ax1.set_aspect('equal')
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.set_title('Snap-Fit Clip Profile Detail (Side View)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Thickness (mm)')
ax1.set_ylabel('Height Z (mm)')
ax1.legend(loc='lower right')
ax1.annotate('Lead-in Ramp\n(Push-in angle)', xy=(1.4, 6.75), xytext=(2.0, 5.0),
             arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)
ax1.annotate('Retention Shoulder\n(Locks against mating part)', xy=(1.4, 7.5), xytext=(1.8, 8.0),
             arrowprops=dict(arrowstyle='->', color='black'), fontsize=9)

# 2. Interior Ribbing Layout Concept
ax2 = axes[1]
theta = np.linspace(0, 2*np.pi, 200)
r_outer = 19.25
ax2.plot(r_outer * np.cos(theta), r_outer * np.sin(theta), 'k-', linewidth=2, label='Outer Rim (6.77mm wall)')

# Concentric circular rib option
r_rib = 13.0
ax2.plot(r_rib * np.cos(theta), r_rib * np.sin(theta), 'c--', linewidth=1.5, label='Circular Rib Option (0.5mm tall)')

# Radial ribs option
for ang in [30, 90, 150, 210, 270, 330]:
    rad = np.radians(ang)
    ax2.plot([5 * np.cos(rad), (r_outer - 1.2) * np.cos(rad)], 
             [5 * np.sin(rad), (r_outer - 1.2) * np.sin(rad)], 
             color='#F39C12', linewidth=2, linestyle=':', label='Radial Stiffener' if ang==30 else "")

ax2.set_xlim(-22, 22)
ax2.set_ylim(-22, 22)
ax2.set_aspect('equal')
ax2.grid(True, linestyle='--', alpha=0.5)
ax2.set_title('Interior Ribbing Concepts (0.5mm tall on base)', fontsize=12, fontweight='bold')
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.legend(loc='lower left', fontsize=8)

plt.tight_layout()
plt.savefig('clip_and_rib_details.png', dpi=150)
print("Saved clip_and_rib_details.png")
