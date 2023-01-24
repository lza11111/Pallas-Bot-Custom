from io import BytesIO
from PIL import Image, ImageFont
from pathlib import Path
from pilmoji import Pilmoji

font_path = Path(__file__).parent.parent.parent.parent.joinpath("data").joinpath("font")
font_semibold = str(font_path.joinpath("PingFang-Medium.ttf"))

def to_image(content: str):
    content_font = ImageFont.truetype(font_semibold, 24)
    content_text_x, content_text_y = content_font.getsize_multiline(content, spacing=15)
    content_bg = Image.new("RGB", (content_text_x + 20, content_text_y + 15), "#FFFFFF")
    draw = Pilmoji(content_bg)
    draw.text((10, 10), content, "#181818", content_font, spacing=15)
    image_bytes = BytesIO()
    content_bg.save(image_bytes, 'JPEG')
    return image_bytes