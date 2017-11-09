from unittest import TestCase

from numpy.testing import assert_array_equal
import numpy as np

from qtar.core.zigzag import zigzag, zigzag_embed_to_cfregions, zigzag_extract_from_cfregions
from qtar.core.matrixregion import MatrixRegions
from qtar.core.curvefitting import CFRegions


class TestZigzag(TestCase):
    def test_zigzag(self):
        actual = zigzag((5, 5))
        ideal = np.array([
            [0,  1,  5,  6,  14],
            [2,  4,  7,  13, 15],
            [3,  8,  12, 16, 21],
            [9,  11, 17, 20, 22],
            [10, 18, 19, 23, 24]
        ])
        assert_array_equal(actual, ideal)

    def test_zigzag_embed_to_cfregions(self):
        container = np.zeros((16, 16)).astype(int)

        rects = [
            (0, 0, 8, 8),
            (8, 0, 16, 8),
            (0, 8, 8, 16),
            (8, 8, 12, 12),
            (12, 8, 16, 12),
            (8, 12, 12, 16),
            (12, 12, 16, 16)
        ]

        container_mr = MatrixRegions(rects, container)

        for i, region in enumerate(container_mr):
            container_mr[i] = np.arange(region.size).reshape(region.shape) + i * 1000

        curves = [
            (3, 2, 3),
            (3, 2, 8),
            (5, 5, 5),
            (4, 4, 4),
            (3, 3, 3),
            (2, 2, 2),
            (0, 0, 0)
        ]

        container_cfr = CFRegions.from_regions(container_mr, curves, 1)

        wm = np.zeros((8, 8)).astype(int)

        wm_rects = (0, 0, 4, 4), (4, 0, 8, 4), (0, 4, 4, 8), (4, 4, 8, 8)

        wm_mr = MatrixRegions(wm_rects, wm)

        for i, region in enumerate(wm_mr):
            wm_mr[i] = (np.arange(region.size).reshape(region.shape) + i * 1000) * -1

        embedded = zigzag_embed_to_cfregions(wm_mr, container_cfr)
        extracted = zigzag_extract_from_cfregions(embedded, (8, 8), 4)

        assert_array_equal(extracted.matrix, wm_mr.matrix)

    def test_zigzag_embed_to_cfregions_2(self):
        container = np.zeros((16, 16)).astype(int)

        rects = [
            (0, 0, 8, 8),
            (8, 0, 16, 8),
            (0, 8, 8, 16),
            (8, 8, 12, 12),
            (12, 8, 16, 12),
            (8, 12, 12, 16),
            (12, 12, 16, 16)
        ]

        container_mr = MatrixRegions(rects, container)

        for i, region in enumerate(container_mr):
            container_mr[i] = np.arange(region.size).reshape(region.shape) + i * 1000

        curves = [
            (2, 1, 2),
            (2, 1, 4),
            (3, 3, 3),
            (1, 1, 1),
            (1, 1, 2),
            (2, 2, 2),
            (2, 2, 2)
        ]

        container_cfr = CFRegions.from_regions(container_mr, curves, 2)

        wm = np.zeros((8, 8)).astype(int)

        wm_rects = (0, 0, 4, 4), (4, 0, 8, 4), (0, 4, 4, 8), (4, 4, 8, 8)

        wm_mr = MatrixRegions(wm_rects, wm)

        for i, region in enumerate(wm_mr):
            wm_mr[i] = (np.arange(region.size).reshape(region.shape) + i * 1000) * -1

        embedded = zigzag_embed_to_cfregions(wm_mr, container_cfr)
        extracted = zigzag_extract_from_cfregions(embedded, (8, 8), 4)

        assert_array_equal(extracted.matrix.astype(int), wm_mr.matrix)
