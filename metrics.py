import numpy as np
from math import sqrt, log10


def psnr(array1, array2, max=255):
    flat_arr1 = np.array(array1).flatten()
    flat_arr2 = np.array(array2).flatten()
    len1 = len(flat_arr1)
    len2 = len(flat_arr2)

    if len1 != len2:
        raise Exception('Arrays must have the same size')

    MSE = 0

    for i in range(len1):
        MSE += (int(flat_arr1[i]) - int(flat_arr2[i])) ** 2

    MSE = sqrt(float(MSE) / float(len1))

    if MSE == 0:
        return float('inf')
    else:
        PSNR = 20 * log10(float(max) / float(MSE))
        return(PSNR)
