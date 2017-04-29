import struct

import numpy as np

from qtar.core.imageqt import parse_qt_key


class Key:
    def __init__(self, ch_scale=None, offset=None, chs_qt_key=None, chs_ar_key=None, wm_shape=None):
        self.ch_scale = ch_scale
        self.offset = offset
        self.chs_qt_key = chs_qt_key or []
        self.chs_ar_key = chs_ar_key or []
        self.wm_shape = wm_shape

    def save(self, path):
        with open(path, 'wb') as file:
            chs_count = len(self.chs_qt_key)
            file.write(struct.pack('>fiiiib', self.ch_scale, *self.offset, *self.wm_shape, chs_count))

            for qt_key, ar_key in zip(self.chs_qt_key, self.chs_ar_key):
                qt_key_packed = np.packbits(qt_key)
                ar_key_packed = np.array(ar_key).astype(np.uint8)
                file.write(struct.pack('>i', len(qt_key_packed)))
                file.write(qt_key_packed.tobytes())
                file.write(ar_key_packed.tobytes())


    @classmethod
    def open(cls, path):
        with open(path, 'rb') as file:
            params_struct = '>fiiiib'
            params_bytes = file.read(struct.calcsize(params_struct))
            ch_scale, x, y, wm_w, wm_h, chs_count = struct.unpack(params_struct, params_bytes)
            offset = (x, y)
            wm_shape = (wm_w, wm_h)
            chs_qt_key = []
            chs_ar_key = []
            for ch in range(chs_count):
                qt_key_bytes_size_bytes = file.read(struct.calcsize('>i'))
                qt_key_bytes_size = struct.unpack('>i', qt_key_bytes_size_bytes)[0]
                qt_key_bytes = file.read(qt_key_bytes_size)
                qt_key = np.unpackbits(np.frombuffer(qt_key_bytes, np.uint8))
                qt_key, block_count = parse_qt_key(qt_key.tolist())
                ar_key_bytes = file.read(block_count)
                ar_key = np.frombuffer(ar_key_bytes, np.uint8)
                chs_qt_key.append(qt_key)
                chs_ar_key.append(ar_key)

        return cls(ch_scale, offset, chs_qt_key, chs_ar_key, wm_shape)


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
