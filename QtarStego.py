import sys
from PIL import Image
from numpy import array
from math import log2, pow
from ImageQTNode import ImageQTNode
from ImageQT import ImageQT
from AdaptiveRegions import AdaptiveRegions


class QtarStego:
    def __init__(self, image, homogeneity_threshold=0.5, min_block_size=2, max_block_size=512):
        self.image = image
        self.size = int(pow(2, int(log2(image.width & image.height))))
        self.image_channels = self.prepare_image(self.size)
        self.root_node = ImageQTNode(None,
                                     [0, 0, self.size, self.size],
                                     self.image_channels['r'],
                                     homogeneity_threshold,
                                     min_block_size,
                                     max_block_size & self.size)
        self.qtree = ImageQT(self.root_node)
        self.stego_regions = AdaptiveRegions(self.qtree)

    def prepare_image(self, size):
        cropped = self.image.crop((0, 0, size, size))
        image_channels = dict()
        image_channel_arrays = dict()
        image_channels['r'], image_channels['g'], image_channels['b'] = cropped.split()
        for channel in image_channels:
            image_channel_arrays[channel] = array(image_channels[channel])
        return image_channel_arrays

    def show_qt_stage(self):
        Image.fromarray(self.qtree.image_with_qt_borders()).show()


def main(argv):
    if len(argv) < 2:
        print("qtarstego [image path]")
        return

    img = Image.open(argv[1])
    qtar = QtarStego(img)
    qtar.show_qt_stage()


if __name__ == "__main__":
    main(sys.argv)

