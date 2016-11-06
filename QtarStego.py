import sys
from PIL import Image
from numpy import array, zeros, uint8
from math import log2, pow
from scipy.fftpack import dct, idct
from ImageQTNode import *
from ImageQT import *
from AdaptiveRegions import *


class QtarStego:
    def __init__(self, homogeneity_threshold=0.4, min_block_size=8, max_block_size=512, quant_power=0.2, ch_scale=4.37):
        self.homogeneity_threshold = homogeneity_threshold
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.quant_power = quant_power
        self.ch_scale = ch_scale
        self.image = Image.new("RGB", (512, 512), "white")
        self.size = 512
        self.key_data = {'wm_size': None, 'aregions-indexes': {'r': [], 'g': [], 'b': []}}
        self.image_chs = {'r': [], 'g': [], 'b': []}
        self.qt_regions_chs = {'r': [], 'g': [], 'b': []}
        self.img_dct_chs = {'r': [], 'g': [], 'b': []}
        self.stego_img_chs = {'r': [], 'g': [], 'b': []}
        self.aregions_chs = {'r': [], 'g': [], 'b': []}
        self.watermark_chs = {'r': [], 'g': [], 'b': []}

    def embed(self, image, watermark=None):
        self.image = image
        self.size = int(pow(2, int(log2(image.width & image.height))))
        self.image_chs = self._prepare_image(image, self.size)
        self.watermark_chs = self._prepare_image(watermark, 256)
        self.key_data['wm_size'] = self.watermark_chs['r'].shape
        for channel, image_ch in self.image_chs.items():
            self.key_data['aregions-indexes'][channel] = self._embed_in_channel(channel, image_ch, self.watermark_chs[channel])

        return self.key_data

    def extract(self, stego_image, key_data):
        self.key_data = key_data
        self.size = stego_image.width & stego_image.height
        self.stego_img_chs = self._prepare_image(stego_image)
        for channel, stego_image_ch in self.stego_img_chs.items():
            self.watermark_chs[channel] = self._extract_from_channel(channel, stego_image_ch, self.key_data)

        return self.get_wm()

    def _embed_in_channel(self, channel, image_ch, watermark_ch=None):
        root_node = ImageQTNode(None,
                                [0, 0, self.size, self.size],
                                image_ch,
                                self.homogeneity_threshold,
                                self.min_block_size,
                                self.max_block_size & self.size)
        qt_regions = ImageQT(root_node).leaves
        img_dct = self._dct_2d(qt_regions)
        dct_regions = MatrixRegion.new_matrix_regions(qt_regions, img_dct)
        adaptive_regions = AdaptiveRegions(dct_regions, self.quant_power)

        self._embed_in_aregions(adaptive_regions.regions, watermark_ch)

        stego_img = self._dct_2d(dct_regions, True)

        self.qt_regions_chs[channel] = qt_regions
        self.img_dct_chs[channel] = img_dct
        self.aregions_chs[channel] = adaptive_regions.regions
        self.stego_img_chs[channel] = stego_img

        return adaptive_regions.indexes

    def _extract_from_channel(self, channel, stego_image_ch, key_data):
        aregions_indexes = key_data['aregions-indexes'][channel]
        wm_size = key_data['wm_size']

        root_node = ImageQTNode(None,
                                [0, 0, self.size, self.size],
                                stego_image_ch,
                                self.homogeneity_threshold,
                                self.min_block_size,
                                self.max_block_size & self.size)
        qt_regions = ImageQT(root_node).leaves
        img_dct = self._dct_2d(qt_regions)
        dct_regions = MatrixRegion.new_matrix_regions(qt_regions, img_dct)
        #adaptive_regions = AdaptiveRegions(dct_regions, self.quant_power, aregions_indexes)

        #watermark_ch = self._extract_from_aregions(adaptive_regions.regions, wm_size)

        self.qt_regions_chs[channel] = qt_regions
        self.img_dct_chs[channel] = img_dct
        #self.aregions_chs[channel] = adaptive_regions.regions
        #self.watermark_chs[channel] = watermark_ch

        #return watermark_ch
        return stego_image_ch

    def _embed_in_aregions(self, aregions, watermark_ch):
        i, j = 0, 0
        imax, jmax = watermark_ch.shape

        for aregion in aregions:
            x0, y0, x1, y1 = aregion.rect
            for y in range(y0, y1):
                for x in range(x0, x1):
                    aregion.matrix[x, y] = watermark_ch[i, j] / 255 * self.ch_scale
                    i += (j + 1) // jmax
                    j = (j + 1) % jmax
                    if i >= imax:
                        break
                if i >= imax:
                    break
            if i >= imax:
                break

    def _extract_from_aregions(self, aregions, wm_size):
        i, j = 0, 0
        imax, jmax = wm_size
        watermark_ch = zeros(wm_size)

        for aregion in aregions:
            x0, y0, x1, y1 = aregion.rect
            for y in range(y0, y1):
                for x in range(x0, x1):
                    watermark_ch[i, j] = aregion.matrix[x, y] * 255 / self.ch_scale
                    i += (j + 1) // jmax
                    j = (j + 1) % jmax
                    if i >= imax:
                        break
                if i >= imax:
                    break
            if i >= imax:
                break

        return watermark_ch

    def _prepare_image(self, image, size=None):
        if size:
            cropped = image.crop((0, 0, size, size))
        else:
            cropped = image
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

    def get_wm(self):
        return self.convert_chs_to_image(self.watermark_chs)


def main(argv):
    img = Image.open("images\Lenna.png")
    watermark = Image.open("images\Garold.jpg")
    qtar = QtarStego()
    key_data = qtar.embed(img, watermark)
    #qtar.get_container_image().show()
    qtar.get_qt_image().show()
    qtar.get_dct_image().show()
    qtar.get_ar_image().show()
    qtar.get_stego_image().show()
    qtar.get_wm().show()

    qtar.extract(qtar.get_stego_image(), key_data)
    qtar.get_qt_image().show()
    # qtar.show_stego()


if __name__ == "__main__":
    main(sys.argv)
