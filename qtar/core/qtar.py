import warnings
from itertools import islice
from math import log2, pow, sqrt
from copy import copy

from PIL import Image, ImageChops
from numpy import array, zeros, append
from scipy.fftpack import dct, idct

from qtar.core.imageqt import ImageQT, ImageQTPM
from qtar.core.curvefitting import fit_cfregions, CFRegions, draw_cf_map
from qtar.core.quantizationmatrix import generate_flat_matrix
from qtar.core.adaptiveregions import adapt_regions
from qtar.core.permutation import reverse_permutation, fix_diff, get_diff_fix
from qtar.core.container import Container, Key
from qtar.core.matrixregion import MatrixRegions, divide_into_equal_regions, draw_borders_on
from qtar.core.zigzag import zigzag_embed_to_regions, zigzag_extract_from_regions

DEFAULT_PARAMS = {
    'homogeneity_threshold': 0.4,
    'min_block_size':        8,
    'max_block_size':        512,
    'wm_block_size':         None,
    'quant_power':           1,
    'cf_grid_size':          None,
    'ch_scale':              4.37,
    'offset':                (0, 0),
    'curve_fitting':         True,
    'use_permutations':      False
}


class QtarStego:
    def __init__(self,
                 homogeneity_threshold=DEFAULT_PARAMS['homogeneity_threshold'],
                 min_block_size=DEFAULT_PARAMS['min_block_size'],
                 max_block_size=DEFAULT_PARAMS['max_block_size'],
                 wm_block_size=DEFAULT_PARAMS['wm_block_size'],
                 quant_power=DEFAULT_PARAMS['quant_power'],
                 cf_grid_size=DEFAULT_PARAMS['cf_grid_size'],
                 ch_scale=DEFAULT_PARAMS['ch_scale'],
                 offset=DEFAULT_PARAMS['offset'],
                 use_permutations=DEFAULT_PARAMS['use_permutations']):
        self.homogeneity_threshold = homogeneity_threshold
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.wm_block_size = wm_block_size
        self.quant_power = quant_power
        self.cf_grid_size = cf_grid_size
        self.ch_scale = ch_scale
        self.offset = offset
        self.curve_fitting = bool(cf_grid_size)
        self.wm_dct = bool(wm_block_size)
        self.use_permutations = use_permutations

    def embed(self, img_container, img_watermark=None, resize_to_fit=True, stages=False):
        size = int(pow(2, int(log2(min(img_container.width, img_container.height)))))

        max_b = min(self.max_block_size, *img_container.size)

        img_container = self.__prepare_image(img_container, shape=(size, size), offset=self.offset)
        chs_container = self.__convert_image_to_chs(img_container)
        container_image_mode = img_container.mode

        key = Key(ch_scale=self.ch_scale,
                  offset=self.offset,
                  cf_grid_size=self.cf_grid_size if self.curve_fitting else None,
                  use_permutations=self.use_permutations,
                  container_shape=(size, size),
                  wm_block_size=self.wm_block_size)
        container = Container(key=key)

        chs_regions = []
        chs_pm_key = []
        for ch, ch_image in enumerate(chs_container):
            if self.use_permutations:
                regions = ImageQTPM(ch_image, self.min_block_size, max_b, self.homogeneity_threshold)
                chs_pm_key.append(regions.permutation)
            else:
                regions = ImageQT(ch_image, self.min_block_size, max_b, self.homogeneity_threshold)
            qt_key = regions.key

            regions_dct = self.__dct_regions(regions)

            if self.curve_fitting:
                regions_embed = fit_cfregions(regions_dct, self.quant_power, self.cf_grid_size)
                key.chs_cf_key.append(regions_embed.curves)
            else:
                regions_embed, ar_indexes = adapt_regions(regions_dct, q_power=self.quant_power)
                key.chs_ar_key.append(ar_indexes)

            chs_regions.append(regions)
            container.chs_regions_dct.append(regions_dct)
            container.chs_regions_dct_embed.append(regions_embed)
            key.chs_qt_key.append(qt_key)

        available_space = container.available_space

        if available_space == 0:
            raise NoSpaceError("There is no space for embedding. Try other parameters.")

        wm_shape = img_watermark.size
        if resize_to_fit:
            wm_size = int(sqrt(available_space))
            wm_shape = (wm_size, wm_size)
        img_watermark = self.__prepare_image(img_watermark, shape=wm_shape, mode=img_container.mode)
        chs_watermark = self.__convert_image_to_chs(img_watermark)
        key.wm_shape = wm_shape

        chs_stego_img = []
        chs_embedded_dct_regions = []

        chs_count = len(chs_container)
        for ch in range(chs_count):
            regions_dct = container.chs_regions_dct[ch]
            embed_dct_regions = container.chs_regions_dct_embed[ch]
            wm_ch = chs_watermark[ch]

            if self.wm_dct:
                wm_regions = divide_into_equal_regions(wm_ch, self.wm_block_size)
                wm_dct_regions = self.__dct_regions(wm_regions)
                wm_ch = self.__quant_regions(wm_dct_regions)

            embedded_dct_regions = self.__embed_in_regions(embed_dct_regions, wm_ch)
            chs_embedded_dct_regions.append(embedded_dct_regions)

            idct_regions = MatrixRegions(regions_dct.rects, embedded_dct_regions.matrix)
            stego_img_mx = self.__idct_regions(idct_regions).matrix

            if self.use_permutations:
                pm_key = chs_pm_key[ch]
                qt_key = key.chs_qt_key[ch]

                stego_img_mx = reverse_permutation(stego_img_mx, pm_key)

                compressed_stego_img_mx = array(Image.fromarray(copy(stego_img_mx)).convert('L'))
                distorted_regions = ImageQTPM(compressed_stego_img_mx, key=qt_key)
                ch_pm_fix = get_diff_fix(pm_key, distorted_regions.permutation, distorted_regions.rects)

                key.chs_pm_fix_key.append(ch_pm_fix)

            chs_stego_img.append(stego_img_mx)

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
                                                              borders=True, factor=10),
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

    @staticmethod
    def __quant_regions(regions):
        quantized = MatrixRegions(regions.rects, copy(regions.matrix))
        for i, region in enumerate(quantized):
            height, width = region.shape
            q_mx = generate_flat_matrix(max((width, height)))
            quantized[i] = region / q_mx[0:height, 0:width]
        return quantized

    @staticmethod
    def __dequant_regions(regions):
        dequantized = MatrixRegions(regions.rects, copy(regions.matrix))
        for i, region in enumerate(dequantized):
            height, width = region.shape
            q_mx = generate_flat_matrix(max((width, height)))
            dequantized[i] = region * q_mx[0:height, 0:width]
        return dequantized

    @classmethod
    def __idct_regions(cls, regions):
        return cls.__dct_regions(regions, True)

    def __embed_in_regions(self, regions, ch_watermark):
        if self.curve_fitting:
            regions = CFRegions(regions.rects, copy(regions.matrix), regions.curves, self.cf_grid_size)
        else:
            regions = MatrixRegions(regions.rects, copy(regions.matrix))

        if self.wm_dct:
            return zigzag_embed_to_regions(ch_watermark, regions)

        wm_iter = ch_watermark.flat

        for i in range(0, len(regions)):
            region = regions[i]
            size = region.size
            shape = region.shape
            region_stego = array(list(islice(wm_iter, size)))

            if region_stego.size == 0:
                if size == 0:
                    continue
                else:
                    return regions

            region_stego = region_stego / 255 * self.ch_scale
            region_stego = append(region_stego, region.flat[region_stego.size:size])
            region_stego = region_stego.reshape(shape)
            regions[i] = region_stego

        try:
            next(wm_iter)
        except StopIteration:
            pass
        else:
            warnings.warn("Container capacity is not enough for embedding given secret image."
                          "The extracted secret image will be incomplete.")
        return regions

    def extract(self, img_stego, key, stages=False):
        img_stego = self.__prepare_image(img_stego, offset=key.offset)
        chs_stego = self.__convert_image_to_chs(img_stego)
        stego_image_mode = img_stego.mode

        chs_regions = []
        chs_regions_extract = []
        chs_watermark = []
        for ch, ch_stego in enumerate(chs_stego):
            wm_shape = key.wm_shape

            qt_key = key.chs_qt_key[ch]

            if key.use_permutations:
                pm_fix_key = key.chs_pm_fix_key[ch]
                distorted_regions = ImageQTPM(copy(ch_stego), key=qt_key)
                distorted_pm_mx_regions = MatrixRegions(distorted_regions.rects, distorted_regions.permutation)
                pm_key = fix_diff(distorted_pm_mx_regions, pm_fix_key).matrix
                regions = ImageQTPM(copy(ch_stego), key=qt_key, permutation=pm_key)
            else:
                regions = ImageQT(ch_stego, key=qt_key)

            regions_dct = self.__dct_regions(regions)

            if bool(key.cf_grid_size):
                cf_key = key.chs_cf_key[ch]
                regions_extract = CFRegions.from_regions(regions_dct, cf_key, key.cf_grid_size)
            else:
                ar_indexes = key.chs_ar_key[ch]
                regions_extract, ar_indexes = adapt_regions(regions_dct, ar_indexes=ar_indexes)

            if bool(key.wm_block_size):
                wm_quantized_regions = self.__extract_from_regions(regions_extract, wm_shape, key.wm_block_size)
                wm_dct_regions = self.__dequant_regions(wm_quantized_regions)
                wm_regions = self.__idct_regions(wm_dct_regions)
                ch_watermark = wm_regions.matrix
            else:
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

    def __extract_from_regions(self, regions, wm_shape, wm_block_size=None):
        if bool(wm_block_size):
            return zigzag_extract_from_regions(regions, wm_shape, wm_block_size)

        region_stego = array([])
        wm_size = wm_shape[0] * wm_shape[1]
        for region in regions:
            region = region.flatten()
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
            'min_block_size':        self.min_block_size,
            'max_block_size':        self.max_block_size,
            'wm_block_size':         self.wm_block_size,
            'quant_power':           self.quant_power,
            'cf_grid_size':          self.cf_grid_size,
            'ch_scale':              self.ch_scale,
            'offset':                self.offset,
            'use_permutations':      self.use_permutations
        }

    @staticmethod
    def from_dict(params):
        return QtarStego(params['homogeneity_threshold'],
                         params['min_block_size'],
                         params['max_block_size'],
                         params['wm_block_size'],
                         params['quant_power'],
                         params['cf_grid_size'],
                         params['ch_scale'],
                         params['offset'],
                         params['use_permutations'])


class StegoEmbedResult:
    def __init__(self, img_stego, key, bpp, img_container=None, img_watermark=None, stages_imgs=None):
        self.img_stego = img_stego
        self.img_container = img_container
        self.img_watermark = img_watermark
        self.key = key
        self.bpp = bpp
        self.stages_imgs = stages_imgs


class NoSpaceError(Exception): pass