import warnings
from PIL import Image
from PIL import ImageChops
from numpy import array, zeros, append
from math import log2, pow, sqrt
from scipy.fftpack import dct, idct
from itertools import islice
from ImageQT import *
from AdaptiveRegions import *

DEFAULT_PARAMS = {
    'homogeneity_threshold': 0.4,
    'min_block_size': 8,
    'max_block_size': 512,
    'quant_power': 1,
    'ch_scale': 4.37,
    'offset': None
}

class QtarStego:
    def __init__(self,
                 homogeneity_threshold=DEFAULT_PARAMS['homogeneity_threshold'],
                 min_block_size=DEFAULT_PARAMS['min_block_size'],
                 max_block_size=DEFAULT_PARAMS['max_block_size'],
                 quant_power=DEFAULT_PARAMS['quant_power'],
                 ch_scale=DEFAULT_PARAMS['ch_scale'],
                 offset=DEFAULT_PARAMS['offset']):
        self.homogeneity_threshold = homogeneity_threshold
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.quant_power = quant_power
        self.ch_scale = ch_scale
        self.offset = offset
        self.image = Image.new("RGB", (512, 512), "white")
        self.watermark = Image.new("RGB", (512, 512), "white")
        self.size = 512
        self.wm_size = (512, 512)
        self.key_data = {'wm_shape': None, 'aregions': [[], [], []]}
        self.image_chs = [[], [], []]
        self.qt_regions_chs = [[], [], []]
        self.dct_regions_chs = [[], [], []]
        self.stego_img_chs = [[], [], []]
        self.aregions_chs = [[], [], []]
        self.watermark_chs = [[], [], []]

    def embed(self, image, watermark=None, resize_to_fit=True):
        self.image = image
        self.watermark = watermark
        self.size = int(pow(2, int(log2(min(image.width, image.height)))))
        self.image_chs = self._prepare_image(image, self.size, self.offset)
        self._alloc()

        for channel, image_ch in enumerate(self.image_chs):
            self._find_regions_in_channel(channel, image_ch)
            self.key_data['aregions'][channel] = self.aregions_chs[channel]

        available_space = self.get_available_space()
        if resize_to_fit:
            new_wm_size = int(sqrt(available_space))
            self.watermark_chs = self._prepare_image(watermark, new_wm_size)
            self.wm_size = (new_wm_size, new_wm_size)
        else:
            self.watermark_chs = self._prepare_image(watermark)
            self.wm_size = watermark.size
        self.key_data['wm_shape'] = self.watermark_chs[0].shape

        for channel, image_ch in enumerate(self.image_chs):
            self._embed_in_channel(channel, self.watermark_chs[channel])

        return self.key_data

    def extract(self, stego_image, key_data):
        self.key_data = key_data
        self.size = min(stego_image.width, stego_image.height)
        self.stego_img_chs = self._prepare_image(stego_image, offset=self.offset)
        for channel, stego_image_ch in enumerate(self.stego_img_chs):
            self.watermark_chs[channel] = self._extract_from_channel(channel, stego_image_ch, self.key_data)

        return self.get_wm()

    def _find_regions_in_channel(self, channel, image_ch):
        qt_regions = ImageQT(image_ch,
                             self.min_block_size,
                             min(self.max_block_size, self.size),
                             self.homogeneity_threshold)
        dct_regions = self._dct_2d(qt_regions)
        adaptive_regions = AdaptiveRegions(dct_regions, self.quant_power)

        self.qt_regions_chs[channel] = qt_regions
        self.dct_regions_chs[channel] = dct_regions
        self.aregions_chs[channel] = adaptive_regions

    def _embed_in_channel(self, channel, watermark_ch=None):
        aregions = self.aregions_chs[channel].regions
        dct_regions = self.dct_regions_chs[channel]
        self._embed_in_aregions(aregions, watermark_ch)
        stego_img = self._dct_2d(dct_regions, True)
        self.stego_img_chs[channel] = stego_img.matrix

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
        if not stop:
            try:
                next(wm_iter)
            except StopIteration:
                return
            warnings.warn("Container capacity is not enough for embedding given secret image. Extracted secret image will be not complete.")

    def _extract_from_aregions(self, aregions, wm_shape):
        flat_stego_region = array([])
        wm_size = wm_shape[0] * wm_shape[1]
        for i in range(0, aregions.count):
            aregion = aregions[i]
            flat_aregion = list(aregion.flat)
            flat_stego_region = append(flat_stego_region, flat_aregion)
            if flat_stego_region.size >= wm_size:
                break
        if flat_stego_region.size <= wm_size:
            flat_stego_region = append(flat_stego_region, zeros(wm_size-flat_stego_region.size))
        watermark_ch = flat_stego_region[0:wm_size].reshape(wm_shape)
        return watermark_ch * 255 / self.ch_scale

    def _alloc(self):
        self.key_data['aregions'] = []
        self.qt_regions_chs = []
        self.dct_regions_chs = []
        self.stego_img_chs = []
        self.aregions_chs = []
        self.watermark_chs = []
        for i in range(0, len(self.image_chs)):
            self.key_data['aregions'].append([])
            self.qt_regions_chs.append([])
            self.dct_regions_chs.append([])
            self.stego_img_chs.append([])
            self.aregions_chs.append([])
            self.watermark_chs.append([])

    def _prepare_image(self, image, size=None, offset=None):
        prepared = image

        if size is not None:
            prepared = prepared.resize((size, size), Image.BILINEAR)
        if offset is not None:
            x, y = offset
            prepared = ImageChops.offset(prepared, x, y)
        if image.mode != self.image.mode:
            prepared = image.convert(self.image.mode)

        image_channels_arrays = [array(image_channel) for image_channel in prepared.split()]
        return image_channels_arrays

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

    def get_available_space(self):
        space_availible = []
        for aregions_ch in self.aregions_chs:
            space_availible.append(aregions_ch.regions.get_total_size())
        return min(space_availible)

    def get_available_bpp(self):
        total_size = 0
        for aregions in self.aregions_chs:
            total_size += aregions.get_total_size()
        bpp = (total_size * 8) / self.size**2
        return bpp

    def get_fact_bpp(self):
        wm_w, wm_h = self.wm_size
        ch_count = len(self.image_chs)
        return (8*ch_count*wm_w * wm_h) / self.size**2

    @staticmethod
    def convert_chs_to_image(matrix_chs, mode, offset=None):
        image_chs = [Image.fromarray(image_ch).convert('L')
                     for image_ch in matrix_chs]
        result_image = Image.merge(mode, image_chs)
        if offset is not None:
            x, y = offset
            result_image = ImageChops.offset(result_image, -x, -y)

        return result_image

    def get_container_image(self):
        return self.convert_chs_to_image(self.image_chs, self.image.mode, self.offset)

    def get_qt_image(self):
        matrix_chs = [qtree_regions.get_matrix_with_borders(only_right_bottom=True)
                      for qtree_regions in self.qt_regions_chs]
        return self.convert_chs_to_image(matrix_chs, self.image.mode, self.offset)

    def get_dct_image(self):
        matrix_chs = [dct_regions.matrix * 10
                      for dct_regions in self.dct_regions_chs]
        return self.convert_chs_to_image(matrix_chs, self.image.mode, self.offset)

    def get_ar_image(self):
        max_dct_value = max([dct_regions.matrix.max() for dct_regions in self.dct_regions_chs])
        matrix_chs = [aregions.regions.get_matrix_with_borders(value=max_dct_value)
                      for aregions in self.aregions_chs]
        return self.convert_chs_to_image(matrix_chs, self.image.mode, self.offset)

    def get_stego_image(self):
        return self.convert_chs_to_image(self.stego_img_chs, self.image.mode, self.offset)

    def get_wm(self):
        return self.convert_chs_to_image(self.watermark_chs, self.watermark.mode)

    @staticmethod
    def from_dict(params):
        return QtarStego(params['homogeneity_threshold'],
                         params['min_block_size'],
                         params['max_block_size'],
                         params['quant_power'],
                         params['ch_scale'],
                         params['offset'])
