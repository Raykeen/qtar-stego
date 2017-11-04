import numpy as np
from math import sqrt, log10
from skimage.measure import compare_ssim, compare_psnr


def psnr(img1, img2):
    return compare_psnr(np.array(img1), np.array(img2))


def ssim(img1, img2):
    np_img1 = np.array(img1)
    np_img2 = np.array(img2)

    if len(np_img1.shape) == 3:
        multichannel = True
    else:
        multichannel = False

    return compare_ssim(np_img1, np_img2, multichannel=multichannel)


def bcr(array1, array2):
    flat_arr1 = np.array(array1).flatten()
    flat_arr2 = np.array(array2).flatten()
    len1 = len(flat_arr1)
    len2 = len(flat_arr2)

    if len1 != len2:
        raise Exception('Arrays must have the same size')

    errors = 0

    for i in range(len1):
        errors += bin(int(flat_arr1[i]) ^ int(flat_arr2[i])).count("1")

    bcr = 1 - (errors / (8 * len1))
    return bcr

