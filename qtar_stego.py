from PIL import Image
from numpy import array
from ImageQTNode import ImageQTNode
from ImageQT import ImageQT
image = Image.open("images/lenna.jpg")

image_channels = dict()
image_channels['r'], image_channels['g'], image_channels['b'] = image.split()

rect = [0, 0, 128, 128]

root_node = ImageQTNode(None, rect, array(image_channels['r']), 20, 8, 128)
qtree = ImageQT(root_node)

for image_node in qtree.leaves:
    x0, y0, x1, y1 = image_node.rect
    region = image_node.image[x0:x1, y0:y1]
    img_region = Image.fromarray(region)
    print(img_region)


# def qtar(cover_image, message, threshold = 0.6, max_block_size = 1024, min_block_size = 8):

#print(array(image.split()[0]))
