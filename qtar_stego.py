from PIL import Image
from numpy import array
from quadtree import Node, QuadTree
image = Image.open("images/lenna.jpg")

# class ImageNode(Node):
#     def __init__(self, parent, rect, image):
#         super().__init__(parent, rect)
#         self.image = image;
#
#     def getinstance(self, rect):
#         return CoverImageNode(self, rect, image)
#
#     def spans_feature(self, rect):
#         return False
# def qtar(cover_image, message, threshold = 0.6, max_block_size = 1024, min_block_size = 8):

print(array(image))
