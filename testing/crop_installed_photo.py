"""
testing/crop_installed_photo.py
Crops and enhances the bracket region of the installed brass part photo to inspect the floor and bracket interior.
"""
import os, sys
from PIL import Image

photo_path = os.path.join(os.path.dirname(__file__), 'installed_brass_part_photo.jpg')
if os.path.exists(photo_path):
    img = Image.open(photo_path)
    w, h = img.size
    print(f"Photo size: {w}x{h}")
    
    # Crop central bracket region
    # Center is approximately (w/2, h/2)
    crop_box = (int(w * 0.20), int(h * 0.30), int(w * 0.80), int(h * 0.85))
    cropped = img.crop(crop_box)
    cropped.save(os.path.join(os.path.dirname(__file__), 'cropped_bracket_photo.jpg'))
    print("Saved cropped_bracket_photo.jpg")
