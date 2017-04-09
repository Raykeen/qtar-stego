from numpy import uint8

from qtar.core.quantizationmatrix import generate_quantization_matrix
from qtar.core.matrixregion import MatrixRegions


def adapt_regions(regions, q_power=None, a_indexes=None):
    if a_indexes is None:
        a_indexes = _find_a_indexes(regions, q_power)
    a_regions = _adapt_by_a_indexes(regions, a_indexes)
    return a_regions, a_indexes


def _find_a_indexes(regions, q_power):
    a_indexes = list()
    for region in regions:
        h, w = region.shape
        if h != w:
            raise RegionShapeError("Regions must have square shape")
        size = h
        quantization_matrix = generate_quantization_matrix(size)
        quantized = uint8(region / (quantization_matrix * q_power))
        if quantized[-1, -1] != 0:
            a_indexes.append(size)
            continue
        for xy in range(0, size):
            aregion = quantized[xy:size][xy:size]
            if not aregion.any():
                a_indexes.append(xy)
                break
    return a_indexes


def _adapt_by_a_indexes(regions, a_indexes):
    a_rects = list()
    for a_index, rect in zip(a_indexes, regions.rects):
        x0, y0, x1, y1 = rect
        new_rect = [x0 + a_index, y0 + a_index, x1, y1]
        a_rects.append(new_rect)
    a_regions = MatrixRegions(a_rects, regions.matrix)
    return a_regions


class RegionShapeError(Exception):
    pass
