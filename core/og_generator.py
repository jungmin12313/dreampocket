import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_og_image(major: str, total_amount: int) -> bytes:
    """
    Generates a dynamic OpenGraph image for viral sharing.
    Returns the image as bytes (PNG format).
    """
    # Create a base image (Toss envelope style or simple clean gradient style)
    # Using a vibrant orange/amber gradient-like solid color for high visibility
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color='#FFFBEB') # Amber-50 bg

    draw = ImageDraw.Draw(img)

    # Draw a colored "envelope" box in the middle
    box_margin_x = 80
    box_margin_y = 60
    draw.rounded_rectangle(
        [(box_margin_x, box_margin_y), (width - box_margin_x, height - box_margin_y)],
        radius=40,
        fill='#F59E0B', # Amber-500
        outline='#D97706', # Amber-600
        width=4
    )
    
    # Try to load the downloaded font, fallback to default if not found
    font_path = os.path.join("static", "fonts", "NotoSansKR-Bold.otf")
    try:
        font_large = ImageFont.truetype(font_path, 80)
        font_medium = ImageFont.truetype(font_path, 55)
        font_small = ImageFont.truetype(font_path, 40)
    except IOError:
        # Fallback for systems without the specific font
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # Prepare text
    amount_str = f"{total_amount:,}원" if total_amount > 0 else "N백만 원"
    major_display = major if major else "우리 학과"
    
    text1 = "내 등록금 돌려줘요 💸"
    text2 = f"({major_display} 기준)"
    text3 = f"숨은 장학금 {amount_str} 뜸 ㄷㄷ"
    
    # Calculate text positions (centered)
    # In Pillow 10+, textbbox is used for text size
    def get_text_width(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    w1 = get_text_width(text1, font_medium)
    w2 = get_text_width(text2, font_small)
    w3 = get_text_width(text3, font_large)
    
    draw.text(((width - w1) / 2, 140), text1, font=font_medium, fill='#FFFFFF')
    draw.text(((width - w2) / 2, 260), text2, font=font_small, fill='#FEF3C7') # Amber-100
    
    # Text 3 with a slight drop shadow for emphasis
    x3 = (width - w3) / 2
    y3 = 380
    draw.text((x3+4, y3+4), text3, font=font_large, fill='#B45309') # Shadow (Amber-700)
    draw.text((x3, y3), text3, font=font_large, fill='#FFFFFF')

    # Add a small footer watermark
    footer = "3초만에 숨은 장학금 싹 다 긁어보기 | 드림포켓"
    w_f = get_text_width(footer, font_small)
    draw.text(((width - w_f) / 2, 510), footer, font=font_small, fill='#FDE68A') # Amber-200

    # Save to buffer
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    return img_buffer.getvalue()
