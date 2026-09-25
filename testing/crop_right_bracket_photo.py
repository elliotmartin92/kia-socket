import os, sys
from PIL import Image

img_path = 'testing/installed_brass_part_photo.jpg'
im = Image.open(img_path)
w, h = im.size
print(f"Original image size: {w} x {h}")

# The photo is oriented with top tab at the top
# Right bracket set is around X in [0.5, 0.85] * w, Y in [0.3, 0.85] * h
crop_box = (int(w * 0.48), int(h * 0.30), int(w * 0.80), int(h * 0.75))
cropped = im.crop(crop_box)
out_crop = 'testing/right_bracket_brass_crop.png'
cropped.save(out_crop)
print(f"Saved cropped view of right bracket set to {out_crop}")
