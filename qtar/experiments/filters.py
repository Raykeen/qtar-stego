from io import BytesIO
from PIL import Image
from PIL.ImageFilter import MedianFilter, UnsharpMask, GaussianBlur


def none(image):
    return image


def jpeg(image, quality):
    buffer = BytesIO()
    image.save(buffer, "JPEG", quality=quality)
    jpeg_image = Image.open(buffer)
    return jpeg_image


def jpeg90(image):
    return jpeg(image, 90)


def jpeg60(image):
    return jpeg(image, 60)


def median(image, size=3):
    mfilter = MedianFilter(size)
    return image.filter(mfilter)


def unsharp(image, radius=2, percent=150, threshold=3):
    usfilter = UnsharpMask(radius, percent, threshold)
    return image.filter(usfilter)


def blur(image, radius=2):
    bfilter = GaussianBlur(radius=radius)
    return image.filter(bfilter)


filters = [
    ("none", none),
    ("jpeg 90%", jpeg90),
    ("jpeg 60%", jpeg60),
    ("median size=3", median),
    ("unsharp radius=2, percent=150, threshold=3", unsharp),
    ("gaussian blur radius=2", blur)
]
