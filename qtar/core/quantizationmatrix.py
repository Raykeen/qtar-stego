from scipy.ndimage.interpolation import zoom
from numpy import asarray
from functools import lru_cache

MATRIX = [
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
]

TO_FLAT_MATRIX = [
    [ 20,  5,  1, 1, 1, 1, 1, 1],
    [  5,  1,  1, 1, 1, 1, 1, 1],
    [  1,  1,  1, 1, 1, 1, 1, 1],
    [  1,  1,  1, 1, 1, 1, 1, 1],
    [  1,  1,  1, 1, 1, 1, 1, 1],
    [  1,  1,  1, 1, 1, 1, 1, 1],
    [  1,  1,  1, 1, 1, 1, 1, 1],
    [  1,  1,  1, 1, 1, 1, 1, 1]
]


@lru_cache(maxsize=None)
def generate_quantization_matrix(n=8):
    return zoom(asarray(MATRIX), n / 8, order=1, mode='nearest')


@lru_cache(maxsize=None)
def generate_flat_matrix(n=8):
    return zoom(asarray(TO_FLAT_MATRIX), n / 8, order=1, mode='nearest')