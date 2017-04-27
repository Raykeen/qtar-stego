from qtar.core.imageqt import ImageQT
from qtar.core.adaptiveregions import adapt_regions


class Key:
    def __init__(self, params=None, chs_rects=None, chs_a_indexes=None, wm_shape=None):
        self.params = params
        self.chs_rects = chs_rects or []
        self.chs_a_indexes = chs_a_indexes or []
        self.wm_shape = wm_shape

    def save(self):
        pass

    def open(self):
        pass


class Container:
    def __init__(self, chs_regions=None, chs_regions_dct=None, chs_regions_dct_embed=None, key=Key()):
        self.chs_regions = chs_regions or []
        self.chs_regions_dct = chs_regions_dct or []
        self.chs_regions_dct_embed = chs_regions_dct_embed or []
        self.key = key

    @property
    def chs_image(self):
        return [regions.matrix
                for regions in self.chs_regions]

    @property
    def size(self):
        return len(self.chs_image[0])

    @property
    def chs_dct_img(self):
        return [regions.matrix
                for regions in self.chs_regions_dct]

    @property
    def available_space(self):
        return min(regions.total_size
                   for regions in self.chs_regions_dct_embed)

    @property
    def available_bpp(self):
        total_size = sum(regions.get_total_size()
                         for regions in self.chs_regions_dct_embed)
        bpp = (total_size * 8) / self.size**2
        return bpp

    @property
    def fact_bpp(self):
        wm_w, wm_h = self.key.wm_shape
        ch_count = len(self.chs_image)
        return (8 * ch_count * wm_w * wm_h) / self.size**2
