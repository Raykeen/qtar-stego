from itertools import count, chain, zip_longest
from functools import lru_cache
from copy import copy

import numpy as np

from qtar.core.matrixregion import MatrixRegions, divide_into_equal_regions
from qtar.core.curvefitting import CFRegions


SCALE = 1


def zigzag_embed_to_cfregions(wm_regions, cf_regions: CFRegions):
    wm_iter = zigzag_order_regions(wm_regions)
    wm_by_regions = sort_wm_by_regions(wm_iter, cf_regions)

    result_regions = CFRegions(cf_regions.rects, copy(cf_regions.matrix), cf_regions.curves, cf_regions.grid_size)

    for i, region, wm_data in zip(count(), result_regions.columned_regions(), wm_by_regions):
        x0, y0, x1, y1 = cf_regions.rects[i]
        shape = y1 - y0, x1 - x0
        height, width = shape

        zz_order = zigzag_order(shape)
        indices = iter(zz_order[::-1])

        for wm_data_item in wm_data:
            while True:
                y, x = next(indices)
                y = y - (height - region[x].size)

                if y < 0:
                    continue

                try:
                    region[x][y] = wm_data_item
                    break
                except IndexError:
                    continue

        result_regions.set_cfregion_columns(result_regions.rects[i], result_regions.curves[i], region)

    return result_regions


def zigzag_extract_from_cfregions(cf_regions: CFRegions, wm_shape, wm_block_size):
    wm_mx = np.zeros(wm_shape)
    wm_regions = divide_into_equal_regions(wm_mx, wm_block_size)
    wm_regions_sizes = [wm_region.size for wm_region in wm_regions]
    wm_data_by_regions = []

    for i, region in enumerate(cf_regions.columned_regions()):
        x0, y0, x1, y1 = cf_regions.rects[i]
        shape = y1 - y0, x1 - x0
        height, width = shape

        size = cf_regions.get_cfregion_size(i)

        zz_order = zigzag_order(shape)
        indices = iter(zz_order[::-1])

        wm_data = []

        for _ in range(size):
            while True:
                y, x = next(indices)
                y = y - (height - region[x].size)

                if y < 0:
                    continue

                try:
                    wm_data.append(region[x][y])
                    break
                except IndexError:
                    continue

        wm_data_by_regions.append(wm_data)

    wm_data_flat = interweave(wm_data_by_regions)
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


def zigzag_embed_to_regions(wm_regions, mx_regions: MatrixRegions):
    wm_iter = zigzag_order_regions(wm_regions)
    wm_by_regions = sort_wm_by_regions(wm_iter, mx_regions)

    result_regions = MatrixRegions(mx_regions.rects, copy(mx_regions.matrix))

    for i, region, wm_data in zip(count(), mx_regions, wm_by_regions):
        size = region.size
        np_wm_data = np.array(wm_data)[::-1]

        if size > np_wm_data.size:
            zz_region = zigzag_from_mx(region)
            np_wm_data = np.append(zz_region[0:size - np_wm_data.size], np_wm_data)

        result_regions[i] = zigzag_to_mx(np_wm_data, region.shape)

    return result_regions


def zigzag_extract_from_regions(mx_regions, wm_shape, wm_block_size):
    wm_mx = np.zeros(wm_shape)
    wm_regions = divide_into_equal_regions(wm_mx, wm_block_size)
    wm_regions_sizes = [wm_region.size for wm_region in wm_regions]
    wm_data_by_regions = [zigzag_from_mx(region)[::-1] for region in mx_regions]
    wm_data_flat = interweave(wm_data_by_regions)
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


def zigzag_from_mx(mx):
    zz = np.zeros(mx.size)
    zz.flat[zigzag(mx.shape)] = mx
    return zz


def zigzag_to_mx(zz, shape):
    return zz[zigzag(shape)]


def zigzag_order_regions(regions):
    zigzags = [zigzag_from_mx(region) for region in regions]
    return interweave(zigzags)


def interweave(arrays):
    iters = [iter(array) for array in arrays]
    finished = [False for _ in iters]
    while not all(finished):
        for i, it, is_finished in zip(count(), iters, finished):
            if is_finished:
                continue
            try:
                yield next(it)
            except StopIteration:
                finished[i] = True


@lru_cache(maxsize=None)
def zigzag(shape):
    h, w = shape

    def move(i, j, n):
        if j < (n - 1):
            return max(0, i-1), j+1
        else:
            return i+1, j

    a = np.zeros((h, w))
    x, y = 0, 0
    for v in range(w * h):
        a[y][x] = v
        if (x + y) & 1:
            x, y = move(x, y, h)
        else:
            y, x = move(y, x, w)

    return a.astype(int)


# @lru_cache(maxsize=None)
def zigzag_order(shape):
    h, w = shape

    def move(i, j, n):
        if j < (n - 1):
            return max(0, i-1), j+1
        else:
            return i+1, j

    a = []
    x, y = 0, 0
    for v in range(w * h):
        a.append((y, x))
        if (x + y) & 1:
            x, y = move(x, y, h)
        else:
            y, x = move(y, x, w)

    return a