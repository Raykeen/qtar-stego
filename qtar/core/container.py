import struct

import numpy as np

from qtar.core.imageqt import parse_qt_key


class Key:
    def __init__(self, ch_scale=None, offset=None, chs_qt_key=None, chs_ar_key=None, wm_shape=None,
                 container_shape=None, chs_pm_fix_key=None):
        self.ch_scale = ch_scale
        self.offset = offset
        self.chs_qt_key = chs_qt_key or []
        self.chs_ar_key = chs_ar_key or []
        self.chs_pm_fix_key = chs_pm_fix_key or []
        self.wm_shape = wm_shape
        self.container_shape = container_shape

    def save(self, path):
        with open(path, 'wb') as file:
            chs_count = len(self.chs_qt_key)
            key_bytes = struct.pack('=fiiiiiib',
                                    self.ch_scale,
                                    *self.offset,
                                    *self.wm_shape,
                                    *self.container_shape,
                                    chs_count)

            for qt_key, ar_key, pm_fix_key in zip(self.chs_qt_key, self.chs_ar_key, self.chs_pm_fix_key):
                qt_key_packed = np.packbits(qt_key)
                qt_key_len_bytes = int_to_byte(len(qt_key_packed))

                ar_key_packed = np.array(ar_key).astype(np.uint8)

                pm_fix_key_bytes = bytes()
                pm_fix_key_len = int_to_byte(len(pm_fix_key))

                for block_n, fix in pm_fix_key.items():
                    fix_len = len(fix)
                    pm_fix_key_bytes += (int_to_byte(block_n)
                                         + int_to_byte(fix_len)
                                         + np.array(fix).astype(np.uint32).tobytes())

                # pm_key_packed = np.array(pm_key).astype(np.uint32)

                key_bytes += (qt_key_len_bytes
                              + qt_key_packed.tobytes()
                              + ar_key_packed.tobytes()
                              # + pm_key_packed.tobytes()
                              + pm_fix_key_len
                              + pm_fix_key_bytes)

            file.write(key_bytes)

    @classmethod
    def open(cls, path):
        with open(path, 'rb') as file:
            params_struct = '=fiiiiiib'
            params_bytes = file.read(struct.calcsize(params_struct))
            ch_scale, x, y, wm_w, wm_h, c_w, c_h, chs_count = struct.unpack(params_struct, params_bytes)
            offset = (x, y)
            wm_shape = (wm_w, wm_h)
            container_shape = (c_w, c_h)

            chs_qt_key = []
            chs_ar_key = []
            chs_pm_fix_key = []
            # chs_pm_key = []

            for ch in range(chs_count):
                qt_key_bytes_size = read_int(file)
                qt_key = read_bits(file, qt_key_bytes_size)

                qt_key, block_count = parse_qt_key(qt_key.tolist())
                ar_key = read_uint8(file, block_count)

                pm_fix_key_len = read_int(file)
                pm_fix_key = {}
                for i in range(pm_fix_key_len):
                    block_n = read_int(file)
                    fix_len = read_int(file)
                    pm_fix_key[block_n] = np.fromfile(file, np.uint32, fix_len)

                # pm_key = np.fromfile(file, np.uint32, c_w * c_h).reshape(container_shape)

                chs_qt_key.append(qt_key)
                chs_ar_key.append(ar_key)
                chs_pm_fix_key.append(pm_fix_key)
                # chs_pm_key.append(pm_key)

        # return cls(ch_scale, offset, chs_qt_key, chs_ar_key, chs_pm_key, wm_shape, container_shape)
        return cls(ch_scale, offset, chs_qt_key, chs_ar_key, wm_shape, container_shape, chs_pm_fix_key)


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


def byte_to_int(byte_):
    return struct.unpack('=i', byte_)[0]


def read_int(file):
    bytes_ = file.read(struct.calcsize('=i'))
    return byte_to_int(bytes_)


def read_uint8(file, size):
    bytes_ = file.read(size)
    return np.frombuffer(bytes_, np.uint8)


def read_bits(file, size):
    return np.unpackbits(read_uint8(file, size))