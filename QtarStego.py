import sys
import argparse
from PIL import Image
from PIL import ImageChops
from numpy import array, zeros, append
from math import log2, pow
from scipy.fftpack import dct, idct
from itertools import islice
from ImageQT import *
from AdaptiveRegions import *
from metrics import psnr


class QtarStego:
    def __init__(self,
                 homogeneity_threshold=(0.4),
                 min_block_size=8,
                 max_block_size=512,
                 quant_power=0.2,
                 ch_scale=4.37,
                 offset=None):
        self.homogeneity_threshold = homogeneity_threshold
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.quant_power = quant_power
        self.ch_scale = ch_scale
        self.offset = offset
        self.image = Image.new("RGB", (512, 512), "white")
        self.size = 512
        self.key_data = {'wm_shape': None, 'aregions': {'r': [], 'g': [], 'b': []}}
        self.image_chs = {'r': [], 'g': [], 'b': []}
        self.qt_regions_chs = {'r': [], 'g': [], 'b': []}
        self.dct_regions_chs = {'r': [], 'g': [], 'b': []}
        self.stego_img_chs = {'r': [], 'g': [], 'b': []}
        self.aregions_chs = {'r': [], 'g': [], 'b': []}
        self.watermark_chs = {'r': [], 'g': [], 'b': []}

    def embed(self, image, watermark=None):
        self.image = image
        self.size = int(pow(2, int(log2(min(image.width, image.height)))))
        self.image_chs = self._prepare_image(image, self.size, self.offset)
        sized_wm = watermark.copy()
        sized_wm.thumbnail((300,300))
        self.watermark_chs = self._prepare_image(sized_wm)
        self.key_data['wm_shape'] = self.watermark_chs['r'].shape
        for channel, image_ch in self.image_chs.items():
            self.key_data['aregions'][channel] = self._embed_in_channel(channel, image_ch, self.watermark_chs[channel])

        return self.key_data

    def extract(self, stego_image, key_data):
        self.key_data = key_data
        self.size = min(stego_image.width, stego_image.height)
        self.stego_img_chs = self._prepare_image(stego_image, offset=self.offset)
        for channel, stego_image_ch in self.stego_img_chs.items():
            self.watermark_chs[channel] = self._extract_from_channel(channel, stego_image_ch, self.key_data)

        return self.get_wm()

    def _embed_in_channel(self, channel, image_ch, watermark_ch=None):
        qt_regions = ImageQT(image_ch,
                             self.min_block_size,
                             min(self.max_block_size, self.size),
                             self.homogeneity_threshold)
        dct_regions = self._dct_2d(qt_regions)
        adaptive_regions = AdaptiveRegions(dct_regions, self.quant_power)
        self._embed_in_aregions(adaptive_regions.regions, watermark_ch)
        stego_img = self._dct_2d(dct_regions, True)

        self.qt_regions_chs[channel] = qt_regions
        self.dct_regions_chs[channel] = dct_regions
        self.aregions_chs[channel] = adaptive_regions.regions
        self.stego_img_chs[channel] = stego_img.matrix

        return adaptive_regions

    def _extract_from_channel(self, channel, stego_image_ch, key_data):
        aregions = key_data['aregions'][channel]
        wm_shape = key_data['wm_shape']
        qt_regions = MatrixRegions(aregions.base_regions.rects, stego_image_ch)
        dct_regions = self._dct_2d(qt_regions)
        adaptive_regions = AdaptiveRegions(dct_regions, self.quant_power, aregions.indexes)

        watermark_ch = self._extract_from_aregions(adaptive_regions.regions, wm_shape)

        self.qt_regions_chs[channel] = qt_regions
        self.dct_regions_chs[channel] = dct_regions
        self.aregions_chs[channel] = adaptive_regions.regions
        self.watermark_chs[channel] = watermark_ch

        return watermark_ch

    def _embed_in_aregions(self, aregions, watermark_ch):
        wm_iter = watermark_ch.flat
        stop = False
        for i in range(0, aregions.count):
            aregion = aregions[i]
            size = aregion.size
            shape = aregion.shape
            flat_stego_region = array(list(islice(wm_iter, size)))
            if flat_stego_region.size < size:
                flat_aregion = list(aregion.flat)
                flat_stego_region = append(flat_stego_region, flat_aregion[flat_stego_region.size:size])
                stop = True
            stego_region = flat_stego_region.reshape(shape)
            aregions[i] = stego_region / 255 * self.ch_scale
            if stop: return

    def _extract_from_aregions(self, aregions, wm_shape):
        flat_stego_region = array([])
        wm_size = wm_shape[0] * wm_shape[1]
        for i in range(0, aregions.count):
            aregion = aregions[i]
            flat_aregion = list(aregion.flat)
            flat_stego_region = append(flat_stego_region, flat_aregion)
            if flat_stego_region.size >= wm_size:
                break
        watermark_ch = flat_stego_region[0:wm_size].reshape(wm_shape)
        return watermark_ch * 255 / self.ch_scale

    def _prepare_image(self, image, size=None, offset=None):
        prepared = image

        if size:
            prepared = prepared.crop((0, 0, size, size))
        if offset:
            x, y = offset
            prepared = ImageChops.offset(prepared, x, y)

        image_channels = dict()
        image_channel_arrays = dict()
        image_channels['r'], image_channels['g'], image_channels['b'] = prepared.split()
        for channel in image_channels:
            image_channel_arrays[channel] = array(image_channels[channel])
        return image_channel_arrays

    def _dct_2d(self, regions, inverse=False):
        result_mx = zeros((self.size, self.size))
        dct_regions = MatrixRegions(regions.rects, result_mx)
        i = 0
        for region in regions:
            if inverse:
                region_dct = idct(idct(region.T, norm='ortho').T, norm='ortho')
            else:
                region_dct = dct(dct(region, norm='ortho').T, norm='ortho').T
            dct_regions[i] = region_dct
            i += 1
        return dct_regions

    @staticmethod
    def convert_chs_to_image(matrix_chs, offset=None):
        image_chs = {channel: Image.fromarray(image_ch).convert('L')
                     for channel, image_ch in matrix_chs.items()}
        result_image = Image.merge("RGB", (image_chs['r'], image_chs['g'], image_chs['b']))
        if offset:
            x, y = offset
            result_image = ImageChops.offset(result_image, -x, -y)

        return result_image

    def get_container_image(self):
        return self.convert_chs_to_image(self.image_chs, self.offset)

    def get_qt_image(self):
        matrix_chs = {channel: qtree_regions.get_matrix_with_borders(only_right_bottom=True)
                     for channel, qtree_regions in self.qt_regions_chs.items()}
        return self.convert_chs_to_image(matrix_chs, self.offset)

    def get_dct_image(self):
        matrix_chs = {channel: dct_regions.matrix * 10
                      for channel, dct_regions in self.dct_regions_chs.items()}
        return self.convert_chs_to_image(matrix_chs, self.offset)

    def get_ar_image(self):
        max_dct_value = max([dct_regions.matrix.max() for dct_regions in self.dct_regions_chs.values()])
        matrix_chs = {channel: aregions.get_matrix_with_borders(value=max_dct_value)
                      for channel, aregions in self.aregions_chs.items()}
        return self.convert_chs_to_image(matrix_chs, self.offset)

    def get_stego_image(self):
        return self.convert_chs_to_image(self.stego_img_chs, self.offset)

    def get_wm(self):
        return self.convert_chs_to_image(self.watermark_chs)


def main(argv):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('container', type=str,
                           help='container image')
    argparser.add_argument('watermark', type=str,
                           help='image to embed into container')
    argparser.add_argument('-t', metavar='threshold', type=float, nargs='+', default=0.4,
                           help='homogeneity thresholds for different brightness levels   float[0, 1])')
    argparser.add_argument('--min', metavar='min_block_size', type=int, default=8,
                           help='min block size   int[2, max_block_size], square of 2')
    argparser.add_argument('--max', metavar='max_block_size', type=int, default=512,
                           help='max block size   int[min_block_size, image_size], square of 2')
    argparser.add_argument('-q', metavar='quant_power', type=float, default=0.2,
                           help='quantization power   float(0, 1]')
    argparser.add_argument('-s', metavar='ch_scale', type=float, default=4.37,
                           help='scale to ch_scale watermark pixels values before embedding   float(0, 255]')
    argparser.add_argument('-o', metavar='offset', type=int, nargs=2, default=None,
                           help='offset container image     2 x int[0, image_size]')
    args = argparser.parse_args()

    img = Image.open(args.container)
    watermark = Image.open(args.watermark)

    qtar = QtarStego(args.t, args.min, args.max, args.q, args.s, args.o)
    key_data = qtar.embed(img, watermark)

    qtar.get_container_image().save('images\stages\\1-container.bmp')
    qtar.get_qt_image().save('images\stages\\2-quad_tree.bmp')
    qtar.get_dct_image().save('images\stages\\3-dct.bmp')
    qtar.get_ar_image().save('images\stages\\4-adaptive_regions.bmp')
    stego_image = qtar.get_stego_image()
    stego_image.save('images\stages\\6-stego_image.bmp')
    wm = qtar.get_wm()
    wm.save('images\stages\\5-watermark.bmp')

    extracted_wm = qtar.extract(stego_image, key_data)
    extracted_wm.save('images\stages\\7-extracted_watermark.bmp')
    print("container PSNR: {}".format(psnr(img, stego_image)))
    print("watermark PSNR: {}".format(psnr(wm, extracted_wm)))


if __name__ == "__main__":
    main(sys.argv)
