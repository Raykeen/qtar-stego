import argparse
from copy import copy

from qtar.core.qtar import DEFAULT_PARAMS


def create_argpaser(with_images=True):
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    if with_images:
        argparser.add_argument('container', type=str,
                               help='container image')
        argparser.add_argument('watermark', type=str,
                               help='image to embed into container')

    argparser.add_argument('-t', '--homogeneity_threshold', metavar='threshold',
                           type=float, nargs='+', default=DEFAULT_PARAMS['homogeneity_threshold'],
                           help='homogeneity thresholds for different brightness levels   float[0, 1])')
    argparser.add_argument('-min', '--min_block_size', metavar='size',
                           type=int, default=DEFAULT_PARAMS['min_block_size'],
                           help='min block size   int[2, max_block_size], square of 2')
    argparser.add_argument('-max', '--max_block_size', metavar='size',
                           type=int, default=DEFAULT_PARAMS['max_block_size'],
                           help='max block size   int[min_block_size, image_size], square of 2')
    argparser.add_argument('-q', '--quant_power', metavar='power',
                           type=float, default=DEFAULT_PARAMS['quant_power'],
                           help='quantization power   float(0, 1]')
    argparser.add_argument('-s', '--ch_scale', metavar='scale',
                           type=float, default=DEFAULT_PARAMS['ch_scale'],
                           help='scale to ch_scale watermark pixels values before embedding   float(0, 255]')
    argparser.add_argument('-o', '--offset', metavar='offset',
                           type=int, nargs=2, default=DEFAULT_PARAMS['offset'],
                           help='offset container image')
    argparser.add_argument('-pm', '--pm_mode', action='store_true',
                           help='use permutation mode')
    argparser.add_argument('-cf', '--cf_mode', action='store_true',
                           help='use curve-fitting mode')
    argparser.add_argument('-cf_g', '--cf_grid_size', metavar='size',
                           type=int, default=DEFAULT_PARAMS['cf_grid_size'],
                           help='grid size to align curve fitting   int[1, min_block_size], square of 2')
    argparser.add_argument('-wmdct', '--wmdct_mode', action='store_true',
                           help='use watermark DCT mode')
    argparser.add_argument('-wmdct_b', '--wmdct_block_size', metavar='size',
                           type=int, default=DEFAULT_PARAMS['wmdct_block_size'],
                           help='watermark block size   int[1, wm_size], square of 2')
    argparser.add_argument('-wmdct_s', '--wmdct_scale', metavar='scale',
                           type=float, default=DEFAULT_PARAMS['wmdct_scale'],
                           help='scale secret image DCT coefficients before embedding, float(0, 1]')

    return argparser


def validate_params(params):
    valid_params = copy(DEFAULT_PARAMS)
    valid_params.update(params)
    return valid_params



