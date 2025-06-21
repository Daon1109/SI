
from PIL import Image
import os

input_folder = "C:/Coding/ssipduck_intelligence/SI_DB/test_rcmd/og"
output_folder = "C:/Coding/ssipduck_intelligence/SI_DB/test_rcmd/Violet_Evergarden"

os.makedirs(output_folder, exist_ok=True)


for filename in os.listdir(input_folder):
    if filename.lower().endswith(".webp"):
        path = os.path.join(input_folder, filename)
        img = Image.open(path).convert("RGB")
        new_name = os.path.splitext(filename)[0] + ".jpg"
        img.save(os.path.join(output_folder, new_name), "JPEG")
