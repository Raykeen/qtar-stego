from unittest import TestCase

import numpy as np

from qtar.core.imageqt import ImageQT


class TestImageQT(TestCase):
    def setUp(self):
        mx = np.array([
            [0, 1, 2, 3],
            [4, 255, 6, 7],
            [0, 9, 127, 0],
            [128, 13, 14, 128]
        ])

        self.qt = ImageQT(mx, 1, 4, 0.5)

    def test_rects(self):
        rects = [
            (0, 0, 2, 2),
            (2, 0, 4, 2),
            (0, 2, 2, 4),
            (2, 2, 3, 3),
            (3, 2, 4, 3),
            (2, 3, 3, 4),
            (3, 3, 4, 4)
        ]

        self.assertEqual(self.qt.rects, rects, "wrong blocks dividing")

    def test_regions(self):
        regions = [
            [[0, 1],
             [0, 0]],
            [[2, 3],
             [4, 6]],
            [[7,  9],
             [13, 14]],
            [[127]],
            [[128]],
            [[128]],
            [[255]]
        ]

        qt_regions = [region.tolist() for region in self.qt]

        self.assertEqual(qt_regions, regions, "get wrong regions")

    def test_depth(self):
        self.assertEqual(self.qt.max_depth, 2, "wrong depth calculation")

    def test_key(self):
        key = [1,
                0,
                0,
                0,
                1,
                 0,
                 0,
                 0,
                 0
               ]

        self.assertEqual(self.qt.key, key, "wrong key generation")

    def test_permutation(self):
        permutation = [
            [0, 1, 2, 3],
            [8, 11, 4, 6],
            [7, 9, 10, 12],
            [13, 14, 15, 5]
        ]

        self.assertEqual(self.qt.permutation.tolist(), permutation, "wrong permutation generation")
