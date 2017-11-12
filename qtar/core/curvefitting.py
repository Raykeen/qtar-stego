import math
from itertools import islice, count

import numpy as np
from PIL import Image, ImageDraw

from qtar.core.matrixregion import MatrixRegions, draw_borders
from qtar.core.quantizationmatrix import generate_quantization_matrix


class CFRegions(MatrixRegions):
    def __init__(self, rects, matrix, curves, grid_size=8):
        super().__init__(rects, matrix)
        self.curves = curves
        self.grid_size = grid_size

    def __getitem__(self, i):
        mx_region = self.get_cfregion(self.rects[i], self.curves[i])
        return mx_region

    def __setitem__(self, i, value):
        self.set_cfregion(self.rects[i], self.curves[i], value)

    def get_cfregion_size(self, i):
        rect = self.rects[i]
        curve = self.curves[i]

        x0, y0, x1, y1 = rect

        height, width = y1 - y0, x1 - x0

        normal_curve = [coord * self.grid_size for coord in curve]

        size = 0
        for x in range(width):
            y = math.ceil(curve_func(normal_curve, x))
            col_h = height - y
            col_h = col_h if col_h >= 0 else 0
            size += col_h

        return size

    def get_cfregion_columns(self, rect, curve):
        rect_region = super().get_region(rect)
        normal_curve = [coord * self.grid_size for coord in curve]
        return [
            column[math.ceil(curve_func(normal_curve, x)):]
            for x, column in enumerate(rect_region.T)  # column wise
        ]

    def get_cfregion(self, *args):
        return np.concatenate(self.get_cfregion_columns(*args))

    def columned_regions(self):
        for rect, curve in zip(self.rects, self.curves):
            yield self.get_cfregion_columns(rect, curve)

    def set_cfregion_columns(self, rect, curve, value):
        region = self.get_region(rect)
        height, width = region.shape
        normal_curve = [coord * self.grid_size for coord in curve]

        for x in range(width):
            y = math.ceil(curve_func(normal_curve, x))
            region[y:, x] = value[x]

    def set_cfregion(self, rect, curve, value):
        region = self.get_region(rect)
        height, width = region.shape
        val_iter = iter(value)
        normal_curve = [coord * self.grid_size for coord in curve]

        for x in range(width):
            y = math.ceil(curve_func(normal_curve, x))
            col_height = max(0, height - y)
            col_value = np.array(list(islice(val_iter, col_height)))
            region[y:, x] = col_value

    @classmethod
    def from_regions(cls, mregions, curves, cf_grid_size):
        return cls(mregions.rects, mregions.matrix, curves, cf_grid_size)

    @property
    def total_size(self):
        total_size = 0
        for i in range(len(self.curves)):
            total_size += self.get_cfregion_size(i)
        return total_size


def aligned_curve_func(curve, x, grid_size=8):
    result = math.ceil(curve_func(curve, x // grid_size)) * grid_size
    return result


def curve_func(curve, x):
    Ay, B, Cx = curve

    if x < B:
        y = (x / B) * (B - Ay) + Ay
    else:
        if Cx == B:
            y = 0
        else:
            y = ((B - x) / (Cx - B) + 1) * B

    return y if y > 0 else 0


def fit_cfregions(dct_regions, q_power, grid_size):
    curves = []

    for region in dct_regions:
        height, width = region.shape
        if height != width:
            raise Exception("Regions must have square shape")
        size = height
        quantization_matrix = generate_quantization_matrix(size)
        quantized = np.uint8(region / (quantization_matrix * q_power))
        nonzero_y_indices, nonzero_x_indices = np.nonzero(quantized)
        significant_area_width = nonzero_x_indices.max()
        significant_area_height = nonzero_y_indices.max()
        try:
            significant_area_diagonal = max(x for x, y in zip(nonzero_x_indices, nonzero_y_indices) if x == y)

            curves.append((
                math.ceil((significant_area_height + 1) / grid_size),
                math.ceil((significant_area_diagonal + 1) / grid_size),
                math.ceil((significant_area_width + 1) / grid_size)
            ))
        except ValueError:
            curves.append((height / grid_size, height / grid_size, width / grid_size))

    return CFRegions.from_regions(dct_regions, curves, grid_size)


def draw_cf_map(cfregions, value=255, only_right_bottom=True):
    mx_with_borders = draw_borders(cfregions, value, only_right_bottom)
    result_regions = MatrixRegions(cfregions.rects, mx_with_borders)

    for i, region, curve in zip(count(), result_regions, cfregions.curves):
        Ay, B, Cx = curve
        region_img = Image.fromarray(region)
        draw = ImageDraw.Draw(region_img)
        draw.line([
            (0, Ay * cfregions.grid_size),
            (B * cfregions.grid_size, B * cfregions.grid_size),
            (Cx * cfregions.grid_size, 0)
        ], fill=value)
        result_regions[i] = np.array(region_img)

    return result_regions.matrix
