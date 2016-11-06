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
        for region in self.base_regions:
            origin_region = region.get_region()
            quantization_matrix = QuantizationMatrix.get_matrix(region.size)
            quantized = uint8(origin_region / (quantization_matrix * self.quant_power))
            if quantized[-1, -1] != 0:
                aregions_indexes.append(region.size)
                continue
            for xy in range(0, region.size):
                aregion = quantized[xy:region.size][xy:region.size]
                if not aregion.any():
                    aregions_indexes.append(xy)
                    break
        return aregions_indexes

    def _get_adaptive_regions(self):
        aregions = list()
        for i in range(0, len(self.base_regions)):
            x0, y0, x1, y1 = self.base_regions[i].rect
            new_x0 = x0 + self.indexes[i]
            new_y0 = y0 + self.indexes[i]
            new_region = MatrixRegion([new_x0, new_y0, x1, y1], self.base_regions[i].matrix)
            aregions.append(new_region)
        return aregions