import numpy as np


class MatrixRegions(object):
    def __init__(self, rects, matrix):
        self.matrix = matrix
        self.rects = rects

    def __getitem__(self, i):
        mx_region = self.get_region(self.rects[i])
        return mx_region

    def __setitem__(self, i, value):
        self.set_region(self.rects[i], value)

    def __len__(self):
        return len(self.rects)

    def get_region(self, rect):
        x0, y0, x1, y1 = rect
        return self.matrix[y0:y1, x0:x1]

    def set_region(self, rect, value):
        x0, y0, x1, y1 = rect
        self.matrix[y0:y1, x0:x1] = value

    @property
    def total_size(self):
            total_size = 0
            for i in range(len(self.rects)):
                total_size += self.rect_size(i)
            return total_size

    def rect_size(self, i):
        x0, y0, x1, y1 = self.rects[i]
        return (x1 - x0) * (y1 - y0)


def draw_borders_on(matrix, rects, value, only_right_bottom=False):
    matrix = np.copy(matrix)
    for rect in rects:
        x0, y0, x1, y1 = rect
        matrix[y1-1, x0:x1] = value
        matrix[y0:y1, x1-1] = value
        if not only_right_bottom:
            matrix[y0, x0:x1] = value
            matrix[y0:y1, x0] = value

    return matrix


def draw_borders(regions, value, only_right_bottom=False):
    return draw_borders_on(regions.matrix, regions.rects, value, only_right_bottom)
