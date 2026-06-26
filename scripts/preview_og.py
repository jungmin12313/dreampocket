import sys
import os

# Add parent directory to path so we can import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.og_generator import generate_og_image

output_path = r"C:\Users\user\.gemini\antigravity\brain\293b0bfc-b82f-46d6-a677-88c99fc00ca1\sample_og.png"

img_bytes = generate_og_image("경영학과", 3500000)

with open(output_path, "wb") as f:
    f.write(img_bytes)

print(f"Saved preview to {output_path}")
