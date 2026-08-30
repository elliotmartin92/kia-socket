"""
testing/inspect_svg_slits.py
Inspect the exact slit coordinates in the master SVG file (part.svg) and the original dimensions.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import xml.etree.ElementTree as ET
import numpy as np

def inspect_svg():
    svg_path = os.path.join(os.path.dirname(__file__), '..', 'part.svg')
    print(f"Reading {svg_path}...")
    
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Let's search for paths, rects, lines in SVG
    SCALE = 0.26458333333333334
    X0 = 108.629
    Y0 = 108.629
    
    print("\nAll elements in part.svg:")
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        attrib = elem.attrib
        if tag in ['rect', 'path', 'circle', 'line', 'polygon', 'polyline']:
            elem_id = attrib.get('id', 'no-id')
            print(f"Tag: {tag}, id: {elem_id}")
            for k, v in attrib.items():
                if k in ['d', 'x', 'y', 'width', 'height', 'cx', 'cy', 'r']:
                    print(f"   {k}: {v[:80] if len(v) > 80 else v}")

if __name__ == '__main__':
    inspect_svg()
