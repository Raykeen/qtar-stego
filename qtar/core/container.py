import struct

import numpy as np

from qtar.core.imageqt import parse_qt_key


MODE_STRUCT = '=???'

PARAMS_STRUCT = '=fiiiib'

CF_POINTS_COUNT = 3


class Key:
    def __init__(self,
                 chs_qt_key=None,
                 chs_pm_fix_key=None,
                 chs_ar_key=None,
                 chs_cf_key=None,
                 wm_shape=None,
                 ch_scale=None,
                 offset=None,
                 pm_mode=False,
                 container_shape=None,
                 cf_mode=False,
                 cf_grid_size=None,
                 wmdct_mode=False,
                 wmdct_block_size=None,
                 wmdct_scale=None
                 ):
        self.chs_qt_key = chs_qt_key or []
        self.chs_pm_fix_key = chs_pm_fix_key or []
        self.chs_cf_key = chs_cf_key or []
        self.chs_ar_key = chs_ar_key or []
        self.wm_shape = wm_shape
        self.ch_scale = ch_scale
        self.offset = offset
        self.pm_mode = pm_mode
        self.container_shape = container_shape
        self.cf_mode = cf_mode
        self.cf_grid_size = cf_grid_size
        self.wmdct_mode = wmdct_mode
        self.wmdct_block_size = wmdct_block_size
        self.wmdct_scale = wmdct_scale

    @property
    def params_bytes(self):
        bytes = struct.pack(MODE_STRUCT, self.pm_mode, self.cf_mode, self.wmdct_mode)

        chs_count = len(self.chs_qt_key)
        bytes += struct.pack(PARAMS_STRUCT,
                             self.wmdct_scale if self.wmdct_mode else self.ch_scale,
                             *self.offset,
                             *self.wm_shape,
                             chs_count)
        if self.pm_mode:
            bytes += int_to_byte(self.container_shape[0]) + int_to_byte(self.container_shape[0])

        if self.cf_mode:
            bytes += int_to_byte(self.cf_grid_size)

        if self.wmdct_mode:
            bytes += int_to_byte(self.wmdct_block_size)

        return bytes

    @staticmethod
    def cf_key_type(cf_grid_size):
        if cf_grid_size == 1:
            return np.uint16
        else:
            return np.uint8

    @property
    def chs_qt_key_bytes(self):
        result = []

        for qt_key in self.chs_qt_key:
            key_bytes = np.packbits(qt_key).tobytes()
            result.append(int_to_byte(len(key_bytes)) + key_bytes)

        return result

    @property
    def chs_pm_fix_key_bytes(self):
        result = []

        for pm_fix_key in self.chs_pm_fix_key:
            pm_fix_key_bytes = bytes()
            pm_fix_key_len = int_to_byte(len(pm_fix_key))
            for fix in pm_fix_key:

                fix_len = len(fix)
                pm_fix_key_bytes += (int_to_byte(fix_len)
                                     + np.array(fix).astype(np.uint32).tobytes())

            result.append(pm_fix_key_len + pm_fix_key_bytes)
        return result

    @property
    def chs_ar_key_bytes(self):
        return [ints_to_bytes(ar_key, np.uint8) for ar_key in self.chs_ar_key]

    @property
    def chs_cf_key_bytes(self):
        result = []

        for cf_key in self.chs_cf_key:
            flat_key = np.array(cf_key).flat
            key_bytes = ints_to_bytes(flat_key, self.cf_key_type(self.cf_grid_size))
            result.append(key_bytes)
        return result

    @property
    def params_size(self):
        return len(self.params_bytes)

    @property
    def qt_key_size(self):
        return size_of_chs(self.chs_qt_key_bytes)

    @property
    def pm_fix_key_size(self):
        return size_of_chs(self.chs_pm_fix_key_bytes)

    @property
    def ar_key_size(self):
        return size_of_chs(self.chs_ar_key_bytes)

    @property
    def cf_key_size(self):
        return size_of_chs(self.chs_cf_key_bytes)

    @property
    def size(self):
        return self.params_size + self.qt_key_size + self.pm_fix_key_size + self.ar_key_size + self.cf_key_size

    def save(self, path):
        with open(path, 'wb') as file:
            key_bytes = self.params_bytes
            for ch_n in range(len(self.chs_qt_key)):
                key_bytes += self.chs_qt_key_bytes[ch_n]

                if self.cf_mode:
                    key_bytes += self.chs_cf_key_bytes[ch_n]
                else:
                    key_bytes += self.chs_ar_key_bytes[ch_n]

                if self.pm_mode:
                    key_bytes += self.chs_pm_fix_key_bytes[ch_n]

            file.write(key_bytes)
        return len(key_bytes)

    @classmethod
    def open(cls, path):
        with open(path, 'rb') as file:
            mode_bytes = file.read(struct.calcsize(MODE_STRUCT))
            pm_mode, cf_mode, wmdct_mode = struct.unpack(MODE_STRUCT, mode_bytes)

            params_bytes = file.read(struct.calcsize(PARAMS_STRUCT))

            scale, x, y, wm_w, wm_h, chs_count = struct.unpack(PARAMS_STRUCT, params_bytes)

            offset = x, y
            wm_shape = wm_w, wm_h

            container_shape = None
            if pm_mode:
                c_w = read_int(file)
                c_h = read_int(file)
                container_shape = c_w, c_h

            cf_grid_size = None
            if cf_mode:
                cf_grid_size = read_int(file)

            wmdct_block_size = None
            ch_scale = None
            wmdct_scale = None
            if wmdct_mode:
                wmdct_scale = scale
                wmdct_block_size = read_int(file)
            else:
                ch_scale = scale

            chs_qt_key = []
            chs_ar_key = []
            chs_cf_key = []
            chs_pm_fix_key = []

            for ch in range(chs_count):
                qt_key_bytes_size = read_int(file)
                qt_key = read_bits(file, qt_key_bytes_size)
                qt_key, block_count = parse_qt_key(qt_key.tolist())
                chs_qt_key.append(qt_key)

                if cf_mode:
                    cf_key_flat = np.fromfile(file, cls.cf_key_type(cf_grid_size), block_count * CF_POINTS_COUNT)
                    cf_key = [tuple(curve.astype(np.int)) for curve in np.split(cf_key_flat, block_count)]
                    chs_cf_key.append(cf_key)
                else:
                    ar_key = np.fromfile(file, np.uint8, block_count).tolist()
                    chs_ar_key.append(ar_key)

                if pm_mode:
                    pm_fix_key_len = read_int(file)
                    pm_fix_key = []
                    for i in range(pm_fix_key_len):
                        fix_len = read_int(file)
                        pm_fix_key.append(np.fromfile(file, np.uint32, fix_len))

                    chs_pm_fix_key.append(pm_fix_key)

        return cls(chs_qt_key,
                   chs_pm_fix_key,
                   chs_ar_key,
                   chs_cf_key,
                   wm_shape,
                   ch_scale,
                   offset,
                   pm_mode,
                   container_shape,
                   cf_mode,
                   cf_grid_size,
                   wmdct_mode,
                   wmdct_block_size,
                   wmdct_scale)


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
        total_size = sum(regions.total_size
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


def read_uint8(file, size):
    bytes_ = file.read(size)
    return np.frombuffer(bytes_, np.uint8)
