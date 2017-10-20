from unittest import TestCase

import numpy as np

np.set_printoptions(threshold=np.inf)

from qtar.core.curvefitting import CFRegions

SIZE = 32

# TODO: fix test

# class TestCFRegion(TestCase):
#     def setUp(self):
#         self.mx = np.arange(SIZE**2).reshape((SIZE, SIZE))
#         self.rects = [(0, 0, SIZE, SIZE)]
#
#     def test0_get_region(self):
#         curves = [(3, 2, 2)]
#         cfr = CFRegions(self.rects, self.mx, curves)
#
#         result = np.concatenate([
#             column[24:] if x < 16 else column[0:]
#             for x, column in enumerate(self.mx.T)
#         ])
#
#         np.testing.assert_array_equal(cfr[0], result)
#         self.assertEqual(cfr.get_cfregion_size(0), 8 ** 2 * 10)
#
#     def test1_get_region(self):
#         curves = [(3, 2, 3)]
#         cfr = CFRegions(self.rects, self.mx, curves)
#
#         result = np.concatenate([
#             column[24:] if x < 16 else column[16:] if x < 24 else column[0:]
#             for x, column in enumerate(self.mx.T)
#         ])
#
#         np.testing.assert_array_equal(cfr[0], result)
#         self.assertEqual(cfr.get_cfregion_size(0), 8 ** 2 * 8)
#
#     def test2_get_region(self):
#         curves = [(2, 2, 2)]
#         cfr = CFRegions(self.rects, self.mx, curves)
#
#         result = np.concatenate([
#             column[16:] if x < 16 else column[0:]
#             for x, column in enumerate(self.mx.T)
#         ])
#
#         np.testing.assert_array_equal(cfr[0], result)
#         self.assertEqual(cfr.get_cfregion_size(0), 8 ** 2 * 12)
#
#     def test3_get_region(self):
#         curves = [(4, 1, 4)]
#         cfr = CFRegions(self.rects, self.mx, curves)
#
#         result = np.concatenate([
#             column[32:] if x < 8 else column[8:]
#             for x, column in enumerate(self.mx.T)
#         ])
#
#         np.testing.assert_array_equal(cfr[0], result)
#         self.assertEqual(cfr.get_cfregion_size(0), 8 ** 2 * 9)
#
#     def test_set_cfregion(self):
#         curves = [(3, 2, 2)]
#         cfr = CFRegions(self.rects, self.mx.copy(), curves)
#
#         cfr[0] = np.zeros(8 ** 2 * 10)
#
#         result = self.mx.copy()
#
#         result[24:32, 0:16] = 0
#         result[:, 16:32] = 0
#
#         np.testing.assert_array_equal(cfr.matrix, result)
