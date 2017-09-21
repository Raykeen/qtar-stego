from math import sqrt
from itertools import count

from numpy import array, concatenate, arange, zeros
import numpy as np

from qtar.core.matrixregion import MatrixRegions


def build_qt_permutation(qt):
    root = qt.root_node
    matrix = qt.matrix
    permutation = arange(matrix.size).reshape(matrix.shape)
    perm_regions = MatrixRegions([], permutation)

    def build(node):
        if node is None:
            return

        rect = node.rect
        perm_region = perm_regions.get_region(rect)
        region = qt.get_region(rect)
        regions_flat = region.flat
        perm_region_flat_sorted = sorted(perm_region.flat, key=lambda k: matrix.flat[k])
        size = len(regions_flat)
        subregion_size = int(size / 4)
        perm_subregions = []

        for i in range(4):
            first = subregion_size * i
            last = first + subregion_size
            flat_subregion_perm = array(sorted(perm_region_flat_sorted[first:last]))
            subregion_shape = int(sqrt(subregion_size))
            subregion_perm = flat_subregion_perm.reshape((subregion_shape, subregion_shape))
            perm_subregions.append(subregion_perm)

        top = concatenate((perm_subregions[0], perm_subregions[1]), axis=1)
        bottom = concatenate((perm_subregions[2], perm_subregions[3]), axis=1)
        perm_region = concatenate((top, bottom), axis=0)
        perm_regions.set_region(rect, perm_region)

        for child in node.children:
            build(child)

    build(root)
    return permutation


def permutate(matrix, permutation):
    permutated = zeros(matrix.shape)
    for i in range(matrix.size):
        permutated.flat[i] = matrix.flat[permutation.flat[i]]
    return permutated


def reverse_permutation(permutated, permutation):
    matrix = zeros(permutated.shape)
    for i in range(permutated.size):
        matrix.flat[permutation.flat[i]] = permutated.flat[i]
    return matrix


def get_diff_fix(base_mx, new_mx, rects):
    base_regions = MatrixRegions(rects, base_mx)
    new_mx = MatrixRegions(rects, new_mx)
    return {
        i: np.setdiff1d(region_base, region_new, True)
        for i, region_base, region_new in zip(count(), base_regions, new_mx)
    }


def fix_diff(regions, fix):
    wrong_elements = [el for elements in fix.values() for el in elements]
    regions_base = [fix_region(region, wrong_elements, fix[i]) for i, region in enumerate(regions) if i in fix]
    mx_regions_base = MatrixRegions(regions.rects, np.copy(regions.matrix))
    for i in range(0, len(mx_regions_base)):
        mx_regions_base[i] = regions_base[i]
    return mx_regions_base


def fix_region(region, wrong, right):
    region_clear = np.setdiff1d(region.flat, wrong)
    region_fixed = np.append(region_clear, right)
    regions_flat = np.sort(region_fixed)
    return regions_flat.reshape(region.shape)
