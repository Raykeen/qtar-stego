import argparse
import math
from copy import copy

from qtar.core.qtar import DEFAULT_PARAMS


def get_qtar_argpaser(with_images=True):
    argparser = argparse.ArgumentParser(add_help=False,
                                        formatter_class=argparse.RawTextHelpFormatter)

    if with_images:
        argparser.add_argument('container',
                               type=str,
                               help='stego-container image')

        argparser.add_argument('secret-image',
                               dest='watermark',
                               type=str,
                               help='secret image to embed into container')

    argparser.add_argument('-t', '--th',
                           dest='homogeneity_threshold',
                           metavar='THRESHOLD',
                           type=float,
                           nargs='+',
                           default=DEFAULT_PARAMS['homogeneity_threshold'],
                           help='A sequence of homogeneity thresholds (th) \n'
                                'for different brightness levels, \n'
                                'real, 0 <= th <= 1.')

    argparser.add_argument('-b', '--min-b',
                           dest='min_block_size',
                           metavar='MIN_BLOCK_SIZE',
                           type=int,
                           default=DEFAULT_PARAMS['min_block_size'],
                           help='Min quad-tree block size (min_b), \n'
                                'integer, 2 <= min_b <= max_b, \n'
                                'power of 2.')

    argparser.add_argument('-B', '--max-b',
                           dest='max_block_size',
                           metavar='MAX_BLOCK_SIZE',
                           type=int,
                           default=DEFAULT_PARAMS['max_block_size'],
                           help='Max quad-tree block size (max_b), \n'
                                'integer, min_b <= max_b <= container size,\n '
                                'power of 2.')

    argparser.add_argument('-q', '--quantization',
                           dest='quant_power',
                           metavar='QUANTIZATION_POWER',
                           type=float,
                           default=DEFAULT_PARAMS['quant_power'],
                           help='Quantization power (q), \n'
                                'real, 0 < q <= 1.')

    argparser.add_argument('-s', '--scale',
                           dest='ch_scale',
                           metavar='SCALE_FACTOR',
                           type=float,
                           default=DEFAULT_PARAMS['ch_scale'],
                           help='Scale factor for secret image pixels values (k), \n'
                                'real, 0 < k <= 20')

    argparser.add_argument('-o', '--offset',
                           metavar=('X', 'Y'),
                           type=int, nargs=2,
                           default=DEFAULT_PARAMS['offset'],
                           help='Apply offset transform to container, \n'
                                'integers, 0 <= x <= secret-image size, \n'
                                '0 <= y <= secret-image size.')

    argparser.add_argument('-p', '--pm',
                           dest='pm_mode',
                           action='store_true',
                           help='Use permutation mode.')

    argparser.add_argument('-c', '--cf',
                           dest='cf_mode',
                           action='store_true',
                           help='Use curve-fitting mode.')

    argparser.add_argument('-g', '--cf-g',
                           dest='cf_grid_size',
                           metavar='CF_GRID_SIZE',
                           type=int,
                           default=DEFAULT_PARAMS['cf_grid_size'],
                           help='Grid size to align curve fitting (cf), \n'
                                'integer, 1 <= cf <= min_b.')

    argparser.add_argument('-d', '--sidct',
                           dest='wmdct_mode',
                           action='store_true',
                           help='SIDCT mode - use DCT on secret image.')

    argparser.add_argument('--si-b',
                           dest='wmdct_block_size',
                           metavar='SI_DCT_BLOCK_SIZE',
                           type=int,
                           default=DEFAULT_PARAMS['wmdct_block_size'],
                           help='Secret image DCT block size (v), \n'
                                'integer, 1 <= v <= secret-image size.')

    argparser.add_argument('--si-s',
                           dest='wmdct_scale',
                           metavar='SI_DCT_SCALE_FACTOR',
                           type=float,
                           default=DEFAULT_PARAMS['wmdct_scale'],
                           help='Scale factor for secret image DCT coefficients (sk), \n'
                                'real, 0 < sk <= 1.')

    return argparser


def validate_params(given_params):
    params = copy(DEFAULT_PARAMS)
    params.update(given_params)

    th = params['homogeneity_threshold']
    min_b = params['min_block_size']
    max_b = params['max_block_size']
    q = params['quant_power']
    s = params['ch_scale']
    cf_g = params['cf_grid_size']
    wmdct_b = params['wmdct_block_size']
    wmdct_s = params['wmdct_scale']

    if isinstance(th, (tuple, list)) and not all(0 <= t <= 1 for t in th) \
            or isinstance(th, (float, int)) and not 0 <= th <= 1:
        raise WrongQTARParamError('Wrong argument: threshold (th) must be real in range 0 <= th <= 1.')

    if not (8 <= min_b <= max_b and is_power_of(min_b, 2)):
        raise WrongQTARParamError('Wrong argument: min block size (min_b) must be integer in range '
                                  '8 <= min_b <= max_b and power of 2.')

    if not (min_b <= max_b and is_power_of(max_b, 2)):
        raise WrongQTARParamError('Wrong argument: max block size (max_b) must be integer in range '
                                  'min_b <= max_b <= container_size and power of 2.')

    if not 0 < q <= 1:
        raise WrongQTARParamError('Wrong argument: quantization power (q) must be real in range 0 < q <= 1.')

    if not 0 < s <= 20:
        raise WrongQTARParamError('Wrong argument: scale factor (k) must be real in range 0 < k <= 20.')

    if not 1 <= cf_g <= min_b:
        raise WrongQTARParamError('Wrong argument: curve-fitting grid (cf) must be integer in range 1 <= cf <= min_b.')

    if not 1 <= wmdct_b:
        raise WrongQTARParamError('Wrong argument: secret image DCT block size (v) must be integer in range '
                                  '1 <= v <= secret-image size.')

    if not 0 < wmdct_s <= 1:
        raise WrongQTARParamError('Wrong argument: scale factor for secret image DCT coefficients (sk) '
                                  'must be real in range 0 < sk <= 1.')

    return params


def is_power_of(value, base):
    power = int(math.log(value, base))
    return value == base**power


class WrongQTARParamError(Exception):
    pass
