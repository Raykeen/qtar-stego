import numpy as np


class MatrixRegion:
    def __init__(self, rect, matrix):
        self.matrix = matrix
        self.rect = rect
        x0, y0, x1, y1 = rect
        self.size = x1 - x0

    def get_region(self, rect=None, matrix=None):
        if not rect:
            rect = self.rect
        if matrix is None:
            matrix = self.matrix
        x0, y0, x1, y1 = rect
        return matrix[x0:x1, y0:y1]

    def each(self, func):
        x0, y0, x1, y1 = self.rect
        for x in range(x0, x1):
            for y in range(y0, y1):
                self.matrix[x][y] = func(self.matrix, x, y)

    @staticmethod
    def new_matrix_regions(regions, matrix):
        new_regions = list()
        for region in regions:
            new_regions.append(MatrixRegion(region.rect, matrix))

        return new_regions

    @staticmethod
    def get_matrix_with_borders(regions, value=255, only_right_bottom=False):
        matrix = np.copy(regions[0].matrix)
        for region in regions:
            x0, y0, x1, y1 = region.rect
            for x in range(x0, x1 - 1):
                matrix[x][y1 - 1] = value
                if not only_right_bottom:
                    matrix[x][y0] = value

            for y in range(y0, y1 - 1):
                matrix[x1 - 1][y] = value
                if not only_right_bottom:
                    matrix[x0][y] = value

        return matrix
