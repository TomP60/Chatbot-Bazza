from PIL import Image
import os

SOURCE_DIR = "assets"  # or wherever your PNGs are
TARGET_WIDTH = 150      # pixels
OUTPUT_FORMAT = "JPEG"

for filename in os.listdir(SOURCE_DIR):
    if filename.lower().endswith(".png"):
        full_path = os.path.join(SOURCE_DIR, filename)
        img = Image.open(full_path)

        # Maintain aspect ratio
        w_percent = TARGET_WIDTH / float(img.size[0])
        h_size = int(float(img.size[1]) * w_percent)
        resized_img = img.resize((TARGET_WIDTH, h_size), Image.LANCZOS)

        # Convert and save as .jpg
        output_name = os.path.splitext(filename)[0] + "_thumb.jpg"
        resized_img = resized_img.convert("RGB")  # JPEG doesn't support transparency
        resized_img.save(os.path.join(SOURCE_DIR, output_name), OUTPUT_FORMAT)

        print(f"✅ Converted {filename} → {output_name}")
