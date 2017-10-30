from unittest import TestCase

from numpy.testing import assert_array_equal
import numpy as np

from qtar.core.zigzag import generate_zigzag_mx


class TestZigzag(TestCase):
    def test_generate_zigzag_mx(self):
        actual = generate_zigzag_mx((5, 5))
        ideal = np.array([
            [0,  1,  5,  6,  14],
            [2,  4,  7,  13, 15],
            [3,  8,  12, 16, 21],
            [9,  11, 17, 20, 22],
            [10, 18, 19, 23, 24]
        ])
        assert_array_equal(actual, ideal)
