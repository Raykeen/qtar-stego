from PIL import Image, ImageDraw


BKG_COLOR = (0, 0, 0, 128)
TXT_COLOR = (255, 255, 255, 255)
PADDING = 10
COORDS = (0, 0)


def stamp_image(img, text):
    img = img.convert('RGBA')
    x, y = COORDS
    stamp = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(stamp)
    text_size_x, text_size_y = draw.textsize(text)
    draw.rectangle((x, y, x + text_size_x + 2 * PADDING, y + text_size_y + 2 * PADDING), BKG_COLOR, None)
    draw.text((PADDING, PADDING), text, fill=TXT_COLOR)
    return Image.alpha_composite(img, stamp)