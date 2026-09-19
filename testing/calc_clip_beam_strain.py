import numpy as np

# Cantilever beam strain calculation:
# epsilon = 1.5 * t * delta / L^2
# Where:
# t = beam thickness (1.20mm)
# delta = deflection (hook depth)
# L = slot depth (cantilever length)

def calc_strain(t, delta, L):
    return 1.5 * t * delta / (L ** 2)

t = 1.20
delta_current = 2.49
L_current = 3.70

print(f"Current Beam Strain: {calc_strain(t, delta_current, L_current) * 100:.1f}%")

# What if L is deeper? e.g. down near base floor (Z = 1.0mm -> L = 5.77mm)
L_deep = 6.77 - 1.20  # 5.57mm
delta_faced = 2.39
print(f"Deep Slot (L={L_deep:.2f}mm) with delta={delta_faced:.2f}mm: Strain = {calc_strain(t, delta_faced, L_deep) * 100:.1f}%")

# What if beam thickness is tapered or thinned to 0.90mm or 1.00mm?
print(f"Thin Beam (t=1.00mm, L={L_deep:.2f}mm): Strain = {calc_strain(1.00, delta_faced, L_deep) * 100:.1f}%")
print(f"Thin Beam (t=0.85mm, L={L_deep:.2f}mm): Strain = {calc_strain(0.85, delta_faced, L_deep) * 100:.1f}%")

# What about a root stress-relief radius (fillet/hole) at slot bottom?
