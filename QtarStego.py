import sys
from PIL import Image
from numpy import array, zeros, uint8
from math import log2, pow
from scipy.fftpack import dct, idct
from ImageQTNode import *
from ImageQT import *
from QuantizationMatrix import *


class QtarStego:
    def __init__(self, homogeneity_threshold=0.5, min_block_size=2, max_block_size=512):
        self.homogeneity_threshold = homogeneity_threshold
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.image = Image.new("RGB", (512, 512), "white")
        self.size = 512
        self.image_chs = {'r': [], 'g': [], 'b': []}
        self.qt_regions_chs = {'r': [], 'g': [], 'b': []}
        self.img_dct_chs = {'r': [], 'g': [], 'b': []}
        self.stego_img_chs = {'r': [], 'g': [], 'b': []}
        self.aregions_chs = {'r': [], 'g': [], 'b': []}

    def embed(self, image, message=None):
        self.image = image
        self.size = int(pow(2, int(log2(image.width & image.height))))

        self.image_chs = self._prepare_image(self.size)
        for channel, image_ch in self.image_chs.items():
            self._embed_in_channel(channel, image_ch, message)

    def _embed_in_channel(self, channel, image_ch, message=None):
        root_node = ImageQTNode(None,
                                [0, 0, self.size, self.size],
                                image_ch,
                                self.homogeneity_threshold,
                                self.min_block_size,
                                self.max_block_size & self.size)
        qt_regions = ImageQT(root_node).leaves
        img_dct = self._dct_2d(qt_regions)
        dct_regions = MatrixRegion.new_matrix_regions(qt_regions, img_dct)
        aregions = self._adapt_regions(dct_regions)

        for aregion in aregions:
            aregion.each(lambda value, x, y: 0)

        stego_img = self._dct_2d(dct_regions, True)

        self.qt_regions_chs[channel] = qt_regions
        self.img_dct_chs[channel] = img_dct
        self.aregions_chs[channel] = aregions
        self.stego_img_chs[channel] = stego_img

    def _prepare_image(self, size):
        cropped = self.image.crop((0, 0, size, size))
        image_channels = dict()
        image_channel_arrays = dict()
        image_channels['r'], image_channels['g'], image_channels['b'] = cropped.split()
        for channel in image_channels:
            image_channel_arrays[channel] = array(image_channels[channel])
        return image_channel_arrays

    def _dct_2d(self, regions, inverse=False):
        result = zeros((self.size, self.size))
        for region in regions:
            rect = region.rect
            x0, y0, x1, y1 = rect
            region = region.get_region()
            if inverse:
                region_dct = idct(idct(region.T, norm='ortho').T, norm='ortho')
            else:
                region_dct = dct(dct(region, norm='ortho').T, norm='ortho').T
            for x in range(x0, x1):
                for y in range(y0, y1):
                    i = x - x0
                    j = y - y0
                    result[x][y] = region_dct[i][j]
        return result

    def _adapt_regions(self, regions):
        aregions_indexes = self._find_adaptive_regions(regions)
        return self._get_adaptive_regions(aregions_indexes, regions)

    def _find_adaptive_regions(self, regions):
        aregions_indexes = list()
        for region in regions:
            origin_region = region.get_region()
            quantization_matrix = QuantizationMatrix.get_matrix(region.size)
            quantized = uint8(origin_region / quantization_matrix)
            if quantized[-1, -1] != 0:
                aregions_indexes.append(region.size)
                continue
            for xy in range(0, region.size):
                aregion = quantized[xy:region.size][xy:region.size]
                if not aregion.any():
                    aregions_indexes.append(xy)
                    break
        return aregions_indexes

    def _get_adaptive_regions(self, aregions_indexes, origin_regions):
        aregions = list()
        for i in range(0, len(origin_regions)):
            x0, y0, x1, y1 = origin_regions[i].rect
            new_x0 = x0 + aregions_indexes[i]
            new_y0 = y0 + aregions_indexes[i]
            new_region = MatrixRegion([new_x0, new_y0, x1, y1], origin_regions[i].matrix)
            aregions.append(new_region)
        return aregions

    @staticmethod
    def convert_chs_to_image(matrix_chs):
        image_chs = {channel: Image.fromarray(image_ch).convert('L')
                     for channel, image_ch in matrix_chs.items()}
        result_image = Image.merge("RGB", (image_chs['r'], image_chs['g'], image_chs['b']))
        return result_image

    def get_container_image(self):
        return self.convert_chs_to_image(self.image_chs)

    def get_qt_image(self):
        matrix_chs = {channel: MatrixRegion.get_matrix_with_borders(qtree_regions, only_right_bottom=True)
                     for channel, qtree_regions in self.qt_regions_chs.items()}
        return self.convert_chs_to_image(matrix_chs)

    def get_dct_image(self):
        return self.convert_chs_to_image(self.img_dct_chs)

    def get_ar_image(self):
        max_dct_value = max([image_ch.max() for image_ch in self.img_dct_chs.values()])
        matrix_chs = {channel: MatrixRegion.get_matrix_with_borders(aregions, max_dct_value)
                      for channel, aregions in self.aregions_chs.items()}
        return self.convert_chs_to_image(matrix_chs)

    def get_stego_image(self):
        return self.convert_chs_to_image(self.stego_img_chs)


def main(argv):
    if len(argv) < 2:
        print("qtarstego [image path]")
        return

    img = Image.open(argv[1])
    qtar = QtarStego()
    qtar.embed(img)
    qtar.get_container_image().show()
    qtar.get_qt_image().show()
    qtar.get_dct_image().show()
    qtar.get_ar_image().show()
    qtar.get_stego_image().show()
    # qtar.show_stego()


if __name__ == "__main__":
    main(sys.argv)
