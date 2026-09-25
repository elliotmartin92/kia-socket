"""
testing/analyze_photo_measurements.py
Analyze pixels in testing/right_bracket_brass_crop.png to measure:
1. Inner width between bracket walls
2. Width and position of the broken half moon stub
3. Gap between the brass U-bridge and the pinching leaves
"""
import os, sys
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

img_path = os.path.join(os.path.dirname(__file__), 'right_bracket_brass_crop.png')
img = Image.open(img_path)
w, h = img.size
print(f"Image shape: {w} x {h}")

plt.figure(figsize=(10, 14), dpi=150)
plt.imshow(img)
plt.title(f"Right Bracket Photo (Shape: {w}x{h})")
plt.grid(True, color='cyan', alpha=0.5, linestyle=':')
plt.tight_layout()
plt.savefig('testing/photo_grid_overlay.png')
print("Saved testing/photo_grid_overlay.png")
