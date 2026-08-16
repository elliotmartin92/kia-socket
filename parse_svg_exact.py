"""
Parse the exact vector path from part.svg and compare it to a circle.
"""
import xml.etree.ElementTree as ET
import re
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# Extract the st2 path (outer perimeter) from part.svg
svg_path = 'part.svg'
with open(svg_path, 'r') as f:
    content = f.read()

# Let's find the d attribute of class="st2"
# <path class="st2" d="..." />
match = re.search(r'<path class="st2" d="([^"]+)"', content)
if not match:
    # Try finding any path with M180.7
    match = re.search(r'd="(M180\.7[^"]+)"', content)

d_str = match.group(1) if match else None
print("Found path d:", d_str[:60] if d_str else "None")

def parse_svg_path(d):
    """Parse SVG path into a list of (X, Y) points by evaluating lines and cubic beziers."""
    # Tokenize commands and numbers
    tokens = re.findall(r'([A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)', d)
    
    points = []
    curr_x, curr_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    
    i = 0
    cmd = None
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
        
        if cmd == 'M':
            curr_x = float(tokens[i])
            curr_y = float(tokens[i+1])
            start_x, start_y = curr_x, curr_y
            points.append((curr_x, curr_y))
            i += 2
            cmd = 'L' # Subsequent coordinates are lines
        elif cmd == 'm':
            curr_x += float(tokens[i])
            curr_y += float(tokens[i+1])
            start_x, start_y = curr_x, curr_y
            points.append((curr_x, curr_y))
            i += 2
            cmd = 'l'
        elif cmd == 'L':
            curr_x = float(tokens[i])
            curr_y = float(tokens[i+1])
            points.append((curr_x, curr_y))
            i += 2
        elif cmd == 'l':
            curr_x += float(tokens[i])
            curr_y += float(tokens[i+1])
            points.append((curr_x, curr_y))
            i += 2
        elif cmd == 'H':
            curr_x = float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'h':
            curr_x += float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'V':
            curr_y = float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'v':
            curr_y += float(tokens[i])
            points.append((curr_x, curr_y))
            i += 1
        elif cmd == 'C':
            x1 = float(tokens[i])
            y1 = float(tokens[i+1])
            x2 = float(tokens[i+2])
            y2 = float(tokens[i+3])
            x3 = float(tokens[i+4])
            y3 = float(tokens[i+5])
            # Evaluate cubic bezier in 20 steps
            for t_step in np.linspace(0.05, 1.0, 20):
                bx = (1-t_step)**3 * curr_x + 3*(1-t_step)**2 * t_step * x1 + 3*(1-t_step)*t_step**2 * x2 + t_step**3 * x3
                by = (1-t_step)**3 * curr_y + 3*(1-t_step)**2 * t_step * y1 + 3*(1-t_step)*t_step**2 * y2 + t_step**3 * y3
                points.append((bx, by))
            curr_x, curr_y = x3, y3
            i += 6
        elif cmd == 'c':
            x1 = curr_x + float(tokens[i])
            y1 = curr_y + float(tokens[i+1])
            x2 = curr_x + float(tokens[i+2])
            y2 = curr_y + float(tokens[i+3])
            x3 = curr_x + float(tokens[i+4])
            y3 = curr_y + float(tokens[i+5])
            for t_step in np.linspace(0.05, 1.0, 20):
                bx = (1-t_step)**3 * curr_x + 3*(1-t_step)**2 * t_step * x1 + 3*(1-t_step)*t_step**2 * x2 + t_step**3 * x3
                by = (1-t_step)**3 * curr_y + 3*(1-t_step)**2 * t_step * y1 + 3*(1-t_step)*t_step**2 * y2 + t_step**3 * y3
                points.append((bx, by))
            curr_x, curr_y = x3, y3
            i += 6
        elif cmd in ('Z', 'z'):
            points.append((start_x, start_y))
            cmd = None
        else:
            i += 1
            
    return np.array(points)

pts = parse_svg_path(d_str)
print(f"Parsed {len(pts)} points from SVG outer perimeter!")

# Let's transform points to mm coordinates centered at X0=128.65, Y0=124.2
SCALE = 8.22 / 23.5  # ~0.349787 mm/unit
X0 = 128.65
Y0 = 124.2

pts_mm = np.zeros_like(pts)
pts_mm[:, 0] = (pts[:, 0] - X0) * SCALE
pts_mm[:, 1] = -(pts[:, 1] - Y0) * SCALE # Invert Y so +Y is up

# Plot comparison between actual SVG path and the circular approximation
fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
ax.plot(pts_mm[:, 0], pts_mm[:, 1], 'b-', linewidth=2.5, label='Actual SVG Outer Perimeter (Non-circular!)')

# Overlay circle for comparison
theta = np.linspace(0, 2*np.pi, 200)
r_circle = 38.5 / 2.0
ax.plot(r_circle * np.cos(theta), r_circle * np.sin(theta), 'r--', linewidth=1.5, label='Previous Circle Approximation (Incorrect)')

ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', fontsize=10)
ax.set_title('Comparison: Actual Vector Path from SVG vs. Circle', fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')

plt.savefig('path_comparison.png', dpi=150)
print("Saved path_comparison.png")
