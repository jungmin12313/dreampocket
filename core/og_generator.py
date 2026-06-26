import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_og_image(major: str, total_amount: int) -> bytes:
    """
    Generates a highly premium OpenGraph image based on a beautiful background template.
    Returns the image as bytes (PNG format).
    """
    # 1. Load the premium background template
    bg_path = os.path.join("static", "og_base_template.png")
    try:
        img = Image.open(bg_path).convert('RGB')
    except Exception:
        # Fallback to a solid dark navy color if image is missing
        img = Image.new('RGB', (1024, 1024), color='#0A1128')
    
    # Resize to standard OG 1200x630 if it's 1024x1024 (cropping center)
    if img.size != (1200, 630):
        # Scale to width 1200, then crop height 630
        ratio = 1200 / img.width
        new_h = int(img.height * ratio)
        img = img.resize((1200, new_h), Image.Resampling.LANCZOS)
        
        # Crop center
        top = (new_h - 630) // 2
        bottom = top + 630
        img = img.crop((0, top, 1200, bottom))

    draw = ImageDraw.Draw(img)
    
    # 2. Load the font
    font_path = os.path.join("static", "fonts", "NotoSansKR-Bold.otf")
    try:
        font_huge = ImageFont.truetype(font_path, 90)
        font_large = ImageFont.truetype(font_path, 60)
        font_medium = ImageFont.truetype(font_path, 40)
    except IOError:
        font_huge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # 3. Prepare texts
    amount_str = f"{total_amount:,}원" if total_amount > 0 else "N백만 원"
    major_display = major if major else "우리 학과"
    
    text1 = f"나만 몰랐던 {major_display} 장학금"
    text2 = f"총 {amount_str}"
    text3 = "드림포켓에서 내 조건으로 3초 만에 싹 다 찾기"
    
    # Helper to get width
    def get_text_width(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    w1 = get_text_width(text1, font_large)
    w2 = get_text_width(text2, font_huge)
    w3 = get_text_width(text3, font_medium)
    
    # 4. Draw texts with subtle shadow for high readability against complex backgrounds
    def draw_text_with_shadow(x, y, text, font, fill_color, shadow_color='#000000'):
        # soft shadow
        draw.text((x+3, y+3), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=fill_color)

    draw_text_with_shadow((1200 - w1) / 2, 160, text1, font_large, fill_color='#E2E8F0') # Slate-200
    draw_text_with_shadow((1200 - w2) / 2, 260, text2, font_huge, fill_color='#38BDF8')  # Sky-400 (Toss Blue style highlight)
    
    # Bottom subtle text
    draw_text_with_shadow((1200 - w3) / 2, 450, text3, font_medium, fill_color='#94A3B8') # Slate-400

    # Save to buffer
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    return img_buffer.getvalue()
