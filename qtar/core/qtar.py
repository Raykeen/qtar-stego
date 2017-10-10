import warnings
from itertools import islice
from math import log2, pow, sqrt
from copy import copy

from PIL import Image
from PIL import ImageChops
from numpy import array, zeros, append
from scipy.fftpack import dct, idct

from qtar.core.imageqt import ImageQT
from qtar.core.curvefitting import fit_cfregions, CFRegions, draw_cf_map
from qtar.core.container import Container, Key
from qtar.core.matrixregion import MatrixRegions, draw_borders_on

DEFAULT_PARAMS = {
    'homogeneity_threshold': 0.4,
    'min_block_size': 8,
    'max_block_size': 512,
    'quant_power': 1,
    'cf_grid_size': 8,
    'ch_scale': 4.37,
    'offset': (0, 0)
}


class QtarStego:
    def __init__(self,
                 homogeneity_threshold=DEFAULT_PARAMS['homogeneity_threshold'],
                 min_block_size=DEFAULT_PARAMS['min_block_size'],
                 max_block_size=DEFAULT_PARAMS['max_block_size'],
                 quant_power=DEFAULT_PARAMS['quant_power'],
                 cf_grid_size=DEFAULT_PARAMS['cf_grid_size'],
                 ch_scale=DEFAULT_PARAMS['ch_scale'],
                 offset=DEFAULT_PARAMS['offset']):
        self.homogeneity_threshold = homogeneity_threshold
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.quant_power = quant_power
        self.cf_grid_size = cf_grid_size
        self.ch_scale = ch_scale
        self.offset = offset

    def embed(self, img_container, img_watermark=None, resize_to_fit=True, stages=False):
        size = int(pow(2, int(log2(min(img_container.width, img_container.height)))))
        img_container = self.__prepare_image(img_container, shape=(size, size), offset=self.offset)
        chs_container = self.__convert_image_to_chs(img_container)
        container_image_mode = img_container.mode

        key = Key(ch_scale=self.ch_scale,
                  cf_grid_size=self.cf_grid_size,
                  offset=self.offset)
        container = Container(key=key)

        chs_regions = []
        for ch, ch_image in enumerate(chs_container):
            regions = self.__divide_into_regions(ch_image)
            qt_key = regions.key
            regions_dct = self.__dct_regions(regions)
            regions_embed = fit_cfregions(regions_dct, self.quant_power, self.cf_grid_size)

            chs_regions.append(regions)
            container.chs_regions_dct.append(regions_dct)
            container.chs_regions_dct_embed.append(regions_embed)
            key.chs_qt_key.append(qt_key)
            key.chs_cf_key.append(regions_embed.curves)

        available_space = container.available_space
        wm_shape = img_watermark.size
        if resize_to_fit:
            wm_size = int(sqrt(available_space))
            wm_shape = (wm_size, wm_size)
        img_watermark = self.__prepare_image(img_watermark, shape=wm_shape, mode=img_container.mode)
        chs_watermark = self.__convert_image_to_chs(img_watermark)
        key.wm_shape = wm_shape

        chs_stego_img = []
        chs_embedded_dct_regions = []
        for regions_dct, embed_dct_regions, wm_ch in zip(container.chs_regions_dct,
                                                         container.chs_regions_dct_embed,
                                                         chs_watermark):
            embedded_dct_regions = self.__embed_in_regions(embed_dct_regions, wm_ch)
            idct_regions = MatrixRegions(regions_dct.rects, embedded_dct_regions.matrix)
            stego_img_regions = self.__idct_regions(idct_regions)
            chs_stego_img.append(stego_img_regions.matrix)
            chs_embedded_dct_regions.append(embedded_dct_regions)

        img_stego = self.__chs_to_image(chs_stego_img, container_image_mode)
        img_stego = self.__prepare_image(img_stego, offset=(-self.offset[0], -self.offset[1]))
        img_container = self.__prepare_image(img_container, offset=(-self.offset[0], -self.offset[1]))
        stages_imgs = None
        if stages:
            stages_imgs = {
                "1-container": img_container,
                "2-quad_tree": self.__regions_to_image(chs_regions, container_image_mode,
                                                       borders=True, only_right_bottom=True),
                "3-adaptive_regions": self.__regions_to_image(container.chs_regions_dct_embed, container_image_mode,
                                                              borders=True, only_right_bottom=True, factor=10),
                "4-dct": self.__regions_to_image(chs_embedded_dct_regions, container_image_mode,
                                                 factor=10),
                "5-watermark": img_watermark,
                "6-stego_image": img_stego
            }
        return StegoEmbedResult(img_stego, key, container.fact_bpp, img_container, img_watermark, stages_imgs)

    @staticmethod
    def __prepare_image(image, shape=None, offset=None, mode=None):
        if shape is not None:
            image = image.resize(shape, Image.BILINEAR)
        if offset is not None:
            x, y = offset
            image = ImageChops.offset(image, -x, -y)
        if mode is not None:
            image = image.convert(mode)
        return image

    def __divide_into_regions(self, ch_image, key=None):
        if key is None:
            size = min(self.max_block_size, ch_image.shape[0])
            regions = ImageQT(ch_image, self.min_block_size, size, self.homogeneity_threshold)
        else:
            regions = ImageQT(ch_image, key=key)
        return regions

    @staticmethod
    def __dct_regions(regions, inverse=False):
        size = regions.matrix.shape[0]
        mx_result = zeros((size, size))
        regions_dct = MatrixRegions(regions.rects, mx_result)
        for i, region in enumerate(regions):
            if inverse:
                region_dct = idct(idct(region.T, norm='ortho').T, norm='ortho')
            else:
                region_dct = dct(dct(region, norm='ortho').T, norm='ortho').T
            regions_dct[i] = region_dct
        return regions_dct

    @classmethod
    def __idct_regions(cls, regions):
        return cls.__dct_regions(regions, True)

    def __embed_in_regions(self, regions, ch_watermark):
        regions = CFRegions(regions.rects, copy(regions.matrix), regions.curves, self.cf_grid_size)
        wm_iter = ch_watermark.flat
        for i in range(0, len(regions)):
            region = regions[i]
            size = region.size
            region_stego = array(list(islice(wm_iter, size)))

            if region_stego.size < size:
                region_stego = append(region_stego, region[region_stego.size:size])

            regions[i] = region_stego / 255 * self.ch_scale

            if region_stego.size < size:
                return regions
        else:
            try:
                next(wm_iter)
            except StopIteration:
                return regions
            warnings.warn("Container capacity is not enough for embedding given secret image."
                          "Extracted secret image will be not complete.")

    def extract(self, img_stego, key, stages=False):
        img_stego = self.__prepare_image(img_stego, offset=self.offset)
        chs_stego = self.__convert_image_to_chs(img_stego)
        stego_image_mode = img_stego.mode

        chs_regions = []
        chs_regions_extract = []
        chs_watermark = []
        for ch, ch_stego in enumerate(chs_stego):
            qt_key = key.chs_qt_key[ch]
            cf_key = key.chs_cf_key[ch]
            wm_shape = key.wm_shape
            regions = self.__divide_into_regions(ch_stego, qt_key)
            regions_dct = self.__dct_regions(regions)
            regions_extract = CFRegions.from_regions(regions_dct, cf_key, self.cf_grid_size)
            ch_watermark = self.__extract_from_regions(regions_extract, wm_shape)
            chs_regions.append(regions)
            chs_regions_extract.append(regions_extract)
            chs_watermark.append(ch_watermark)

        if stages:
            stages_imgs = {
                "7-quad_tree": self.__regions_to_image(chs_regions, stego_image_mode,
                                                       borders=True, only_right_bottom=True),
                "8-adaptive_regions": self.__regions_to_image(chs_regions_extract, stego_image_mode,
                                                              borders=True, factor=10),
                "9-extracted_watermark": self.__chs_to_image(chs_watermark, stego_image_mode)
            }
            return stages_imgs
        else:
            return self.__chs_to_image(chs_watermark, stego_image_mode)

    def __extract_from_regions(self, regions, wm_shape):
        region_stego = array([])
        wm_size = wm_shape[0] * wm_shape[1]
        for region in regions:
            region_stego = append(region_stego, region)
            if region_stego.size >= wm_size:
                break
        else:
            region_stego = append(region_stego, zeros(wm_size - region_stego.size))
        ch_watermark = region_stego[0:wm_size].reshape(wm_shape)
        return ch_watermark * 255 / self.ch_scale

    @staticmethod
    def __convert_image_to_chs(image):
        chs_image = [array(ch_image)
                     for ch_image in image.split()]
        return chs_image

    @staticmethod
    def __chs_to_image(chs_matrix, mode, offset=None, factor=1):
        chs_image = [Image.fromarray(ch_matrix * factor).convert('L')
                     for ch_matrix in chs_matrix]
        image = Image.merge(mode, chs_image)
        if offset is not None:
            x, y = offset
            image = ImageChops.offset(image, -x, -y)

        return image

    def __draw_borders(self, chs_regions, only_right_bottom=False):
        chs_matrix = [ch_regions.matrix for ch_regions in chs_regions]
        max_value = max([ch_matrix.max() for ch_matrix in chs_matrix])

        is_cf_regions = type(chs_regions[0]) is CFRegions

        for ch_id in range(0, len(chs_matrix)):
            for ch_regions in chs_regions:
                if is_cf_regions:
                    chs_matrix[ch_id] = draw_cf_map(
                        CFRegions(ch_regions.rects, chs_matrix[ch_id], ch_regions.curves, self.cf_grid_size),
                        0, only_right_bottom)
                else:
                    chs_matrix[ch_id] = draw_borders_on(chs_matrix[ch_id], ch_regions.rects, 0, only_right_bottom)
            if is_cf_regions:
                chs_matrix[ch_id] = draw_cf_map(
                    CFRegions(chs_regions[ch_id].rects, chs_matrix[ch_id], chs_regions[ch_id].curves, self.cf_grid_size),
                    max_value, only_right_bottom)
            else:
                chs_matrix[ch_id] = draw_borders_on(chs_matrix[ch_id], chs_regions[ch_id].rects, max_value,
                                                    only_right_bottom)
        return chs_matrix

    def __regions_to_image(self, chs_regions, mode, offset=None, factor=1, borders=False, only_right_bottom=False):
        if borders:
            chs_matrix = self.__draw_borders(chs_regions, only_right_bottom)
        else:
            chs_matrix = [ch_regions.matrix for ch_regions in chs_regions]

        return self.__chs_to_image(chs_matrix, mode, offset, factor)

    @property
    def params(self):
        return {
            'homogeneity_threshold': self.homogeneity_threshold,
            'min_block_size': self.min_block_size,
            'max_block_size': self.max_block_size,
            'quant_power': self.quant_power,
            'cf_grid_size': self.cf_grid_size,
            'ch_scale': self.ch_scale,
            'offset': self.offset
        }

    @staticmethod
    def from_dict(params):
        return QtarStego(params['homogeneity_threshold'],
                         params['min_block_size'],
                         params['max_block_size'],
                         params['quant_power'],
                         params['cf_grid_size'],
                         params['ch_scale'],
                         params['offset'])


class StegoEmbedResult:
    def __init__(self, img_stego, key, bpp, img_container=None, img_watermark=None, stages_imgs=None):
        self.img_stego = img_stego
        self.img_container = img_container
        self.img_watermark = img_watermark
        self.key = key
        self.bpp = bpp
        self.stages_imgs = stages_imgs
