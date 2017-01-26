from itertools import product
from math import sqrt, cos, pi

from numpy import array, zeros, arange, exp


def dct2d(mx):
    mx = array(mx)
    h, w = mx.shape
    dct = zeros((h, w))

    dct_coords = product(range(0, h), range(0, w))
    for v, u in dct_coords:
        sum = 0
        mx_coords = product(range(0, h), range(0, w))
        for y, x in mx_coords:
            sum += mx[y, x] * (cos(pi * u * (2 * x + 1) / (2 * w)) * cos(pi * v * (2 * y + 1) / (2 * h)))
        F = 2/h * c(u) * c(v) * sum
        dct[v, u] = F

    return dct


def idct2d(dct):
    dct = array(dct)
    h, w = dct.shape
    mx = zeros((h, w))

    mx_coords = product(range(0, h), range(0, w))
    for y, x in mx_coords:
        sum = 0
        dct_coords = product(range(0, h), range(0, w))
        for v, u in dct_coords:
            sum += c(u) * c(v) * dct[v, u] * (cos(pi * u * (2 * x + 1) / (2 * w)) * cos(pi * v * (2 * y + 1) / (2 * h)))
        f = 2/h * sum
        mx[y, x] = f

    return mx

def c(u):
    if u == 0:
        return 1/sqrt(2)
    else:
        return 1


from numpy.random import rand
from scipy.fftpack import dct, idct
#from numpy.fft.fftpack import ifft, fft
from accelerate.mkl.fftpack import ifft, fft
from time import time


def fftdct(x, inv=False):
    if len(x.shape) == 2:
        return _fftdctmx(x, inv)
    elif len(x.shape) == 1:
        N = len(x)
        k = arange(N)
        y = zeros(2 * N)
        y[:N] = x

        if inv:
            Y = ifft(y)[:N]
        else:
            Y = fft(y)[:N]

        Y *= 2 * exp(-1j * pi * k / (2 * N))
        Y = Y.real
        Y[0] /= sqrt(2)
        return Y.real


def _fftdctmx(x, inv):
    w, h = x.shape
    result = zeros(x.shape)
    for i in range(h):
        result[i] = fftdct(x[i], inv)
    return result



im = (rand(128,128) * 255).astype(int)
print("IMAGE:")
print(im)

print("MY DCT:")
# d = dct2d(im)
# print(d.astype(int))

print("MY IDCT:")
# id = idct2d(d)
# print(id.astype(int))
# print(bcr(im,id))

dct_time = time()
print("SCIPY DCT:")
d2 = dct(dct(im, norm='ortho').T, norm='ortho').T
print(d2.astype(int))
#print(bcr(d,d2))
print('{0} sec'.format(time() - dct_time))

print("SCIPY IDCT:")
id2 = idct(idct(d2.T, norm='ortho').T, norm='ortho')
print(id2.astype(int))
#print(bcr(id,id2))
#print(bcr(im,id2))

fft_time = time()
print("\nNUMPY FFT2:")
ff = fftdct(fftdct(im).T).T
print(ff.astype(int))
print('{0} sec'.format(time() - fft_time))

print("\nNUMPY IFFT2:")
print(fftdct(fftdct(ff, True).T, True).T.astype(int))
