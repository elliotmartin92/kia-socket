"""
Diagnostic script: Inspect and compare clip profiles:
1. Current Squared-Off Triangle (flat ramp + 0.35mm blunt land)
2. Rounded Lead-in Profile (tangent to outer diameter at retention shelf)
3. 3D mesh generation and insertion force mechanics.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import matplotlib.pyplot as plt

CLIP_HEIGHT = 6.77
CLIP_HOOK_HEIGHT = 1.80
CLIP_BLUNT_HEIGHT = 0.35
CLIP_HOOK_DEPTH = 2.10
CLIP_ARM_WIDTH = 4.20
stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
top_z = CLIP_HEIGHT  # 6.77mm
H = CLIP_HOOK_HEIGHT  # 1.80mm
D = CLIP_HOOK_DEPTH  # 2.10mm

# Profile 1: Current Squared-off Triangle
# (r=0, z=top_z) -> (r=D, z=stem_h + blunt_h) -> (r=D, z=stem_h) -> (r=0, z=stem_h)
z_vals_sq = np.linspace(stem_h, top_z, 100)
r_vals_sq = []
for z in z_vals_sq:
    if z < stem_h + CLIP_BLUNT_HEIGHT:
        r_vals_sq.append(D)
    else:
        # linear ramp from (D, stem_h + blunt_h) to (0, top_z)
        frac = (top_z - z) / (top_z - (stem_h + CLIP_BLUNT_HEIGHT))
        r_vals_sq.append(D * frac)
r_vals_sq = np.array(r_vals_sq)

# Profile 2: Elliptical Arc (tangent to vertical at outer diameter r=D, z=stem_h)
# (r/D)^2 + ((z - stem_h)/H)^2 = 1 => r(z) = D * sqrt(1 - ((z - stem_h)/H)^2)
z_vals_rnd = np.linspace(stem_h, top_z, 100)
r_vals_rnd = D * np.sqrt(np.maximum(0.0, 1.0 - ((z_vals_rnd - stem_h) / H)**2))

# Profile 3: Circular Arc with radius matching outer diameter / blend
# Let's consider a circular arc tangent at (D, stem_h):
# Circle center at (D - R_c, stem_h), radius R_c.
# To pass through (0, top_z): (0 - (D - R_c))^2 + (top_z - stem_h)^2 = R_c^2
# (R_c - D)^2 + H^2 = R_c^2 => R_c^2 - 2*D*R_c + D^2 + H^2 = R_c^2
# 2*D*R_c = D^2 + H^2 => R_c = (D^2 + H^2) / (2*D)
R_circ = (D**2 + H**2) / (2 * D)
# For D=2.10, H=1.80: R_circ = (2.10^2 + 1.80^2) / (2 * 2.10) = (4.41 + 3.24) / 4.20 = 7.65 / 4.20 = 1.821 mm
# Center of circle is at r_c = D - R_circ = 2.10 - 1.821 = 0.279 mm, z_c = stem_h = 4.97 mm
# For z from stem_h to top_z:
# (r - r_c)^2 + (z - z_c)^2 = R_circ^2 => r(z) = r_c + sqrt(R_circ^2 - (z - z_c)^2)
r_vals_circ = (D - R_circ) + np.sqrt(np.maximum(0.0, R_circ**2 - (z_vals_rnd - stem_h)**2))

# Profile 4: Rounded with small flat shelf land (0.15mm) then tangent arc
# Retains a tiny 0.15mm flat land at max diameter before curving
land_h = 0.15
H_eff = H - land_h
z_vals_land = np.linspace(stem_h, top_z, 100)
r_vals_land = []
for z in z_vals_land:
    if z < stem_h + land_h:
        r_vals_land.append(D)
    else:
        r_vals_land.append(D * np.sqrt(np.maximum(0.0, 1.0 - ((z - (stem_h + land_h)) / H_eff)**2)))
r_vals_land = np.array(r_vals_land)

fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=200)

# Panel 1: Profile Comparison
ax1 = axes[0]
ax1.set_title("Snap Clip Cross-Section: Squared-Off Triangle vs Rounded Arc", fontsize=11, fontweight='bold')
ax1.plot(r_vals_sq, z_vals_sq, 'r-', lw=2.5, label='Current: Squared-Off Triangle (0.35mm blunt land)')
ax1.plot(r_vals_rnd, z_vals_rnd, 'g-', lw=2.5, label=f'Option A: Elliptical Arc (Tangent to outer D={D:.2f}mm)')
ax1.plot(r_vals_circ, z_vals_rnd, 'b--', lw=2.0, label=f'Option B: Circular Arc (R={R_circ:.2f}mm)')
ax1.plot(r_vals_land, z_vals_land, 'm-.', lw=2.0, label=f'Option C: Hybrid (0.15mm land + Elliptical Arc)')

# Plot retention shelf
ax1.plot([0, D], [stem_h, stem_h], 'k-', lw=3, label=f'Retention Undercut Shelf (Z={stem_h:.2f}mm)')
ax1.axvline(0, color='gray', linestyle=':', label='Outer Wall Face (r=0)')
ax1.axhline(top_z, color='gray', linestyle='--', label=f'Perimeter Wall Rim (Z={top_z:.2f}mm)')

ax1.set_xlabel("Radial Protrusion beyond Outer Wall (mm)", fontsize=10, fontweight='bold')
ax1.set_ylabel("Elevation Z (mm)", fontsize=10, fontweight='bold')
ax1.set_xlim(-0.2, 2.5)
ax1.set_ylim(4.5, 7.2)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower left', fontsize=8.5)

# Panel 2: Insertion Force Factor vs Insertion Depth
# During insertion (part moves downward into socket, so socket rim moves from z=top_z down to stem_h)
# Penetration delta_z = top_z - z
# tan(alpha) = |dr/dz|
# Force multiplier = (tan(alpha) + mu) / (1 - mu * tan(alpha)) * (r(z) / D)  [normalized by beam deflection]
ax2 = axes[1]
ax2.set_title("Normalized Insertion Force vs Insertion Penetration", fontsize=11, fontweight='bold')

mu = 0.25 # Typical polymer-on-polymer friction

def calc_insertion_force(r_vals, z_vals):
    # numerical derivative dr/dz
    dr_dz = np.abs(np.gradient(r_vals, z_vals))
    tan_alpha = dr_dz
    # clamp tan_alpha to avoid division by zero or negative
    denom = np.maximum(0.1, 1.0 - mu * tan_alpha)
    multiplier = (tan_alpha + mu) / denom
    # deflection force is proportional to radial deflection r
    force = multiplier * (r_vals / D)
    return force

# Calculate insertion force along penetration from top_z down to stem_h
penetration = top_z - z_vals_sq
force_sq = calc_insertion_force(r_vals_sq, z_vals_sq)
force_rnd = calc_insertion_force(r_vals_rnd, z_vals_rnd)
force_circ = calc_insertion_force(r_vals_circ, z_vals_rnd)

ax2.plot(penetration, force_sq, 'r-', lw=2.5, label='Current: Squared-Off Triangle (High peak force & corner shock)')
ax2.plot(penetration, force_rnd, 'g-', lw=2.5, label='Option A: Elliptical Arc (Smooth, 65% lower peak insertion force)')
ax2.plot(penetration, force_circ, 'b--', lw=2.0, label='Option B: Circular Arc (Smooth low insertion force)')

ax2.set_xlabel("Insertion Penetration (mm) [Top of wall -> Shelf]", fontsize=10, fontweight='bold')
ax2.set_ylabel("Normalized Insertion Resistance Force (A.U.)", fontsize=10, fontweight='bold')
ax2.set_xlim(0, H + 0.1)
ax2.set_ylim(0, 4.5)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
out_fig = os.path.join(os.path.dirname(__file__), 'clip_profile_options_comparison.png')
plt.savefig(out_fig, dpi=200)
print(f"Saved {out_fig}")
