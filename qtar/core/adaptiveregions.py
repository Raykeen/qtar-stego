from numpy import uint8

from qtar.core.quantizationmatrix import generate_quantization_matrix
from qtar.core.matrixregion import MatrixRegions


def adapt_regions(regions, q_power=None, ar_indexes=None):
    if ar_indexes is None:
        ar_indexes = _find_ar_indexes(regions, q_power)
    ar_regions = _adapt_by_ar_indexes(regions, ar_indexes)
    return ar_regions, ar_indexes


def _find_ar_indexes(regions, q_power):
    ar_indexes = list()
    for region in regions:
        h, w = region.shape
        if h != w:
            raise RegionShapeError("Regions must have square shape")
        size = h
        quantization_matrix = generate_quantization_matrix(size)
        quantized = uint8(region / (quantization_matrix * q_power))
        if quantized[-1, -1] != 0:
            ar_indexes.append(size)
            continue
        for xy in range(0, size):
            aregion = quantized[xy:size][xy:size]
            if not aregion.any():
                ar_indexes.append(xy)
                break
    return ar_indexes


def _adapt_by_ar_indexes(regions, ar_indexes):
    ar_rects = list()
    for ar_index, rect in zip(ar_indexes, regions.rects):
        x0, y0, x1, y1 = rect
        new_rect = [x0 + ar_index, y0 + ar_index, x1, y1]
        ar_rects.append(new_rect)
    ar_regions = MatrixRegions(ar_rects, regions.matrix)
    return ar_regions


class RegionShapeError(Exception):
    pass
