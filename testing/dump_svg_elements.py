"""
Inspect all elements and paths in part.svg in complete detail.
"""
import xml.etree.ElementTree as ET
import re

with open('part.svg', 'r') as f:
    text = f.read()

# Let's find all path, polyline, line, polygon, circle, rect tags
elements = re.findall(r'<((?:path|polyline|line|polygon|circle|rect)[^>]+)>', text)
print(f"Total elements found: {len(elements)}\n")

for idx, el in enumerate(elements):
    # Extract tag name and attributes
    tag = el.split()[0]
    cls = re.search(r'class="([^"]+)"', el)
    cls_str = cls.group(1) if cls else ""
    d = re.search(r'd="([^"]+)"', el)
    pts = re.search(r'points="([^"]+)"', el)
    x1 = re.search(r'x1="([^"]+)"', el)
    
    print(f"--- Element {idx+1}: <{tag} class='{cls_str}'> ---")
    if d:
        print(f"  d: {d.group(1)}")
    if pts:
        print(f"  points: {pts.group(1)}")
    if x1:
        x2 = re.search(r'x2="([^"]+)"', el).group(1)
        y1 = re.search(r'y1="([^"]+)"', el).group(1)
        y2 = re.search(r'y2="([^"]+)"', el).group(1)
        print(f"  line: ({x1.group(1)}, {y1}) -> ({x2}, {y2})")
    print()
