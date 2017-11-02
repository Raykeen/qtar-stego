from itertools import count, chain, zip_longest, islice
from copy import copy
import math

import numpy as np

from qtar.core.matrixregion import MatrixRegions, divide_into_equal_regions


SCALE = 1


def zigzag_embed_to_regions(wm_regions, mx_regions):
    wm_iter = zigzag_order_regions(wm_regions)
    wm_by_regions = sort_wm_by_regions(wm_iter, mx_regions)

    result_regions = MatrixRegions(mx_regions.rects, copy(mx_regions.matrix))

    for i, region, wm_data in zip(count(), mx_regions, wm_by_regions):
        size = region.size
        np_wm_data = np.array(wm_data)[::-1]

        if size > np_wm_data.size:
            zz_region = zigzag_mx(region)
            np_wm_data = np.append(zz_region[0:size - np_wm_data.size], np_wm_data)

        result_regions[i] = zigzag_to_mx(np_wm_data, region.shape)

    return result_regions


def zigzag_extract_from_regions(mx_regions, wm_shape, wm_block_size):
    wm_mx = np.zeros(wm_shape)
    wm_regions = divide_into_equal_regions(wm_mx, wm_block_size)
    wm_regions_sizes = [wm_region.size for wm_region in wm_regions]
    wm_data_by_regions = [zigzag_mx(region)[::-1] for region in mx_regions]
    wm_data_flat = filter(lambda x: x != '', chain.from_iterable(zip_longest(*wm_data_by_regions, fillvalue='')))
    wm_flat_regions = [[] for _ in range(len(wm_regions))]
    wm_flat_regions_filled = [False for _ in range(len(wm_regions))]

    while not all(wm_flat_regions_filled):
        for i, wm_region_size, wm_flat_region in zip(count(), wm_regions_sizes, wm_flat_regions):
            if len(wm_flat_region) < wm_region_size:
                try:
                    wm_flat_regions[i].append(next(wm_data_flat) * SCALE)
                except StopIteration:
                    break
            else:
                wm_flat_regions_filled[i] = True

    for i, wm_region in enumerate(wm_flat_regions):
        shape = wm_regions[i].shape
        wm_regions[i] = zigzag_to_mx(np.array(wm_region), shape)

    return wm_regions


def sort_wm_by_regions(wm_iter, mx_regions):
    regions_sizes = [region.size for region in mx_regions]
    wm_data_by_regions = [[] for _ in mx_regions]

    while True:
        for i, wm_data, region_size in zip(count(), wm_data_by_regions, regions_sizes):
            if len(wm_data) >= region_size:
                continue
            try:
                wm_data = next(wm_iter) / SCALE
                wm_data_by_regions[i].append(wm_data)
            except StopIteration:
                break
        else:
            continue
        break

    return wm_data_by_regions


def zigzag_mx(mx):
    return mx.flat[zigzag_order(mx.shape)]


def zigzag_to_mx(zz, shape):
    return zz[generate_zigzag_mx(shape)]


def zigzag_order_regions(regions):
    zigzags = [iter(zigzag_mx(region)) for region in regions]
    while zigzags:
        for i, zz in enumerate(zigzags):
            try:
                yield next(zz)
            except StopIteration:
                del zigzags[i]


def zigzag_order(shape):
    height, width = shape

    def sort_f(index):
        y, x = divmod(index, width)
        return x + y, y if (x + y) % 2 else -y

    index_order = sorted(range(height * width), key=sort_f)
    return index_order


def generate_zigzag_mx(shape):
    zz_order = zigzag_order(shape)
    zz_order_resorted = sorted(enumerate(zz_order), key=lambda c: c[1])
    zz_mx_flat = list(zip(*zz_order_resorted))[0]

    return np.array(zz_mx_flat).reshape(shape)