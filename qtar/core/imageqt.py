from copy import copy
from math import sqrt

import numpy as np

from qtar.core.matrixregion import MatrixRegions
from qtar.core.permutation import permutate


class QtNode:
    ROOT = 0
    BRANCH = 1
    LEAF = 2

    def __init__(self, parent, rect=None):
        self.parent = parent
        self.children = [None, None, None, None]
        self.rect = rect
        x0, y0, x1, y1 = self.rect
        self.size = x1-x0
        if not parent:
            self.depth = 0
        else:
            self.depth = parent.depth + 1

        if not self.parent:
            self.type = QtNode.ROOT
        else:
            self.type = QtNode.LEAF

    def subdivide(self):
        x0, y0, x1, y1 = self.rect

        h = int((x1 - x0) / 2)
        rects = list()
        rects.append((x0, y0, x0 + h, y0 + h))
        rects.append((x0 + h, y0, x1, y0 + h))
        rects.append((x0, y0 + h, x0 + h, y1))
        rects.append((x0 + h, y0 + h, x1, y1))
        self.type = QtNode.BRANCH
        for n in range(len(rects)):
            self.children[n] = QtNode(self, rects[n])

        return self.children


class ImageQT(MatrixRegions):
    def __init__(self, matrix, min_size=None, max_size=None, threshold=None, key=None, permutation=None):
        super().__init__([], matrix)
        self.original_mx = matrix
        self.threshold = threshold
        self.min_size = min_size
        self.max_size = max_size
        self.max_depth = 0
        self.key = key
        self.permutation = permutation
        self.all_nodes = []
        self.leaves = []
        self.root_node = QtNode(None, (0, 0, matrix.shape[1], matrix.shape[0]))

        if key is None and permutation is None:
            self.key = []
            self.permutation = np.arange(matrix.size).reshape(matrix.shape)
            self.__build_tree(self.root_node)
            self.matrix = permutate(self.matrix, self.permutation)
        else:
            self.min_size = 0
            self.max_size = 0
            self.__build_tree_from_key(self.root_node, copy(key))
            self.matrix = permutate(self.matrix, permutation)
        self.rects = [leave.rect for leave in self.leaves]

    @classmethod
    def from_keys(cls, matrix, qt_key, pm_key):
        return cls(matrix, key=qt_key, permutation=pm_key)

    def __build_tree(self, node):
        too_big = node.size > self.max_size
        too_small = node.size <= self.min_size
        self.all_nodes.append(node)

        if (not too_big and self.__spans_homogeneity(node.rect)) or too_small:
            if node.depth > self.max_depth:
                self.max_depth = node.depth
            self.key.append(False)
            self.leaves.append(node)
            return

        self.__align(node.rect)
        self.key.append(True)
        children = node.subdivide()
        for child in children:
            self.__build_tree(child)

    def __build_tree_from_key(self, node, key):
        subivide = key.pop(0)
        self.all_nodes.append(node)
        if subivide:
            children = node.subdivide()
            for child in children:
                self.__build_tree_from_key(child, key)
        else:
            if node.depth > self.max_depth:
                self.max_depth = node.depth
            if node.size > self.max_size:
                self.max_size = node.size
            if node.size < self.min_size:
                self.min_size = node.size
            self.leaves.append(node)

    def __spans_homogeneity(self, rect):
        region = self.__get_pm_region(rect)
        max_value = np.amax(region)
        min_value = np.amin(region)
        homogeneity = max_value - min_value
        if isinstance(self.threshold, (float, int)):
            return homogeneity < self.threshold * 256
        else:
            brightness = np.average(region)
            bright_types_count = len(self.threshold)
            for i in range(0, bright_types_count-1):
                bright_type_max = int(255 / bright_types_count * (i + 1))
                if brightness <= bright_type_max:
                    return homogeneity < self.threshold[i] * 256
            return homogeneity < self.threshold[-1] * 256

    def __align(self, rect):
        perm_regions = MatrixRegions([], self.permutation)
        perm_region = perm_regions.get_region(rect)
        region = self.get_region(rect)
        regions_flat = region.flat
        perm_region_flat_sorted = sorted(perm_region.flat, key=lambda k: self.original_mx.flat[k])
        size = len(regions_flat)
        subregion_size = int(size / 4)
        perm_subregions = []

        for i in range(4):
            first = subregion_size * i
            last = first + subregion_size
            flat_subregion_perm = np.array(sorted(perm_region_flat_sorted[first:last]))
            subregion_shape = int(sqrt(subregion_size))
            subregion_perm = flat_subregion_perm.reshape((subregion_shape, subregion_shape))
            perm_subregions.append(subregion_perm)

        top = np.concatenate((perm_subregions[0], perm_subregions[1]), axis=1)
        bottom = np.concatenate((perm_subregions[2], perm_subregions[3]), axis=1)
        perm_region = np.concatenate((top, bottom), axis=0)
        perm_regions.set_region(rect, perm_region)

    def __get_pm_region(self, rect):
        perm_regions = MatrixRegions([], self.permutation)
        perm = perm_regions.get_region(rect)
        region_flat = [self.original_mx.flat[p] for p in perm]
        region = np.array(region_flat).reshape(perm.shape)
        return region


def parse_qt_key(key, block_count=1, result_key=None):
    if result_key is None:
        result_key = []

    subdivide = bool(key.pop(0))
    result_key.append(subdivide)
    if subdivide:
        block_count = block_count - 1
        for i in range(4):
            result_key, block_count = parse_qt_key(key, block_count + 1, result_key)

    return result_key, block_count
