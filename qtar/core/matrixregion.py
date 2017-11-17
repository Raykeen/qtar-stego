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
        return sum(self.rect_size(i) for i in range(len(self.rects)))

    def rect_size(self, i):
        return rect_size(self.rects[i])


def draw_borders_on(matrix, rects, value, only_right_bottom=False):
    matrix = np.copy(matrix)

    for rect in rects:
        if rect_size(rect) == 0:
            continue

        x0, y0, x1, y1 = rect
        matrix[y1-1, x0:x1] = value
        matrix[y0:y1, x1-1] = value
        if not only_right_bottom:
            matrix[y0, x0:x1] = value
            matrix[y0:y1, x0] = value

    return matrix


def draw_borders(regions, value, only_right_bottom=False):
    return draw_borders_on(regions.matrix, regions.rects, value, only_right_bottom)


def divide_into_equal_regions(matrix, region_size):
    height, width = matrix.shape
    rects = [
        (x, y, x + region_size, y + region_size)
        for y in range(0, height, region_size) for x in range(0, width, region_size)
    ]

    return MatrixRegions(rects, matrix)


def rect_size(rect):
    x0, y0, x1, y1 = rect
    return (x1 - x0) * (y1 - y0)