from unittest import TestCase

import numpy as np

from qtar.core.matrixregion import divide_into_equal_regions


class TestMatrixRegion(TestCase):
    def test_divide_into_equal_regions(self):
        MX_SIZE = 16
        REGION_SIZE = 8

        mx = np.arange(MX_SIZE * MX_SIZE).reshape((MX_SIZE, MX_SIZE))

        regions = divide_into_equal_regions(mx, REGION_SIZE)
        rects = regions.rects

        self.assertEqual(rects, [(0, 0, 8, 8), (8, 0, 16, 8), (0, 8, 8, 16), (8, 8, 16, 16)])
