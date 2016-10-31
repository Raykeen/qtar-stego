from PIL import Image
from numpy import array
from ImageQTNode import ImageQTNode
from ImageQT import ImageQT
img = Image.open("images/lenna.png")


def prepare_image(image, size):
    cropped = image.crop((0, 0, size, size))
    image_channels = dict()
    image_channel_arrays = dict()
    image_channels['r'], image_channels['g'], image_channels['b'] = cropped.split()
    for channel in image_channels:
        image_channel_arrays[channel] = array(image_channels[channel])
    return image_channel_arrays

rect = [0, 0, 512, 512]
root_node = ImageQTNode(None, rect, prepare_image(img, 512)['r'], 150, 2, 512)
qtree = ImageQT(root_node)
Image.fromarray(qtree.image_with_qt_borders()).show()
