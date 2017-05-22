import numpy as np
from itertools import count

from qtar.core.matrixregion import MatrixRegions


def permutate(matrix, permutation):
    return matrix.flat[permutation.flatten()].reshape(matrix.shape)


def reverse_permutation(permutated, permutation):
    matrix = np.zeros(permutated.shape)
    matrix.flat[permutation.flatten()] = permutated.flat
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
