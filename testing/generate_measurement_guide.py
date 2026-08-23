import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#1e1e1e')

# Style configuration
for ax in (ax1, ax2):
    ax.set_facecolor('#252526')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#555555')
    ax.spines['top'].set_color('#555555')
    ax.spines['left'].set_color('#555555')
    ax.spines['right'].set_color('#555555')

# --- Panel 1: Top-Down View ---
ax1.set_title("TOP-DOWN VIEW (Axle & Rib Array)", color='white', fontsize=13, weight='bold', pad=15)
ax1.set_xlim(-1, 15)
ax1.set_ylim(-3, 8)
ax1.set_aspect('equal')

# Main axle pins
# Left pin: x in [0, 2], y in [2.5, 4.5] (dia ~ 2)
# Center hub: x in [2, 9.5], y in [2.2, 4.8] (dia ~ 2.6)
# Right pin: x in [9.5, 11.5], y in [2.5, 4.5]
ax1.add_patch(patches.Rectangle((0, 2.5), 2.0, 2.0, color='#888888', ec='cyan', lw=1.5))
ax1.add_patch(patches.Rectangle((9.5, 2.5), 2.0, 2.0, color='#888888', ec='cyan', lw=1.5))
ax1.add_patch(patches.Rectangle((2.0, 2.1), 7.5, 2.8, color='#555555', ec='white', lw=1.5))

# Upper Cam Tab
ax1.add_patch(patches.Rectangle((3.5, 4.9), 3.0, 2.2, color='#4a90e2', ec='deepskyblue', lw=1.5))

# 3 Downward Ribs
# Rib 1 (left): x in [3.5, 4.3], y in [0.0, 2.1]
# Rib 2 (center): x in [4.7, 5.5], y in [-1.5, 2.1]
# Rib 3 (right): x in [5.9, 6.7], y in [0.0, 2.1]
ax1.add_patch(patches.Rectangle((3.5, 0.2), 0.8, 1.9, color='#e67e22', ec='yellow', lw=1.5))
ax1.add_patch(patches.Rectangle((4.6, -1.5), 1.0, 3.6, color='#e74c3c', ec='yellow', lw=1.5))
ax1.add_patch(patches.Rectangle((5.8, 0.2), 0.8, 1.9, color='#e67e22', ec='yellow', lw=1.5))

# Dimension 1: Total Axle Length (0 to 11.5)
ax1.annotate('', xy=(0, 6.5), xytext=(11.5, 6.5),
             arrowprops=dict(arrowstyle='<->', color='#2ecc71', lw=2))
ax1.text(5.75, 6.8, "(1) Total Length = 11.5 mm", color='#2ecc71', ha='center', fontsize=11, weight='bold')

# Dimension 3: Pin Extension (0 to 2.0)
ax1.annotate('', xy=(0, 1.2), xytext=(2.0, 1.2),
             arrowprops=dict(arrowstyle='<->', color='#00d2ff', lw=2))
ax1.text(1.0, 0.4, "(3) Pin Ext", color='#00d2ff', ha='center', fontsize=10, weight='bold')

# Dimension 4: Central Body Width (2.0 to 9.5)
ax1.annotate('', xy=(2.0, -2.5), xytext=(9.5, -2.5),
             arrowprops=dict(arrowstyle='<->', color='#f39c12', lw=2))
ax1.text(5.75, -2.2, "(4) Central Body Width", color='#f39c12', ha='center', fontsize=11, weight='bold')

# Dimension 5: Total Width across 3 Ribs (3.5 to 6.6)
ax1.annotate('', xy=(3.5, -0.6), xytext=(6.6, -0.6),
             arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=2))
ax1.text(5.05, -0.3, "(5) Width across 3 ribs", color='#e74c3c', ha='center', fontsize=10, weight='bold')


# --- Panel 2: Side Profile View ---
ax2.set_title("SIDE PROFILE VIEW (Bellcrank Angle & Pin Dia)", color='white', fontsize=13, weight='bold', pad=15)
ax2.set_xlim(-4, 7)
ax2.set_ylim(-5, 6)
ax2.set_aspect('equal')

# Pivot axle circle
circle = plt.Circle((0, 0), 1.135, color='#888888', ec='cyan', lw=2)
ax2.add_patch(circle)

# Upper Cam Arm Profile
cam_pts = np.array([[0.5, 0.8], [3.2, 3.8], [2.2, 4.4], [-0.5, 1.0]])
ax2.add_patch(patches.Polygon(cam_pts, closed=True, color='#4a90e2', ec='deepskyblue', lw=1.5))

# Lower Plunger Profile (3-Rib Side)
plunger_pts = np.array([[-0.8, -0.5], [0.8, -0.5], [0.5, -3.8], [-0.5, -3.8]])
ax2.add_patch(patches.Polygon(plunger_pts, closed=True, color='#e74c3c', ec='yellow', lw=1.5))

# Dimension 2: Pin Diameter
ax2.annotate('', xy=(-1.135, 0), xytext=(1.135, 0),
             arrowprops=dict(arrowstyle='<->', color='#00d2ff', lw=2))
ax2.text(0, -1.8, "(2) Pin Dia = 2.27 mm", color='#00d2ff', ha='center', fontsize=11, weight='bold')

# Bellcrank Angle indicator
arc = patches.Arc((0, 0), 4.0, 4.0, angle=0, theta1=-75, theta2=45, color='#f1c40f', lw=2, ls='--')
ax2.add_patch(arc)
ax2.text(2.5, -0.5, "Bellcrank Angle\n(~100°-115°)", color='#f1c40f', fontsize=10, weight='bold')

# Cam width / thickness
ax2.text(3.6, 3.8, "(6) Cam Tab\nLength & Thickness", color='#4a90e2', fontsize=10, weight='bold')

plt.tight_layout()
plt.savefig("testing/measurement_guide_diagram.png", dpi=300)
print("Saved testing/measurement_guide_diagram.png")
