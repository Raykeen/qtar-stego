import numpy as np


class QuantizationMatrix:
    MATRIX = [
        [862, 52, 35, 20, 11, 8, 5, 3],
        [60, 48, 31, 27, 11, 7, 4, 2],
        [34, 30, 27, 25, 10, 6, 3, 2],
        [20, 18, 13, 10, 8, 5, 3, 1],
        [13, 11, 9, 7, 5, 3, 2, 1],
        [8, 7, 5, 4, 3, 2, 1, 1],
        [4, 4, 3, 2, 1, 1, 1, 0],
        [3, 2, 2, 1, 1, 1, 0, 0]
    ]

    def get_scaled_matrix(self, n=8):
        return self._interpolate_matrix(QuantizationMatrix.MATRIX, n / 8)

    @staticmethod
    def _interpolate_matrix(matrix, scale):
        if scale == 1:
            return matrix

        two_x_matrix = QuantizationMatrix._interpolate_matrix(matrix, scale / 2)
        nmatrix = np.array(two_x_matrix)
        size = nmatrix[0].size
        interpolated = np.zeros((size * 2, size * 2))
        for i in range(0, size):
            for j in range(1, size):
                interpolated[i * 2][j * 2 - 2] = int(nmatrix[i][j - 1])
                interpolated[i * 2][j * 2 - 1] = int((nmatrix[i][j - 1] + nmatrix[i][j]) / 2)
            interpolated[i * 2][size * 2 - 2] = int(nmatrix[i][size - 1])
            interpolated[i * 2][size * 2 - 1] = int(nmatrix[i][size - 1] / 2)

            if i == 0:
                continue

            for j in range(0, size):
                interpolated[i * 2 - 1][j] = int((interpolated[i * 2 - 2][j] + interpolated[i * 2][j]) / 2)

        for j in range(0, size):
            interpolated[size * 2 - 1][j] = int(interpolated[size * 2 - 2][j] / 2)

        return interpolated
