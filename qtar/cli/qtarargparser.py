import argparse
from copy import copy

from qtar.core.qtar import DEFAULT_PARAMS


def get_qtar_argpaser(with_images=True):
    argparser = argparse.ArgumentParser(add_help=False)

    if with_images:
        argparser.add_argument('container', type=str,
                               help='stego-container image')
        argparser.add_argument('secret-image', type=str,
                               help='secret image to embed into container')

    argparser.add_argument('-t', '--threshold', dest='homogeneity_threshold', metavar='threshold',
                           type=float, nargs='+', default=DEFAULT_PARAMS['homogeneity_threshold'],
                           help='homogeneity thresholds for different brightness levels   float[0, 1])')
    argparser.add_argument('-b', '--min-block', dest='min_block_size', metavar='min_b',
                           type=int, default=DEFAULT_PARAMS['min_block_size'],
                           help='min block size   int[2, maxblock], square of 2')
    argparser.add_argument('-B', '--max-block', dest='max_block_size', metavar='max_b',
                           type=int, default=DEFAULT_PARAMS['max_block_size'],
                           help='max block size   int[minblock, image size], square of 2')
    argparser.add_argument('-q', '--quantization', dest='quant_power', metavar='q',
                           type=float, default=DEFAULT_PARAMS['quant_power'],
                           help='quantization power   float(0, 1]')
    argparser.add_argument('-s', '--scale', dest='ch_scale', metavar='k',
                           type=float, default=DEFAULT_PARAMS['ch_scale'],
                           help='scale secret image pixels values before embedding   float(0, 255]')
    argparser.add_argument('-o', '--offset', metavar=('x', 'y'),
                           type=int, nargs=2, default=DEFAULT_PARAMS['offset'],
                           help='offset container image')
    argparser.add_argument('-p', '--pm', dest='pm_mode', action='store_true',
                           help='use permutation mode')
    argparser.add_argument('-c', '--cf', dest='cf_mode', action='store_true',
                           help='use curve-fitting mode')
    argparser.add_argument('-g', '--cf-grid', dest='cf_grid_size', metavar='cf',
                           type=int, default=DEFAULT_PARAMS['cf_grid_size'],
                           help='grid size to align curve fitting   int[1, minblock]')
    argparser.add_argument('-d', '--sidct', dest='wmdct_mode', action='store_true',
                           help='use DCT on secret image - SIDCT mode')
    argparser.add_argument('--si-b', dest='wmdct_block_size', metavar='v',
                           type=int, default=DEFAULT_PARAMS['wmdct_block_size'],
                           help='seret image block size   int[1, si size], square of 2')
    argparser.add_argument('--si-s', dest='wmdct_scale', metavar='sk',
                           type=float, default=DEFAULT_PARAMS['wmdct_scale'],
                           help='scale secret image DCT coefficients before embedding, float(0, 1]')

    return argparser


def validate_params(params):
    valid_params = copy(DEFAULT_PARAMS)
    valid_params.update(params)
    return valid_params



