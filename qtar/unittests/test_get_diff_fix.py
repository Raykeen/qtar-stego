from unittest import TestCase

import numpy as np

from qtar.core.permutation import MatrixRegions, get_diff_fix, fix_diff


class TestGetDiffFix(TestCase):
    def setUp(self):
        rects = [
            (0, 0, 2, 2),
            (2, 0, 4, 2),
            (0, 2, 2, 4),
            (2, 2, 4, 4)
        ]

        base_mx = np.arange(16).reshape((4, 4))
        self.base = MatrixRegions(
            rects,
            base_mx
        )

        new_mx = np.copy(base_mx)
        new_mx[1][1], new_mx[1][2] = new_mx[1][2], new_mx[1][1]
        new_mx[3][1], new_mx[3][2] = new_mx[3][2], new_mx[3][1]
        self.new = MatrixRegions(
            rects,
            new_mx
        )

        self.fix = {
            0: np.array([5]),
            1: np.array([6]),
            2: np.array([13]),
            3: np.array([14])
        }

    def test_get_diff_fix(self):
        self.assertEqual(self.fix, get_diff_fix(self.base, self.new))

    def test_fix_diff(self):
        np.testing.assert_array_equal(self.base.matrix, fix_diff(self.new, self.fix).matrix)


