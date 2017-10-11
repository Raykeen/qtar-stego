import struct

import numpy as np

from qtar.core.imageqt import parse_qt_key

PARAMS_STRUCT = '=ifiiiib'


class Key:
    def __init__(self, wm_block_size=None, ch_scale=None, offset=None, chs_qt_key=None, chs_ar_key=None, wm_shape=None):
        self.wm_block_size = wm_block_size
        self.ch_scale = ch_scale
        self.offset = offset
        self.chs_qt_key = chs_qt_key or []
        self.chs_ar_key = chs_ar_key or []
        self.wm_shape = wm_shape

    @property
    def params_bytes(self):
        chs_count = len(self.chs_qt_key)
        return struct.pack(PARAMS_STRUCT,
                           self.wm_block_size,
                           self.ch_scale,
                           *self.offset,
                           *self.wm_shape,
                           chs_count)

    @property
    def chs_qt_key_bytes(self):
        result = []

        for qt_key in self.chs_qt_key:
            key_bytes = np.packbits(qt_key).tobytes()
            result.append(int_to_byte(len(key_bytes)) + key_bytes)

        return result

    @property
    def chs_ar_key_bytes(self):
        return [ints_to_bytes(ar_key, np.uint8) for ar_key in self.chs_ar_key]

    @property
    def params_size(self):
        return len(self.params_bytes)

    @property
    def qt_key_size(self):
        return size_of_chs(self.chs_qt_key_bytes)

    @property
    def ar_key_size(self):
        return size_of_chs(self.chs_ar_key_bytes)

    @property
    def size(self):
        return self.params_size + self.qt_key_size + self.ar_key_size

    def save(self, path):
        with open(path, 'wb') as file:
            key_bytes = self.params_bytes
            for qt_key_bytes, ar_key_bytes in zip(self.chs_qt_key_bytes, self.chs_ar_key_bytes):
                key_bytes += (qt_key_bytes + ar_key_bytes)

            file.write(key_bytes)
        return len(key_bytes)

    @classmethod
    def open(cls, path):
        with open(path, 'rb') as file:
            params_bytes = file.read(struct.calcsize(PARAMS_STRUCT))
            wm_block_size, ch_scale, x, y, wm_w, wm_h, chs_count = struct.unpack(PARAMS_STRUCT, params_bytes)
            offset = (x, y)
            wm_shape = (wm_w, wm_h)

            chs_qt_key = []
            chs_ar_key = []

            for ch in range(chs_count):
                qt_key_bytes_size = read_int(file)
                qt_key = read_bits(file, qt_key_bytes_size)
                qt_key, block_count = parse_qt_key(qt_key.tolist())

                ar_key = np.fromfile(file, np.uint8, block_count).tolist()

                chs_qt_key.append(qt_key)
                chs_ar_key.append(ar_key)

        return cls(wm_block_size, ch_scale, offset, chs_qt_key, chs_ar_key, wm_shape)


class Container:
    def __init__(self, chs_regions_dct=None, chs_regions_dct_embed=None, key=Key()):
        self.chs_regions_dct = chs_regions_dct or []
        self.chs_regions_dct_embed = chs_regions_dct_embed or []
        self.key = key

    @property
    def size(self):
        return len(self.chs_regions_dct[0].matrix)

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
        bpp = (total_size * 8) / self.size ** 2
        return bpp

    @property
    def fact_bpp(self):
        wm_w, wm_h = self.key.wm_shape
        ch_count = len(self.chs_regions_dct)
        return (8 * ch_count * wm_w * wm_h) / self.size ** 2


def int_to_byte(int_):
    return struct.pack('=i', int_)


def ints_to_bytes(ints, type_):
    return np.array(ints).astype(type_).tobytes()


def byte_to_int(byte_):
    return struct.unpack('=i', byte_)[0]


def read_int(file):
    bytes_ = file.read(struct.calcsize('=i'))
    return byte_to_int(bytes_)


def read_bits(file, size):
    return np.unpackbits(np.fromfile(file, np.uint8, size))


def size_of_chs(chs):
    return sum(len(ch) for ch in chs)
