from math import sqrt
from os import listdir
from re import match

import matplotlib.pyplot as plt
import numpy as np


def read_log(log):
    log.readline()
    arrays = ([], [], [], [], [])
    zero_values = (0, 0, 0, 0, 0)
    for line in log:
        values = [float(val) for val in line.split(' ')]
        for i in range(len(values)):
            arrays[i].append(values[i])

        x, y, psnr, bcr, bpp = values
        if x == 0 and y == 0:
            zero_values = values

    return arrays, zero_values


def bpp_psnr_plot(bpp, psnr, bpp0, psnr0):
    plt.figure()
    plt.scatter(bpp, psnr, s=4, color='black')
    plt.scatter(bpp0, psnr0, s=8, color='red')
    plt.xlabel("BPP")
    plt.ylabel("PSNR")
    plt.text(bpp0 + 0.01, psnr0, '(0, 0)', fontsize=14, bbox=dict(edgecolor='r', facecolor='w'))
    plt.grid(True)
    return plt


def map_plot(x, name):
    plt.figure()
    size = int(sqrt(len(x)))
    x2d = np.array(x).reshape((size, size))
    plt.xlabel("x (px)")
    plt.ylabel("y (px)")
    plt.imshow(x2d)
    plt.colorbar(label=name)
    return plt


def main():
    logs = listdir('logs')
    enum_logs = [log for log in logs if match("enum_[_.\w]*.log", log)]
    for log in enum_logs:
        name = match("enum_(.*).log", log).groups()[0]
        log_file = open('logs\\' + log)
        arrays, zero_values = read_log(log_file)

        x, y, psnr, bcr, bpp = arrays
        x0, y0, psnr0, bcr0, bpp0 = zero_values

        bpp_psnr_plot(bpp, psnr, bpp0, psnr0).savefig('plots\\bpp_psnr_'+name+'.png')
        map_plot(psnr, "PSNR").savefig('plots\\psnr_map_'+name+'.png')
        map_plot(bpp, "BPP").savefig('plots\\bpp_map_'+name+'.png')


if __name__ == "__main__":
    main()

