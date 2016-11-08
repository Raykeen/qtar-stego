from QuantizationMatrix import *
from MatrixRegion import *
from numpy import uint8


class AdaptiveRegions:
    def __init__(self, regions, quant_power, indexes=None):
        self.quant_power = quant_power
        self.base_regions = regions
        self.indexes = indexes or self._find_adaptive_regions()
        self.regions = self._get_adaptive_regions()

    def _find_adaptive_regions(self):
        aregions_indexes = list()
        for base_region in self.base_regions:
            size = base_region.shape[0]
            quantization_matrix = QuantizationMatrix.get_matrix(size)
            quantized = uint8(base_region / (quantization_matrix * self.quant_power))
            if quantized[-1, -1] != 0:
                aregions_indexes.append(size)
                continue
            for xy in range(0, size):
                aregion = quantized[xy:size][xy:size]
                if not aregion.any():
                    aregions_indexes.append(xy)
                    break
        return aregions_indexes

    def _get_adaptive_regions(self):
        arects = list()
        for i in range(0, self.base_regions.count):
            x0, y0, x1, y1 = self.base_regions.rects[i]
            new_x0 = x0 + self.indexes[i]
            new_y0 = y0 + self.indexes[i]
            new_rect = [new_x0, new_y0, x1, y1]
            arects.append(new_rect)
        aregions = MatrixRegions(arects, self.base_regions.matrix)
        return aregions
