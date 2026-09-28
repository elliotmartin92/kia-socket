"""
testing/crop_user_image.py
Crop and zoom into the right window of the user's screenshot to see the slicer preview clearly.
"""

from PIL import Image

img = Image.open('C:/Users/Elliot/.gemini/antigravity/brain/63a3b1f9-6945-492b-b74d-04fba01ad21e/.user_uploaded/media_1790621315103.png')
w, h = img.size
print(f"Original size: {w}x{h}")

# The right window is from x ~ 0.55*w to w
crop_slicer = img.crop((int(0.55 * w), 0, w, h))
crop_slicer.save('testing/slicer_window.png')

# Also crop tightly around the 3D model in the slicer
# In the right window, the model is in the middle-right area
crop_model = img.crop((int(0.70 * w), int(0.10 * h), int(0.90 * w), int(0.60 * h)))
crop_model.save('testing/slicer_model_zoom.png')

# Also crop the slicer settings and legend
crop_legend = img.crop((int(0.88 * w), int(0.10 * h), int(0.99 * w), int(0.50 * h)))
crop_legend.save('testing/slicer_legend.png')

print("Saved crops in testing/")
