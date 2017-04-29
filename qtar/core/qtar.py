import warnings
from itertools import islice
from math import log2, pow, sqrt
from copy import copy

from PIL import Image
from PIL import ImageChops
from numpy import array, zeros, append
from scipy.fftpack import dct, idct

from qtar.core.imageqt import ImageQT
from qtar.core.adaptiveregions import adapt_regions
from qtar.core.container import Container, Key
from qtar.core.matrixregion import MatrixRegions, draw_borders_on

DEFAULT_PARAMS = {
    'homogeneity_threshold': 0.4,
    'min_block_size':        8,
    'max_block_size':        512,
    'quant_power':           1,
    'ch_scale':              4.37,
    'offset':                (0, 0)
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

    def embed(self, img_container, img_watermark=None, resize_to_fit=True, stages=False):
        size = int(pow(2, int(log2(min(img_container.width, img_container.height)))))
        img_container = self.__prepare_image(img_container, shape=(size, size), offset=self.offset)
        chs_container = self.__convert_image_to_chs(img_container)
        container_image_mode = img_container.mode

        key = Key(ch_scale=self.ch_scale,
                  offset=self.offset)
        container = Container(key=key)

        for ch, ch_image in enumerate(chs_container):
            regions = self.__divide_into_regions(ch_image)
            qt_key = regions.key
            regions_dct = self.__dct_regions(regions)
            regions_embed, ar_indexes = self.__define_regions_to_embed(regions_dct)

            container.chs_regions.append(regions)
            container.chs_regions_dct.append(regions_dct)
            container.chs_regions_dct_embed.append(regions_embed)
            key.chs_qt_key.append(qt_key)
            key.chs_ar_key.append(ar_indexes)

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
                "2-quad_tree": self.__regions_to_image(container.chs_regions, container_image_mode,
                                                       borders=True, only_right_bottom=True),
                "3-adaptive_regions": self.__regions_to_image(container.chs_regions_dct_embed, container_image_mode,
                                                              borders=True, factor=10),
                "4-dct": self.__regions_to_image(chs_embedded_dct_regions, container_image_mode,
                                                 factor=10),
                "5-watermark": img_watermark,
                "6-stego_image": img_stego
            }
        return StegoEmbedResult(img_stego, key, container.fact_bpp, img_container, img_watermark,  stages_imgs)

    @staticmethod
    def __prepare_image(image, shape=None, offset=None, mode=None):
        if shape is not None:
            image = image.resize(shape, Image.BILINEAR)
        if offset is not None:
            x, y = offset
            image = ImageChops.offset(image, x, y)
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

    def __define_regions_to_embed(self, regions):
        return adapt_regions(regions, q_power=self.quant_power)

    def __embed_in_regions(self, regions, ch_watermark):
        regions = MatrixRegions(regions.rects, copy(regions.matrix))
        wm_iter = ch_watermark.flat
        stop = False
        for i in range(0, len(regions)):
            region = regions[i]
            size = region.size
            shape = region.shape
            region_stego_flat = array(list(islice(wm_iter, size)))
            if region_stego_flat.size < size:
                region_flat = list(region.flat)
                region_stego_flat = append(region_stego_flat, region_flat[region_stego_flat.size:size])
                stop = True
            region_stego = region_stego_flat.reshape(shape)
            regions[i] = region_stego / 255 * self.ch_scale
            if stop:
                return regions
        if not stop:
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
            ar_indexes = key.chs_ar_key[ch]
            wm_shape = key.wm_shape
            regions = self.__divide_into_regions(ch_stego, qt_key)
            regions_dct = self.__dct_regions(regions)
            regions_extract = self.__define_regions_to_extract(regions_dct, ar_indexes)
            ch_watermark = self.__extract_from_regions(regions_extract, wm_shape)
            chs_regions.append(regions)
            chs_regions_extract.append(regions_extract)
            chs_watermark.append(ch_watermark)

        if stages:
            stages_imgs = {
                "7-quad_tree":  self.__regions_to_image(chs_regions, stego_image_mode,
                                                        borders=True, only_right_bottom=True),
                "8-adaptive_regions": self.__regions_to_image(chs_regions_extract, stego_image_mode,
                                                              borders=True, factor=10),
                "9-extracted_watermark": self.__chs_to_image(chs_watermark, stego_image_mode)
            }
            return stages_imgs
        else:
            return self.__chs_to_image(chs_watermark, stego_image_mode)

    @staticmethod
    def __define_regions_to_extract(regions, ar_indexes):
        regions_extract, ar_indexes = adapt_regions(regions, ar_indexes=ar_indexes)
        return regions_extract

    def __extract_from_regions(self, regions, wm_shape):
        regions = MatrixRegions(regions.rects, copy(regions.matrix))
        region_stego_flat = array([])
        wm_size = wm_shape[0] * wm_shape[1]
        for region in regions:
            region_flat = list(region.flat)
            region_stego_flat = append(region_stego_flat, region_flat)
            if region_stego_flat.size >= wm_size:
                break
        if region_stego_flat.size <= wm_size:
            region_stego_flat = append(region_stego_flat, zeros(wm_size - region_stego_flat.size))
        ch_watermark = region_stego_flat[0:wm_size].reshape(wm_shape)
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

    @staticmethod
    def __draw_borders(chs_regions, only_right_bottom=False):
        chs_matrix = [ch_regions.matrix for ch_regions in chs_regions]
        max_value = max([ch_matrix.max() for ch_matrix in chs_matrix])

        for ch_id in range(0, len(chs_matrix)):
            for ch_regions in chs_regions:
                chs_matrix[ch_id] = draw_borders_on(chs_matrix[ch_id], ch_regions.rects, 0, only_right_bottom)
            chs_matrix[ch_id] = draw_borders_on(chs_matrix[ch_id], chs_regions[ch_id].rects, max_value,
                                                only_right_bottom)
        return chs_matrix

    @classmethod
    def __regions_to_image(cls, chs_regions, mode, offset=None, factor=1, borders=False, only_right_bottom=False):
        if borders:
            chs_matrix = cls.__draw_borders(chs_regions, only_right_bottom)
        else:
            chs_matrix = [ch_regions.matrix for ch_regions in chs_regions]

        return cls.__chs_to_image(chs_matrix, mode, offset, factor)

    @property
    def params(self):
        return {
            'homogeneity_threshold': self.homogeneity_threshold,
            'min_block_size':        self.min_block_size,
            'max_block_size':        self.max_block_size,
            'quant_power':           self.quant_power,
            'ch_scale':              self.ch_scale,
            'offset':                self.offset
        }

    @staticmethod
    def from_dict(params):
        return QtarStego(params['homogeneity_threshold'],
                         params['min_block_size'],
                         params['max_block_size'],
                         params['quant_power'],
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
