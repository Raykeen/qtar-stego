import numpy as np


class MatrixRegions(object):
    def __init__(self, rects, matrix):
        self.matrix = matrix
        self.rects = rects
        self.count = len(rects)

    def __getitem__(self, i):
        mx_region = self.get_region(self.rects[i])
        return mx_region

    def __setitem__(self, key, value):
        x0, y0, x1, y1 = self.rects[key]
        h = y1 - y0
        w = x1 - x0
        for y, i in zip(range(y0, y1), range(0, h)):
            for x, j in zip(range(x0, x1), range(0, w)):
                self.matrix[y][x] = value[i][j]

    def get_region(self, region):
        x0, y0, x1, y1 = region
        return self.matrix[x0:x1, y0:y1]

    def get_matrix_with_borders(self, value=255, only_right_bottom=False):
        matrix = np.copy(self.matrix)
        for region in self.rects:
            x0, y0, x1, y1 = region
            for x in range(x0, x1 - 1):
                matrix[x][y1 - 1] = value
                if not only_right_bottom:
                    matrix[x][y0] = value

            for y in range(y0, y1 - 1):
                matrix[x1 - 1][y] = value
                if not only_right_bottom:
                    matrix[x0][y] = value

        return matrix
