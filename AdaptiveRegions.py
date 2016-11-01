from QuantizationMatrix import QuantizationMatrix


class AdaptiveRegions:
    def __init__(self, qtree):
        self.image = qtree.root_node.image
        self.qtree = qtree
        self.regions = self.find_regions()

    def find_regions(self):
        for leave in self.qtree.leaves:
            base_region = leave.get_region()
            quantization_matrix = QuantizationMatrix.get_matrix(leave.size)
            quantized = base_region / quantization_matrix
        return 0
