import argparse
from qtar.core.qtar import QtarStego, DEFAULT_PARAMS

argparser = argparse.ArgumentParser()
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
