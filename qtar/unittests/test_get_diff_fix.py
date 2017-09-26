from unittest import TestCase

import numpy as np

from qtar.core.permutation import MatrixRegions, get_diff_fix, fix_diff


class TestGetDiffFix(TestCase):
    def setUp(self):
        self.rects = [
            (0, 0, 2, 2),
            (2, 0, 4, 2),
            (0, 2, 2, 4),
            (2, 2, 4, 4)
        ]

        self.base_mx = np.arange(16).reshape((4, 4))
        self.base = MatrixRegions(
            self.rects,
            self.base_mx
        )

        self.new_mx = np.copy(self.base_mx)
        self.new_mx[1][1], self.new_mx[1][2] = self.new_mx[1][2], self.new_mx[1][1]
        self.new_mx[3][1], self.new_mx[3][2] = self.new_mx[3][2], self.new_mx[3][1]
        self.new = MatrixRegions(
            self.rects,
            self.new_mx
        )

        self.fix = [
            np.array([5]),
            np.array([6]),
            np.array([13]),
            np.array([14])
        ]

    def test_get_diff_fix(self):
        self.assertEqual(self.fix, get_diff_fix(self.base_mx, self.new_mx, self.rects))

    def test_fix_diff(self):
        np.testing.assert_array_equal(self.base.matrix, fix_diff(self.new, self.fix).matrix)
